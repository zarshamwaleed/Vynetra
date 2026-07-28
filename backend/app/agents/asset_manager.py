import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.utils.asset_utils import AssetManager
from app.agents.schemas.asset_schema import AssetType, AssetStatus

logger = logging.getLogger(__name__)

class AssetManagerAgent(BaseAgent):
    '''Asset Manager Agent for organizing and tracking generated assets'''
    
    def __init__(self, llm_service):
        super().__init__("AssetManager", llm_service)
        self.asset_manager = AssetManager()
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Managing assets...")
        
        try:
            # Register assets from state
            await self._register_assets(state)
            
            # Get summary
            summary = self.asset_manager.get_summary()
            
            # Export manifest
            manifest_path = self.asset_manager.export_manifest()
            
            # Clean up temporary files
            cleaned = self.asset_manager.cleanup_temp()
            
            # Update state
            state.asset_summary = summary
            state.asset_manifest = manifest_path
            state.progress = 100
            
            await self._log_step(
                state,
                f"Managed {summary['total_count']} assets "
                f"({summary['total_size_readable']}), cleaned {cleaned} temp files"
            )
            
        except Exception as e:
            await self._add_error(state, f"Asset manager error: {str(e)}")
            logger.error(f"Asset manager error details: {e}", exc_info=True)
        
        return state
    
    async def _register_assets(self, state: AgentState):
        '''Register all assets from the state'''
        
        # Register presentation
        if state.presentation_path and os.path.exists(state.presentation_path):
            self.asset_manager.add_asset(
                state.presentation_path,
                asset_type=AssetType.PPT,
                metadata={"presentation": True}
            )
        
        # Register PDF
        if state.export_paths:
            for format_type, path in state.export_paths.items():
                if os.path.exists(path):
                    asset_type = AssetType.PDF if format_type == "pdf" else AssetType.JSON
                    self.asset_manager.add_asset(
                        path,
                        asset_type=asset_type,
                        metadata={"export_format": format_type}
                    )
        
        # Register animations
        if state.animations:
            for scene in state.animations.get('scenes', []):
                video_path = scene.get('video_path')
                if video_path and os.path.exists(video_path):
                    self.asset_manager.add_asset(
                        video_path,
                        asset_type=AssetType.VIDEO,
                        metadata={"scene": scene.get('name', 'unknown')}
                    )
        
        # Register diagrams
        if state.diagrams:
            for diagram in state.diagrams:
                if isinstance(diagram, dict):
                    diagram_path = diagram.get('path')
                    if diagram_path and os.path.exists(diagram_path):
                        self.asset_manager.add_asset(
                            diagram_path,
                            asset_type=AssetType.DIAGRAM,
                            metadata={"diagram_type": diagram.get('type', 'unknown')}
                        )
        
        # Register research
        if state.research:
            research_path = "./generated/research/research.md"
            if os.path.exists(research_path):
                self.asset_manager.add_asset(
                    research_path,
                    asset_type=AssetType.REFERENCES,
                    metadata={"research": True}
                )
        
        # Register content
        if state.content:
            content_path = "./generated/content/slides.json"
            if os.path.exists(content_path):
                self.asset_manager.add_asset(
                    content_path,
                    asset_type=AssetType.JSON,
                    metadata={"content": True}
                )
    
    def get_asset_summary(self) -> Dict[str, Any]:
        '''Get a summary of all assets'''
        return self.asset_manager.get_summary()
    
    def get_assets_by_type(self, asset_type: str) -> List[Dict[str, Any]]:
        '''Get assets by type'''
        try:
            asset_type_enum = AssetType(asset_type)
            assets = self.asset_manager.get_assets_by_type(asset_type_enum)
            return [a.to_dict() for a in assets]
        except Exception as e:
            logger.error(f"Error getting assets by type: {e}")
            return []
    
    def get_asset_report(self) -> str:
        '''Get a detailed asset report'''
        return self.asset_manager.create_asset_report()
    
    def cleanup_assets(self) -> int:
        '''Clean up temporary and orphaned assets'''
        return self.asset_manager.cleanup_temp()
