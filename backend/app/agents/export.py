import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.export_schema import (
    ExportDocument, ExportSlide, ExportFormat, PDFStyle
)
from app.agents.utils.pdf_builder import PDFBuilder

logger = logging.getLogger(__name__)

class ExportAgent(BaseAgent):
    '''Enhanced Export Agent for PDF and other formats'''
    
    def __init__(self, llm_service):
        super().__init__("Export", llm_service)
        self.pdf_builder = PDFBuilder()
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Exporting presentation...")
        
        try:
            # Get data from state
            slides_data = state.slides
            topic = state.topic or state.prompt[:50]
            title = state.outline.get("title", f"Presentation on {topic}")
            
            # Determine style
            style = self._determine_style(state.outline)
            
            # Create export slides
            export_slides = []
            for slide_data in slides_data:
                export_slide = ExportSlide(
                    number=slide_data.get('number', 0),
                    title=slide_data.get('title', 'Slide'),
                    content=slide_data.get('content', ''),
                    bullet_points=slide_data.get('bullet_points', []),
                    speaker_notes=slide_data.get('speaker_notes', ''),
                    images=[],
                    diagrams=[]
                )
                export_slides.append(export_slide)
            
            # Create export document
            export_doc = ExportDocument(
                title=title,
                topic=topic,
                slides=export_slides,
                total_slides=len(export_slides),
                style=style,
                formats=["pdf", "markdown"]
            )
            
            # Export formats
            export_paths = {}
            
            # Export PDF
            pdf_path = await self._export_pdf(title, export_slides, style)
            if pdf_path:
                export_paths["pdf"] = pdf_path
            
            # Export Markdown
            md_path = await self._export_markdown(title, export_slides)
            if md_path:
                export_paths["markdown"] = md_path
            
            # Export JSON
            json_path = await self._export_json(export_doc)
            if json_path:
                export_paths["json"] = json_path
            
            # Update state
            export_doc.output_path = pdf_path or md_path or json_path
            export_doc.status = "completed"
            state.export = export_doc.to_dict()
            state.export_paths = export_paths
            state.status = "completed"
            state.progress = 100
            
            await self._log_step(
                state,
                f"Exported to: {', '.join(export_paths.keys())}"
            )
            
        except Exception as e:
            await self._add_error(state, f"Export error: {str(e)}")
            logger.error(f"Export error details: {e}", exc_info=True)
        
        return state
    
    def _determine_style(self, outline: Dict[str, Any]) -> PDFStyle:
        tone = outline.get("tone", "professional")
        style_map = {
            "professional": PDFStyle.PROFESSIONAL,
            "educational": PDFStyle.MODERN,
            "casual": PDFStyle.CREATIVE,
            "persuasive": PDFStyle.PROFESSIONAL,
            "inspirational": PDFStyle.MODERN
        }
        return style_map.get(tone, PDFStyle.PROFESSIONAL)
    
    async def _export_pdf(
        self,
        title: str,
        slides: List[ExportSlide],
        style: PDFStyle
    ) -> Optional[str]:
        '''Export to PDF'''
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"presentation_{timestamp}.pdf"
            
            # Convert slides to dict
            slides_dict = [s.to_dict() for s in slides]
            
            # Create PDF
            output_path = self.pdf_builder.create_pdf(
                title=title,
                topic=slides_dict[0].get('topic', title) if slides_dict else title,
                slides=slides_dict,
                filename=filename,
                style=style.value
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"PDF export failed: {e}")
            return None
    
    async def _export_markdown(
        self,
        title: str,
        slides: List[ExportSlide]
    ) -> Optional[str]:
        '''Export to Markdown'''
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"presentation_{timestamp}.md"
            
            slides_dict = [s.to_dict() for s in slides]
            output_path = self.pdf_builder.create_markdown(
                title=title,
                slides=slides_dict,
                filename=filename
            )
            
            return output_path
            
        except Exception as e:
            logger.error(f"Markdown export failed: {e}")
            return None
    
    async def _export_json(self, export_doc: ExportDocument) -> Optional[str]:
        '''Export to JSON'''
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"presentation_{timestamp}.json"
            output_path = os.path.join("./generated/pdf", filename)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_doc.to_dict(), f, indent=2)
            
            logger.info(f"JSON saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"JSON export failed: {e}")
            return None
