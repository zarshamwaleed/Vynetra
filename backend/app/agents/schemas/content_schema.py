from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class ContentStyle(str, Enum):
    EDUCATIONAL = "educational"
    PROFESSIONAL = "professional"
    CONCISE = "concise"
    DETAILED = "detailed"
    PERSUASIVE = "persuasive"

class ContentQuality(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SlideContent:
    number: int
    title: str
    subtitle: Optional[str] = None
    content: str = ""
    bullet_points: List[str] = field(default_factory=list)
    explanation: str = ""
    examples: List[str] = field(default_factory=list)
    speaker_notes: str = ""
    style: ContentStyle = ContentStyle.EDUCATIONAL
    quality_score: float = 0.0
    key_takeaways: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "number": self.number,
            "title": self.title,
            "subtitle": self.subtitle,
            "content": self.content,
            "bullet_points": self.bullet_points,
            "explanation": self.explanation,
            "examples": self.examples,
            "speaker_notes": self.speaker_notes,
            "style": self.style.value,
            "quality_score": self.quality_score,
            "key_takeaways": self.key_takeaways,
            "references": self.references
        }

@dataclass
class PresentationContent:
    title: str
    topic: str
    slides: List[SlideContent] = field(default_factory=list)
    total_slides: int = 0
    style: ContentStyle = ContentStyle.EDUCATIONAL
    audience: str = "general"
    tone: str = "professional"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "topic": self.topic,
            "slides": [s.to_dict() for s in self.slides],
            "total_slides": self.total_slides,
            "style": self.style.value,
            "audience": self.audience,
            "tone": self.tone,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)
    
    def to_markdown(self) -> str:
        md = f"# {self.title}\n\n"
        md += f"**Topic:** {self.topic}\n"
        md += f"**Audience:** {self.audience}\n"
        md += f"**Tone:** {self.tone}\n"
        md += f"**Total Slides:** {self.total_slides}\n\n"
        md += "---\n\n"
        
        for slide in self.slides:
            md += f"## Slide {slide.number}: {slide.title}\n\n"
            if slide.subtitle:
                md += f"*{slide.subtitle}*\n\n"
            if slide.content:
                md += f"{slide.content}\n\n"
            if slide.bullet_points:
                md += "**Key Points:**\n"
                for point in slide.bullet_points:
                    md += f"- {point}\n"
                md += "\n"
            if slide.explanation:
                md += f"**Explanation:** {slide.explanation}\n\n"
            if slide.examples:
                md += "**Examples:**\n"
                for example in slide.examples:
                    md += f"- {example}\n"
                md += "\n"
            if slide.speaker_notes:
                md += f"**Speaker Notes:** {slide.speaker_notes}\n\n"
            if slide.key_takeaways:
                md += "**Key Takeaways:**\n"
                for takeaway in slide.key_takeaways:
                    md += f"- {takeaway}\n"
                md += "\n"
            md += "---\n\n"
        
        return md
