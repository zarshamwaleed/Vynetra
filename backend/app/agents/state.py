from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json

@dataclass
class AgentState:
    prompt: str = ""
    topic: str = ""
    outline: Dict[str, Any] = field(default_factory=dict)
    slide_count: int = 0
    research: Dict[str, Any] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)
    content: Dict[str, Any] = field(default_factory=dict)
    slides: List[Dict[str, Any]] = field(default_factory=list)
    visualizations: Dict[str, Any] = field(default_factory=dict)
    diagrams: List[str] = field(default_factory=list)
    animations: Dict[str, Any] = field(default_factory=dict)
    presentation: Dict[str, Any] = field(default_factory=dict)
    presentation_path: str = ""
    export: Dict[str, Any] = field(default_factory=dict)
    export_paths: Dict[str, str] = field(default_factory=dict)
    current_agent: str = ""
    errors: List[str] = field(default_factory=list)
    status: str = "pending"
    progress: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "topic": self.topic,
            "outline": self.outline,
            "slide_count": self.slide_count,
            "research": self.research,
            "references": self.references,
            "content": self.content,
            "slides": self.slides,
            "visualizations": self.visualizations,
            "diagrams": self.diagrams,
            "animations": self.animations,
            "presentation": self.presentation,
            "presentation_path": self.presentation_path,
            "export": self.export,
            "export_paths": self.export_paths,
            "current_agent": self.current_agent,
            "errors": self.errors,
            "status": self.status,
            "progress": self.progress,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
