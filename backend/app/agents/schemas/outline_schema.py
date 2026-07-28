from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class SlideType(str, Enum):
    TITLE = "title"
    INTRODUCTION = "introduction"
    CONTENT = "content"
    DIAGRAM = "diagram"
    EXAMPLE = "example"
    SUMMARY = "summary"
    CONCLUSION = "conclusion"
    QNA = "qna"
    REFERENCE = "reference"

class AudienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    MIXED = "mixed"

class PresentationTone(str, Enum):
    PROFESSIONAL = "professional"
    EDUCATIONAL = "educational"
    CASUAL = "casual"
    PERSUASIVE = "persuasive"
    INSPIRATIONAL = "inspirational"

@dataclass
class SlideOutline:
    number: int
    title: str
    slide_type: SlideType
    purpose: str
    key_points: List[str] = field(default_factory=list)
    estimated_duration: int = 60  # seconds
    notes: Optional[str] = None
    prerequisites: List[str] = field(default_factory=list)
    learning_objectives: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)

@dataclass
class PresentationOutline:
    title: str
    topic: str
    audience: AudienceLevel
    tone: PresentationTone
    total_slides: int
    estimated_duration: int  # total minutes
    slides: List[SlideOutline]
    learning_flow: str
    prerequisites: List[str] = field(default_factory=list)
    key_takeaways: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    created_at: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "topic": self.topic,
            "audience": self.audience.value,
            "tone": self.tone.value,
            "total_slides": self.total_slides,
            "estimated_duration": self.estimated_duration,
            "slides": [
                {
                    "number": s.number,
                    "title": s.title,
                    "type": s.slide_type.value,
                    "purpose": s.purpose,
                    "key_points": s.key_points,
                    "estimated_duration": s.estimated_duration,
                    "notes": s.notes,
                    "prerequisites": s.prerequisites,
                    "learning_objectives": s.learning_objectives
                }
                for s in self.slides
            ],
            "learning_flow": self.learning_flow,
            "prerequisites": self.prerequisites,
            "key_takeaways": self.key_takeaways,
            "references": self.references,
            "created_at": self.created_at
        }
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)
