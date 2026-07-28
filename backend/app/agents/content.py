import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.content_schema import (
    PresentationContent, SlideContent, ContentStyle, ContentQuality
)
from app.agents.prompts.content_prompts import (
    CONTENT_SYSTEM_PROMPT, SLIDE_TITLE_PROMPT, BULLET_POINTS_PROMPT,
    EXPLANATION_PROMPT, EXAMPLES_PROMPT, SPEAKER_NOTES_PROMPT,
    CONTENT_QUALITY_PROMPT
)

logger = logging.getLogger(__name__)

class ContentAgent(BaseAgent):
    '''Enhanced Content Agent for slide generation'''
    
    def __init__(self, llm_service):
        super().__init__("Content", llm_service)
        self.max_slides = 20
        self.min_slides = 3
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Generating slide content...")
        
        try:
            # Get outline and research
            outline = state.outline
            research = state.research
            
            # Determine content style
            style = self._determine_style(outline)
            audience = outline.get("audience", "general")
            tone = outline.get("tone", "professional")
            
            # Generate content for each slide
            slides_content = []
            slide_templates = outline.get("slides", [])
            
            for slide_template in slide_templates:
                slide_content = await self._generate_slide_content(
                    template=slide_template,
                    topic=state.topic,
                    research=research,
                    audience=audience,
                    tone=tone,
                    style=style
                )
                slides_content.append(slide_content)
            
            # Create presentation content
            presentation_content = PresentationContent(
                title=outline.get("title", f"Presentation on {state.topic}"),
                topic=state.topic,
                slides=slides_content,
                total_slides=len(slides_content),
                style=style,
                audience=audience,
                tone=tone
            )
            
            # Save to state
            state.content = presentation_content.to_dict()
            state.slides = [s.to_dict() for s in slides_content]
            state.progress = 60
            
            # Save to file
            await self._save_content(presentation_content)
            
            await self._log_step(
                state,
                f"Generated content for {len(slides_content)} slides"
            )
            
        except Exception as e:
            await self._add_error(state, f"Content error: {str(e)}")
            logger.error(f"Content error details: {e}", exc_info=True)
        
        return state
    
    def _determine_style(self, outline: Dict[str, Any]) -> ContentStyle:
        '''Determine the content style based on audience and tone'''
        audience = outline.get("audience", "general")
        tone = outline.get("tone", "professional")
        
        if audience == "beginner":
            return ContentStyle.EDUCATIONAL
        elif audience == "expert":
            return ContentStyle.DETAILED
        elif tone == "persuasive":
            return ContentStyle.PERSUASIVE
        elif tone == "professional":
            return ContentStyle.PROFESSIONAL
        else:
            return ContentStyle.EDUCATIONAL
    
    async def _generate_slide_content(
        self,
        template: Dict[str, Any],
        topic: str,
        research: Dict[str, Any],
        audience: str,
        tone: str,
        style: ContentStyle
    ) -> SlideContent:
        '''Generate content for a single slide'''
        
        number = template.get("number", 0)
        title = template.get("title", f"Slide {number}")
        purpose = template.get("purpose", "")
        
        # Generate content components
        bullet_points = await self._generate_bullet_points(
            topic=topic,
            title=title,
            purpose=purpose,
            audience=audience
        )
        
        explanation = await self._generate_explanation(
            topic=topic,
            title=title,
            bullet_points=bullet_points,
            audience=audience
        )
        
        examples = await self._generate_examples(
            topic=topic,
            title=title,
            explanation=explanation,
            audience=audience
        )
        
        content_text = self._generate_content_text(
            title=title,
            explanation=explanation,
            bullet_points=bullet_points
        )
        
        speaker_notes = await self._generate_speaker_notes(
            topic=topic,
            title=title,
            content=content_text,
            audience=audience
        )
        
        # Determine key takeaways
        key_takeaways = bullet_points[:3] if bullet_points else []
        
        return SlideContent(
            number=number,
            title=title,
            content=content_text,
            bullet_points=bullet_points,
            explanation=explanation,
            examples=examples,
            speaker_notes=speaker_notes,
            style=style,
            quality_score=0.8,
            key_takeaways=key_takeaways
        )
    
    async def _generate_bullet_points(
        self,
        topic: str,
        title: str,
        purpose: str,
        audience: str
    ) -> List[str]:
        '''Generate bullet points for a slide'''
        try:
            prompt = BULLET_POINTS_PROMPT.format(
                topic=topic,
                content=title,
                audience=audience
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are an expert at creating concise bullet points.",
                temperature=0.3,
                max_tokens=512
            )
            
            points = self._parse_json(response.text)
            if isinstance(points, list):
                return points[:5]  # Limit to 5 bullet points
            else:
                return [
                    f"Key concept about {topic}",
                    f"Important aspect of {title}",
                    f"Practical application of {topic}"
                ]
        except Exception as e:
            logger.warning(f"Bullet points generation failed: {e}")
            return [f"Key point about {title}", f"Important concept in {topic}"]
    
    async def _generate_explanation(
        self,
        topic: str,
        title: str,
        bullet_points: List[str],
        audience: str
    ) -> str:
        '''Generate detailed explanation'''
        try:
            concept = bullet_points[0] if bullet_points else title
            
            prompt = EXPLANATION_PROMPT.format(
                topic=topic,
                concept=concept,
                audience=audience
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are an expert at explaining complex concepts clearly.",
                temperature=0.4,
                max_tokens=512
            )
            
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Explanation generation failed: {e}")
            return f"{title} is an important concept in {topic}."
    
    async def _generate_examples(
        self,
        topic: str,
        title: str,
        explanation: str,
        audience: str
    ) -> List[str]:
        '''Generate examples for a slide'''
        try:
            prompt = EXAMPLES_PROMPT.format(
                topic=topic,
                concept=title,
                audience=audience
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are an expert at creating relevant examples.",
                temperature=0.4,
                max_tokens=512
            )
            
            examples = self._parse_json(response.text)
            if isinstance(examples, list):
                return examples[:3]
            else:
                return [f"Real-world example of {title}", f"Practical application of {topic}"]
        except Exception as e:
            logger.warning(f"Examples generation failed: {e}")
            return [f"Example of {title}", f"Application in {topic}"]
    
    async def _generate_speaker_notes(
        self,
        topic: str,
        title: str,
        content: str,
        audience: str
    ) -> str:
        '''Generate speaker notes for a slide'''
        try:
            prompt = SPEAKER_NOTES_PROMPT.format(
                topic=topic,
                title=title,
                content=content,
                audience=audience
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are an expert at creating engaging speaker notes.",
                temperature=0.4,
                max_tokens=512
            )
            
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Speaker notes generation failed: {e}")
            return f"Welcome to this slide about {title}. Let's explore the key concepts."
    
    def _generate_content_text(
        self,
        title: str,
        explanation: str,
        bullet_points: List[str]
    ) -> str:
        '''Generate combined content text'''
        content = explanation
        
        if bullet_points:
            content += "\n\nKey points:\n" + "\n".join([f"- {p}" for p in bullet_points])
        
        return content
    
    async def _save_content(self, content: PresentationContent):
        '''Save content to file'''
        try:
            # Create directory
            os.makedirs("./generated/content", exist_ok=True)
            
            # Save as JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            json_path = f"./generated/content/slides_{timestamp}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                f.write(content.to_json())
            
            # Save as Markdown
            md_path = f"./generated/content/slides_{timestamp}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content.to_markdown())
            
            logger.info(f"Content saved to: {json_path} and {md_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save content: {e}")
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        '''Parse JSON from LLM response'''
        try:
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return {}
