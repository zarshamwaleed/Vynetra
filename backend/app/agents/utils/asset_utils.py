import os
import shutil
import hashlib
import json
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import uuid

from app.agents.schemas.asset_schema import Asset, AssetType, AssetStatus, AssetCollection

logger = logging.getLogger(__name__)

class AssetManager:
    '''Manages all assets in the Vynetra system'''
    
    def __init__(self, base_dir: str = "./generated"):
        self.base_dir = Path(base_dir)
        self.collection = AssetCollection()
        self.asset_map: Dict[str, Asset] = {}
        self._init_directories()
        self._load_assets()
    
    def _init_directories(self):
        '''Initialize all asset directories'''
        directories = [
            "animations",
            "images",
            "diagrams",
            "ppt",
            "pdf",
            "notes",
            "references",
            "export",
            "content",
            "presentations",
            "research"
        ]
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory created: {dir_path}")
    
    def _load_assets(self):
        '''Load existing assets from directories'''
        for dir_name in self.base_dir.iterdir():
            if dir_name.is_dir():
                for file_path in dir_name.rglob("*"):
                    if file_path.is_file():
                        asset = self._create_asset_from_file(file_path)
                        if asset:
                            self.collection.add_asset(asset)
                            self.asset_map[asset.id] = asset
        
        logger.info(f"Loaded {self.collection.total_count} assets")
    
    def _create_asset_from_file(self, file_path: Path) -> Optional[Asset]:
        '''Create an asset from a file path'''
        try:
            # Determine asset type from extension
            ext = file_path.suffix.lower()
            asset_type = self._get_asset_type(ext)
            
            # Get file info
            size = file_path.stat().st_size
            asset_id = str(uuid.uuid4())
            
            # Get relative path
            rel_path = str(file_path.relative_to(self.base_dir))
            
            return Asset(
                id=asset_id,
                name=file_path.name,
                type=asset_type,
                path=rel_path,
                size=size,
                status=AssetStatus.GENERATED,
                metadata={
                    "extension": ext,
                    "parent_dir": str(file_path.parent.name),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }
            )
        except Exception as e:
            logger.warning(f"Failed to create asset from {file_path}: {e}")
            return None
    
    def _get_asset_type(self, extension: str) -> AssetType:
        '''Map file extension to asset type'''
        type_map = {
            ".mp4": AssetType.VIDEO,
            ".mov": AssetType.VIDEO,
            ".avi": AssetType.VIDEO,
            ".png": AssetType.IMAGE,
            ".jpg": AssetType.IMAGE,
            ".jpeg": AssetType.IMAGE,
            ".svg": AssetType.IMAGE,
            ".gif": AssetType.IMAGE,
            ".mmd": AssetType.DIAGRAM,
            ".dot": AssetType.DIAGRAM,
            ".pptx": AssetType.PPT,
            ".pdf": AssetType.PDF,
            ".md": AssetType.MARKDOWN,
            ".json": AssetType.JSON,
            ".txt": AssetType.NOTES
        }
        return type_map.get(extension, AssetType.JSON)
    
    def add_asset(
        self,
        file_path: str,
        asset_type: Optional[AssetType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Asset]:
        '''Add a new asset to the collection'''
        try:
            path = Path(file_path)
            if not path.exists():
                logger.warning(f"File not found: {file_path}")
                return None
            
            # Create asset
            asset = self._create_asset_from_file(path)
            if not asset:
                return None
            
            # Override type if provided
            if asset_type:
                asset.type = asset_type
            
            # Add metadata
            if metadata:
                asset.metadata.update(metadata)
            
            # Add to collection
            self.collection.add_asset(asset)
            self.asset_map[asset.id] = asset
            
            logger.info(f"Added asset: {asset.name} ({asset.type.value})")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to add asset: {e}")
            return None
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        '''Get an asset by ID'''
        return self.asset_map.get(asset_id)
    
    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        '''Get all assets of a specific type'''
        return self.collection.get_by_type(asset_type)
    
    def get_assets_by_status(self, status: AssetStatus) -> List[Asset]:
        '''Get all assets with a specific status'''
        return self.collection.get_by_status(status)
    
    def get_assets_by_extension(self, extension: str) -> List[Asset]:
        '''Get all assets with a specific extension'''
        extension = extension.lower()
        if not extension.startswith('.'):
            extension = f".{extension}"
        return [a for a in self.collection.assets if a.metadata.get('extension') == extension]
    
    def delete_asset(self, asset_id: str) -> bool:
        '''Delete an asset from the collection and file system'''
        try:
            asset = self.asset_map.get(asset_id)
            if not asset:
                return False
            
            # Delete file
            file_path = self.base_dir / asset.path
            if file_path.exists():
                file_path.unlink()
            
            # Remove from collection
            self.collection.remove_asset(asset_id)
            del self.asset_map[asset_id]
            
            logger.info(f"Deleted asset: {asset.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete asset: {e}")
            return False
    
    def move_asset(self, asset_id: str, new_dir: str) -> Optional[Asset]:
        '''Move an asset to a new directory'''
        try:
            asset = self.asset_map.get(asset_id)
            if not asset:
                return None
            
            # Get current and new paths
            old_path = self.base_dir / asset.path
            new_path = self.base_dir / new_dir / asset.name
            
            # Create new directory
            new_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file
            shutil.move(str(old_path), str(new_path))
            
            # Update asset
            asset.path = str(new_path.relative_to(self.base_dir))
            asset.metadata["parent_dir"] = new_dir
            asset.updated_at = datetime.now().isoformat()
            
            logger.info(f"Moved asset: {asset.name} to {new_dir}")
            return asset
            
        except Exception as e:
            logger.error(f"Failed to move asset: {e}")
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        '''Get a summary of all assets'''
        return self.collection.get_summary()
    
    def export_manifest(self, output_path: str = "./generated/manifest.json") -> str:
        '''Export asset manifest to JSON'''
        try:
            manifest = {
                "exported_at": datetime.now().isoformat(),
                "total_assets": self.collection.total_count,
                "total_size": self.collection.total_size,
                "assets": [a.to_dict() for a in self.collection.assets]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Manifest exported to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export manifest: {e}")
            return ""
    
    def cleanup_temp(self) -> int:
        '''Clean up temporary files'''
        temp_count = 0
        temp_dir = self.base_dir / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            temp_count += 1
        
        # Clean up orphaned files (files not in the collection)
        for dir_path in self.base_dir.iterdir():
            if dir_path.is_dir() and dir_path.name != "temp":
                for file_path in dir_path.rglob("*"):
                    if file_path.is_file():
                        # Check if file is in collection
                        rel_path = str(file_path.relative_to(self.base_dir))
                        found = False
                        for asset in self.collection.assets:
                            if asset.path == rel_path:
                                found = True
                                break
                        if not found:
                            file_path.unlink()
                            temp_count += 1
        
        logger.info(f"Cleaned up {temp_count} temporary files")
        return temp_count
    
    def create_asset_report(self) -> str:
        '''Create a detailed asset report'''
        summary = self.get_summary()
        
        report = f"""
        ============================================================
        ASSET MANAGEMENT REPORT
        ============================================================
        
        Total Assets: {summary['total_count']}
        Total Size: {summary['total_size_readable']}
        
        By Type:
        {self._format_dict(summary['by_type']['counts'])}
        
        By Size:
        {self._format_dict(summary['by_type']['sizes'])}
        
        By Status:
        {self._format_dict(summary['by_status'])}
        
        ============================================================
        """
        
        return report
    
    def _format_dict(self, data: Dict[str, Any]) -> str:
        '''Format a dictionary for display'''
        lines = []
        for key, value in data.items():
            lines.append(f"  {key}: {value}")
        return "\n".join(lines)
