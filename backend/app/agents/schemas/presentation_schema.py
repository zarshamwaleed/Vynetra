from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class SlideLayout(str, Enum):
    TITLE = "title"
    TITLE_BULLET = "title_bullet"
    CONTENT = "content"
    TWO_COLUMN = "two_column"
    DIAGRAM = "diagram"
    VIDEO = "video"
    BLANK = "blank"

class SlideTheme(str, Enum):
    MODERN = "modern"
    CLASSIC = "classic"
    CREATIVE = "creative"
    PROFESSIONAL = "professional"
    MINIMAL = "minimal"

@dataclass
class SlideElement:
    type: str
    content: Any
    position: Optional[Dict[str, int]] = None
    size: Optional[Dict[str, int]] = None
    style: Optional[Dict[str, Any]] = None

@dataclass
class PptSlide:
    number: int
    layout: SlideLayout
    title: str
    content: str = ""
    bullet_points: List[str] = field(default_factory=list)
    speaker_notes: str = ""
    images: List[str] = field(default_factory=list)
    diagrams: List[str] = field(default_factory=list)
    videos: List[str] = field(default_factory=list)
    elements: List[SlideElement] = field(default_factory=list)
    theme: SlideTheme = SlideTheme.MODERN
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "layout": self.layout.value,
            "title": self.title,
            "content": self.content,
            "bullet_points": self.bullet_points,
            "speaker_notes": self.speaker_notes,
            "images": self.images,
            "diagrams": self.diagrams,
            "videos": self.videos,
            "theme": self.theme.value
        }

@dataclass
class PowerPointPresentation:
    title: str
    topic: str
    slides: List[PptSlide] = field(default_factory=list)
    total_slides: int = 0
    theme: SlideTheme = SlideTheme.MODERN
    output_path: str = ""
    status: str = "pending"
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "topic": self.topic,
            "slides": [s.to_dict() for s in self.slides],
            "total_slides": self.total_slides,
            "theme": self.theme.value,
            "output_path": self.output_path,
            "status": self.status,
            "errors": self.errors,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
