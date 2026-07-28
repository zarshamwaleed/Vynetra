import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.outline_schema import (
    PresentationOutline, SlideOutline, SlideType, AudienceLevel, PresentationTone
)
from app.agents.prompts.planner_prompts import (
    PLANNER_SYSTEM_PROMPT, OUTLINE_ANALYSIS_PROMPT, LEARNING_FLOW_PROMPT
)

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    '''Enhanced Planner Agent with sophisticated outline generation'''
    
    def __init__(self, llm_service):
        super().__init__("Planner", llm_service)
        self.max_slides = 15
        self.min_slides = 5
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Creating detailed presentation outline...")
        
        try:
            # Step 1: Analyze the prompt
            analysis = await self._analyze_prompt(state.prompt)
            
            # Step 2: Determine audience and tone
            audience = self._determine_audience(analysis)
            tone = self._determine_tone(analysis)
            
            # Step 3: Generate the outline
            outline_data = await self._generate_outline(
                prompt=state.prompt,
                topic=analysis.get("topic", state.prompt[:50]),
                audience=audience,
                tone=tone,
                slide_count=analysis.get("slide_count", 10)
            )
            
            # Step 4: Create structured outline
            outline = self._create_outline_object(outline_data, audience, tone)
            
            # Step 5: Generate learning flow
            learning_flow = await self._generate_learning_flow(outline)
            outline.learning_flow = learning_flow
            
            # Step 6: Update state
            state.topic = outline.topic
            state.outline = outline.to_dict()
            state.slide_count = outline.total_slides
            state.progress = 25
            
            await self._log_step(
                state, 
                f"Created outline with {outline.total_slides} slides, "
                f"estimated duration: {outline.estimated_duration} minutes"
            )
            
        except Exception as e:
            await self._add_error(state, f"Planner error: {str(e)}")
            logger.error(f"Planner error details: {e}", exc_info=True)
        
        return state
    
    async def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        '''Analyze the prompt to extract key information'''
        try:
            system_prompt = '''You are a presentation analyst. Analyze the user's request and provide insights.
            Return ONLY valid JSON with:
            {
                "topic": "Main topic",
                "audience": "beginner|intermediate|expert|mixed",
                "complexity": 1-5,
                "slide_count": 8-15,
                "key_areas": ["area1", "area2"],
                "challenges": ["challenge1"],
                "tone": "professional|educational|casual|persuasive|inspirational"
            }'''
            
            response = await self.llm.generate(
                prompt=f"Analyze this request: {prompt}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1024
            )
            
            return self._parse_json(response.text)
        except Exception as e:
            logger.warning(f"Prompt analysis failed, using defaults: {e}")
            return {
                "topic": prompt[:50],
                "audience": "mixed",
                "complexity": 3,
                "slide_count": 10,
                "key_areas": [],
                "challenges": [],
                "tone": "educational"
            }
    
    def _determine_audience(self, analysis: Dict[str, Any]) -> AudienceLevel:
        '''Determine the target audience'''
        audience_str = analysis.get("audience", "mixed").lower()
        try:
            return AudienceLevel(audience_str)
        except ValueError:
            audience_map = {
                "beginner": AudienceLevel.BEGINNER,
                "intermediate": AudienceLevel.INTERMEDIATE,
                "expert": AudienceLevel.EXPERT,
                "mixed": AudienceLevel.MIXED
            }
            return audience_map.get(audience_str, AudienceLevel.MIXED)
    
    def _determine_tone(self, analysis: Dict[str, Any]) -> PresentationTone:
        '''Determine the presentation tone'''
        tone_str = analysis.get("tone", "educational").lower()
        try:
            return PresentationTone(tone_str)
        except ValueError:
            tone_map = {
                "professional": PresentationTone.PROFESSIONAL,
                "educational": PresentationTone.EDUCATIONAL,
                "casual": PresentationTone.CASUAL,
                "persuasive": PresentationTone.PERSUASIVE,
                "inspirational": PresentationTone.INSPIRATIONAL
            }
            return tone_map.get(tone_str, PresentationTone.EDUCATIONAL)
    
    async def _generate_outline(
        self,
        prompt: str,
        topic: str,
        audience: AudienceLevel,
        tone: PresentationTone,
        slide_count: int
    ) -> Dict[str, Any]:
        '''Generate the presentation outline using LLM'''
        try:
            system_prompt = PLANNER_SYSTEM_PROMPT
            
            user_prompt = f'''
            Create a presentation outline for:
            
            Topic: {topic}
            Audience: {audience.value}
            Tone: {tone.value}
            Number of slides: {slide_count}
            Original prompt: {prompt}
            
            Return ONLY valid JSON with the structure specified.
            Make sure the outline is logical, engaging, and appropriate for the audience.
            '''
            
            response = await self.llm.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.4,
                max_tokens=4096
            )
            
            return self._parse_json(response.text)
            
        except Exception as e:
            logger.error(f"Outline generation failed: {e}")
            return self._create_fallback_outline(topic, slide_count)
    
    def _create_outline_object(
        self,
        data: Dict[str, Any],
        audience: AudienceLevel,
        tone: PresentationTone
    ) -> PresentationOutline:
        '''Create a PresentationOutline object from the LLM response'''
        slides = []
        for slide_data in data.get("slides", []):
            slide_type = slide_data.get("type", "content")
            try:
                slide_type_enum = SlideType(slide_type)
            except ValueError:
                slide_type_enum = SlideType.CONTENT
            
            slide = SlideOutline(
                number=slide_data.get("number", len(slides) + 1),
                title=slide_data.get("title", f"Slide {len(slides) + 1}"),
                slide_type=slide_type_enum,
                purpose=slide_data.get("purpose", ""),
                key_points=slide_data.get("key_points", []),
                estimated_duration=slide_data.get("estimated_duration", 60),
                notes=slide_data.get("notes", ""),
                prerequisites=slide_data.get("prerequisites", []),
                learning_objectives=slide_data.get("learning_objectives", [])
            )
            slides.append(slide)
        
        if not slides:
            slides = self._create_fallback_slides(data.get("topic", "Presentation"), 5)
        
        total_duration = sum(s.estimated_duration for s in slides) // 60
        
        return PresentationOutline(
            title=data.get("title", f"Presentation on {data.get('topic', '')}"),
            topic=data.get("topic", ""),
            audience=audience,
            tone=tone,
            total_slides=len(slides),
            estimated_duration=max(total_duration, 5),
            slides=slides,
            learning_flow=data.get("learning_flow", ""),
            prerequisites=data.get("prerequisites", []),
            key_takeaways=data.get("key_takeaways", []),
            references=data.get("references", []),
            created_at=datetime.now().isoformat()
        )
    
    async def _generate_learning_flow(self, outline: PresentationOutline) -> str:
        '''Generate a learning flow description'''
        try:
            slides_summary = "\n".join([
                f"Slide {s.number}: {s.title} ({s.slide_type.value}) - {s.purpose}"
                for s in outline.slides[:10]
            ])
            
            prompt = LEARNING_FLOW_PROMPT.format(slides=slides_summary)
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt="You are a learning experience designer.",
                temperature=0.3,
                max_tokens=512
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.warning(f"Learning flow generation failed: {e}")
            return "The presentation follows a logical flow from introduction to conclusion, building knowledge progressively."
    
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
    
    def _create_fallback_outline(self, topic: str, slide_count: int) -> Dict[str, Any]:
        '''Create a fallback outline if LLM fails'''
        slides = [
            {
                "number": i + 1,
                "title": f"Slide {i + 1}",
                "type": "content",
                "purpose": f"Cover aspect of {topic}",
                "key_points": [f"Key point {j + 1}" for j in range(2)],
                "estimated_duration": 60,
                "notes": "",
                "prerequisites": [],
                "learning_objectives": []
            }
            for i in range(min(slide_count, 10))
        ]
        
        return {
            "title": f"Presentation on {topic}",
            "topic": topic,
            "audience": "mixed",
            "tone": "educational",
            "total_slides": len(slides),
            "estimated_duration": len(slides) * 2,
            "slides": slides,
            "learning_flow": "This presentation covers the topic from introduction to conclusion.",
            "prerequisites": ["None"],
            "key_takeaways": [f"Key takeaway {i + 1}" for i in range(3)],
            "references": []
        }
    
    def _create_fallback_slides(self, topic: str, count: int) -> List[SlideOutline]:
        '''Create fallback slides'''
        slide_titles = [
            f"Introduction to {topic}",
            f"What is {topic}?",
            f"Key Concepts of {topic}",
            f"Applications of {topic}",
            f"Benefits of {topic}",
            f"Challenges in {topic}",
            f"Future of {topic}",
            f"Summary of {topic}",
            f"Q&A on {topic}",
            f"Conclusion: {topic}"
        ]
        
        slides = []
        for i in range(min(count, len(slide_titles))):
            slides.append(
                SlideOutline(
                    number=i + 1,
                    title=slide_titles[i],
                    slide_type=SlideType.CONTENT if i > 0 else SlideType.TITLE,
                    purpose=f"Cover {slide_titles[i]}",
                    key_points=[f"Key point about {topic}" for _ in range(2)],
                    estimated_duration=60
                )
            )
        return slides
