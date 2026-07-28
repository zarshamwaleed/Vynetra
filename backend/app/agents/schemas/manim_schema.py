from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ManimSceneType(str, Enum):
    SQUARE_TO_CIRCLE = "SquareToCircle"
    MOVING_CIRCLE = "MovingCircle"
    GRAPH = "Graph"
    MATRIX = "Matrix"
    THREE_D = "ThreeD"
    ANIMATION = "Animation"
    CUSTOM = "Custom"

class AnimationQuality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    ULTRA = "ultra"

@dataclass
class ManimScene:
    name: str
    class_name: str
    code: str
    scene_type: ManimSceneType
    description: str
    output_path: str = ""
    status: str = "pending"
    video_path: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class ManimAnimation:
    topic: str
    scenes: List[ManimScene] = field(default_factory=list)
    quality: AnimationQuality = AnimationQuality.MEDIUM
    total_scenes: int = 0
    status: str = "pending"
    output_dir: str = "./generated/animations"
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "scenes": [
                {
                    "name": s.name,
                    "class_name": s.class_name,
                    "code": s.code,
                    "type": s.scene_type.value,
                    "description": s.description,
                    "status": s.status,
                    "video_path": s.video_path
                }
                for s in self.scenes
            ],
            "quality": self.quality.value,
            "total_scenes": self.total_scenes,
            "status": self.status,
            "output_dir": self.output_dir,
            "errors": self.errors,
            "created_at": self.created_at
        }
