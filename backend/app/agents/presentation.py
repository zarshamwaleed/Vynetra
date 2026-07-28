import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.presentation_schema import (
    PowerPointPresentation, PptSlide, SlideLayout, SlideTheme
)
from app.agents.utils.ppt_builder import PowerPointBuilder

logger = logging.getLogger(__name__)

class PresentationAgent(BaseAgent):
    '''Enhanced Presentation Agent for building PowerPoint presentations'''
    
    def __init__(self, llm_service):
        super().__init__("Presentation", llm_service)
        self.builder = PowerPointBuilder()
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Building PowerPoint presentation...")
        
        try:
            # Get data from state
            slides_data = state.slides
            topic = state.topic or state.prompt[:50]
            title = state.outline.get("title", f"Presentation on {topic}")
            theme = self._determine_theme(state.outline)
            
            # Create presentation
            presentation = PowerPointPresentation(
                title=title,
                topic=topic,
                theme=theme,
                slides=[]
            )
            
            # Build PowerPoint
            self.builder.create_presentation(title)
            
            # Add title slide
            self.builder.add_title_slide(title, f"Topic: {topic}")
            
            # Add content slides
            for slide_data in slides_data:
                ppt_slide = await self._create_slide(slide_data, state)
                presentation.slides.append(ppt_slide)
                
                # Add to PowerPoint
                self.builder.add_content_slide(
                    title=ppt_slide.title,
                    bullet_points=ppt_slide.bullet_points,
                    speaker_notes=ppt_slide.speaker_notes,
                    images=ppt_slide.images,
                    diagrams=ppt_slide.diagrams,
                    videos=ppt_slide.videos
                )
            
            # Add a thank you slide
            self.builder.add_content_slide(
                title="Thank You!",
                content="Questions?",
                bullet_points=[]
            )
            
            # Save presentation
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"presentation_{timestamp}"
            output_path = self.builder.save(filename)
            
            # Update state
            presentation.output_path = output_path
            presentation.total_slides = len(presentation.slides) + 2
            presentation.status = "completed"
            
            state.presentation = presentation.to_dict()
            state.presentation_path = output_path
            state.progress = 95
            state.status = "completed"
            
            await self._log_step(
                state,
                f"Presentation built: {output_path} with {presentation.total_slides} slides"
            )
            
        except Exception as e:
            await self._add_error(state, f"Presentation error: {str(e)}")
            logger.error(f"Presentation error details: {e}", exc_info=True)
        
        return state
    
    def _determine_theme(self, outline: Dict[str, Any]) -> SlideTheme:
        tone = outline.get("tone", "professional")
        theme_map = {
            "professional": SlideTheme.PROFESSIONAL,
            "educational": SlideTheme.MODERN,
            "casual": SlideTheme.CREATIVE,
            "persuasive": SlideTheme.PROFESSIONAL,
            "inspirational": SlideTheme.MODERN
        }
        return theme_map.get(tone, SlideTheme.MODERN)
    
    async def _create_slide(self, slide_data: Dict[str, Any], state: AgentState) -> PptSlide:
        layout = SlideLayout.CONTENT
        if slide_data.get('diagrams'):
            layout = SlideLayout.DIAGRAM
        elif slide_data.get('videos'):
            layout = SlideLayout.VIDEO
        elif slide_data.get('bullet_points'):
            layout = SlideLayout.TITLE_BULLET
        
        return PptSlide(
            number=slide_data.get('number', 0),
            layout=layout,
            title=slide_data.get('title', 'Slide'),
            content=slide_data.get('content', ''),
            bullet_points=slide_data.get('bullet_points', []),
            speaker_notes=slide_data.get('speaker_notes', ''),
            images=[],
            diagrams=self._find_diagrams(slide_data, state),
            videos=self._find_videos(slide_data, state)
        )
    
    def _find_diagrams(self, slide_data: Dict[str, Any], state: AgentState) -> List[str]:
        diagrams = []
        if state.diagrams:
            for diagram in state.diagrams:
                if slide_data.get('title', '').lower() in diagram.get('title', '').lower():
                    diagrams.append(f"./generated/diagrams/{diagram.get('title', 'diagram')}.png")
                elif len(diagrams) < 1:
                    diagrams.append("./generated/diagrams/diagram_placeholder.png")
        return diagrams[:1]
    
    def _find_videos(self, slide_data: Dict[str, Any], state: AgentState) -> List[str]:
        videos = []
        # Check if animations exists and has scenes
        if hasattr(state, 'animations') and state.animations:
            for scene in state.animations.get('scenes', []):
                if scene.get('video_path'):
                    videos.append(scene.get('video_path'))
                    break
        return videos[:1]
