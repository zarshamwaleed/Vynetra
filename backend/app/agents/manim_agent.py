import json
import logging
import os
import subprocess
import httpx
import tempfile
import glob
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.manim_schema import (
    ManimAnimation, ManimScene, ManimSceneType, AnimationQuality
)
from app.agents.prompts.manim_prompts import (
    MANIM_SYSTEM_PROMPT, SCENE_GENERATION_PROMPT, SCENE_EXTRACTION_PROMPT
)

logger = logging.getLogger(__name__)

class ManimAgent(BaseAgent):
    '''Manim Integration Agent for generating educational animations'''
    
    def __init__(self, llm_service, mcp_client=None):
        super().__init__("Manim", llm_service)
        self.mcp = mcp_client
        self.server_url = "http://localhost:8002"
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Generating educational animations...")
        
        try:
            # Extract content for animation
            content = self._extract_content(state)
            
            # Generate scene concepts - with fallback
            scene_concepts = await self._extract_scenes(content)
            
            # If no scenes extracted, create default scenes
            if not scene_concepts:
                logger.warning("No scenes extracted, using default scenes")
                scene_concepts = self._create_default_scenes(state.topic)
            
            # Generate Manim code for each scene
            scenes = []
            for concept in scene_concepts[:2]:
                scene = await self._generate_scene(
                    topic=state.topic,
                    concept=concept,
                    audience="beginner"
                )
                if scene:
                    scenes.append(scene)
            
            # Create animation
            animation = ManimAnimation(
                topic=state.topic,
                scenes=scenes,
                total_scenes=len(scenes),
                output_dir="./generated/animations"
            )
            
            # Render scenes
            for scene in scenes:
                video_path = await self._render_scene(scene)
                if video_path:
                    scene.video_path = video_path
                    scene.status = "completed"
            
            # Update state
            state.animations = animation.to_dict()
            state.progress = 85
            
            # Save to file
            await self._save_animation(animation)
            
            await self._log_step(
                state,
                f"Generated {len(scenes)} animation(s)"
            )
            
        except Exception as e:
            await self._add_error(state, f"Manim error: {str(e)}")
            logger.error(f"Manim error details: {e}", exc_info=True)
        
        return state
    
    def _extract_content(self, state: AgentState) -> str:
        '''Extract content for animation'''
        content = ""
        if state.slides:
            for slide in state.slides[:3]:
                if slide.get('content'):
                    content += slide['content'] + "\n"
                if slide.get('bullet_points'):
                    content += "\n".join(slide['bullet_points']) + "\n"
        if state.research:
            if isinstance(state.research, dict):
                content += state.research.get('summary', '') + "\n"
                content += "\n".join(state.research.get('key_concepts', [])) + "\n"
        return content[:1500]
    
    async def _extract_scenes(self, content: str) -> List[Dict[str, Any]]:
        '''Extract scene concepts from content with fallback'''
        try:
            prompt = SCENE_EXTRACTION_PROMPT.format(content=content[:1000])
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a Manim animation concept extractor. Return ONLY valid JSON.",
                temperature=0.3,
                max_tokens=1024
            )
            
            data = self._parse_json(response.text)
            scenes = data.get('scenes', [])
            
            # If no scenes, try to parse as direct array
            if not scenes and isinstance(data, list):
                scenes = data
            
            # If still no scenes, create default
            if not scenes:
                logger.warning("No scenes extracted, using defaults")
                scenes = [
                    {
                        "name": "Introduction",
                        "concept": "Main concept",
                        "description": "Visual explanation of the key concept"
                    }
                ]
            
            return scenes
            
        except Exception as e:
            logger.warning(f"Scene extraction failed: {e}")
            return self._create_default_scenes(content[:50])
    
    def _create_default_scenes(self, topic: str) -> List[Dict[str, Any]]:
        '''Create default scene concepts'''
        return [
            {
                "name": "Introduction",
                "concept": topic,
                "description": f"Visual introduction to {topic}"
            },
            {
                "name": "Key Concepts",
                "concept": f"Key concepts of {topic}",
                "description": f"Exploring the main concepts of {topic}"
            }
        ]
    
    async def _generate_scene(
        self,
        topic: str,
        concept: Dict[str, Any],
        audience: str
    ) -> Optional[ManimScene]:
        try:
            prompt = SCENE_GENERATION_PROMPT.format(
                topic=topic,
                concept=concept.get('concept', topic),
                description=concept.get('description', ''),
                audience=audience
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=MANIM_SYSTEM_PROMPT,
                temperature=0.4,
                max_tokens=2048
            )
            
            code = response.text
            
            # Clean up the code if it has markdown formatting
            code = self._clean_code(code)
            
            class_name = self._extract_class_name(code)
            
            # If no class name found, create a default
            if not class_name:
                class_name = "AnimationScene"
                code = self._create_default_code(topic, class_name)
            
            return ManimScene(
                name=concept.get('name', 'Animation'),
                class_name=class_name,
                code=code,
                scene_type=ManimSceneType.ANIMATION,
                description=concept.get('description', '')
            )
            
        except Exception as e:
            logger.warning(f"Scene generation failed: {e}")
            return None
    
    def _clean_code(self, code: str) -> str:
        '''Clean up code from markdown formatting'''
        # Remove markdown code blocks
        code = re.sub(r'`python\s*', '', code)
        code = re.sub(r'`\s*', '', code)
        return code.strip()
    
    def _create_default_code(self, topic: str, class_name: str) -> str:
        '''Create default Manim code'''
        return f'''
from manim import *

class {class_name}(Scene):
    def construct(self):
        title = Text("{topic}", color=WHITE)
        title.to_edge(UP)
        
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))
'''
    
    def _extract_class_name(self, code: str) -> str:
        match = re.search(r'class\s+(\w+)\s*\(', code)
        if match:
            return match.group(1)
        return None
    
    async def _render_scene(self, scene: ManimScene) -> Optional[str]:
        try:
            # Try MCP server first
            if self.mcp:
                try:
                    response = await self.mcp.call_tool(
                        "manim",
                        "generate_animation",
                        {
                            "code": scene.code,
                            "scene_name": scene.class_name
                        }
                    )
                    
                    if response.success:
                        video_files = response.result.get('video_files', [])
                        if video_files:
                            return video_files[0]
                except Exception as e:
                    logger.warning(f"MCP render failed: {e}")
            
            # Fallback: Direct manim command
            return await self._render_locally(scene)
            
        except Exception as e:
            logger.error(f"Scene rendering failed: {e}")
            return None
    
    async def _render_locally(self, scene: ManimScene) -> Optional[str]:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(scene.code)
                script_path = f.name
            
            try:
                result = subprocess.run(
                    ["manim", "-p", "-ql", script_path, scene.class_name],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    video_files = glob.glob("./media/videos/**/*.mp4", recursive=True)
                    if video_files:
                        return video_files[0]
            finally:
                try:
                    os.unlink(script_path)
                except:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"Local rendering failed: {e}")
            return None
    
    async def _save_animation(self, animation: ManimAnimation):
        try:
            os.makedirs("./generated/animations", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"./generated/animations/animation_{timestamp}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(animation.to_dict(), f, indent=2)
            
            for i, scene in enumerate(animation.scenes):
                code_path = f"./generated/animations/scene_{i+1}_{scene.class_name}.py"
                with open(code_path, 'w', encoding='utf-8') as f:
                    f.write(scene.code)
            
            logger.info(f"Animation saved to: {json_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save animation: {e}")
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        try:
            import re
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            # Try to parse as array
            array_match = re.search(r'\[.*\]', text, re.DOTALL)
            if array_match:
                return json.loads(array_match.group())
            return {}
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return {}
