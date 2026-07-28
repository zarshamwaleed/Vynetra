from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ExportFormat(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    JSON = "json"

class PDFStyle(str, Enum):
    PROFESSIONAL = "professional"
    MODERN = "modern"
    MINIMAL = "minimal"
    CREATIVE = "creative"

@dataclass
class ExportSlide:
    number: int
    title: str
    content: str = ""
    bullet_points: List[str] = field(default_factory=list)
    speaker_notes: str = ""
    images: List[str] = field(default_factory=list)
    diagrams: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "content": self.content,
            "bullet_points": self.bullet_points,
            "speaker_notes": self.speaker_notes,
            "images": self.images,
            "diagrams": self.diagrams
        }

@dataclass
class ExportDocument:
    title: str
    topic: str
    slides: List[ExportSlide] = field(default_factory=list)
    total_slides: int = 0
    style: PDFStyle = PDFStyle.PROFESSIONAL
    output_path: str = ""
    formats: List[str] = field(default_factory=list)
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
            "style": self.style.value,
            "output_path": self.output_path,
            "formats": self.formats,
            "status": self.status,
            "errors": self.errors,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
