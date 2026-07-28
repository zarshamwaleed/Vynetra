from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import os

class AssetType(str, Enum):
    ANIMATION = "animation"
    IMAGE = "image"
    DIAGRAM = "diagram"
    PPT = "ppt"
    PDF = "pdf"
    NOTES = "notes"
    REFERENCES = "references"
    JSON = "json"
    MARKDOWN = "markdown"
    VIDEO = "video"

class AssetStatus(str, Enum):
    PENDING = "pending"
    GENERATED = "generated"
    PROCESSED = "processed"
    ARCHIVED = "archived"
    DELETED = "deleted"
    ERROR = "error"

@dataclass
class Asset:
    id: str
    name: str
    type: AssetType
    path: str
    size: int  # bytes
    status: AssetStatus = AssetStatus.GENERATED
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "path": self.path,
            "size": self.size,
            "status": self.status.value,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_bytes(self) -> str:
        if self.size < 1024:
            return f"{self.size} B"
        elif self.size < 1024 * 1024:
            return f"{self.size / 1024:.2f} KB"
        elif self.size < 1024 * 1024 * 1024:
            return f"{self.size / (1024 * 1024):.2f} MB"
        else:
            return f"{self.size / (1024 * 1024 * 1024):.2f} GB"

@dataclass
class AssetCollection:
    assets: List[Asset] = field(default_factory=list)
    total_size: int = 0
    total_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "assets": [a.to_dict() for a in self.assets],
            "total_size": self.total_size,
            "total_count": self.total_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def add_asset(self, asset: Asset):
        self.assets.append(asset)
        self.total_size += asset.size
        self.total_count += 1
        self.updated_at = datetime.now().isoformat()
    
    def remove_asset(self, asset_id: str):
        for asset in self.assets:
            if asset.id == asset_id:
                self.assets.remove(asset)
                self.total_size -= asset.size
                self.total_count -= 1
                break
        self.updated_at = datetime.now().isoformat()
    
    def get_by_type(self, asset_type: AssetType) -> List[Asset]:
        return [a for a in self.assets if a.type == asset_type]
    
    def get_by_status(self, status: AssetStatus) -> List[Asset]:
        return [a for a in self.assets if a.status == status]
    
    def get_summary(self) -> Dict[str, Any]:
        type_counts = {}
        type_sizes = {}
        for asset in self.assets:
            type_counts[asset.type.value] = type_counts.get(asset.type.value, 0) + 1
            type_sizes[asset.type.value] = type_sizes.get(asset.type.value, 0) + asset.size
        
        return {
            "total_count": self.total_count,
            "total_size": self.total_size,
            "total_size_readable": self._format_size(self.total_size),
            "by_type": {
                "counts": type_counts,
                "sizes": {k: self._format_size(v) for k, v in type_sizes.items()}
            },
            "by_status": {
                status.value: len(self.get_by_status(status))
                for status in AssetStatus
            }
        }
    
    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.2f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.2f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.2f} GB"
