from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class SourceType(str, Enum):
    WEBSITE = "website"
    ARTICLE = "article"
    PAPER = "paper"
    BOOK = "book"
    VIDEO = "video"
    DOCUMENTATION = "documentation"
    OTHER = "other"

class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class Reference:
    title: str
    url: Optional[str] = None
    source_type: SourceType = SourceType.WEBSITE
    author: Optional[str] = None
    year: Optional[int] = None
    publisher: Optional[str] = None
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    key_points: List[str] = field(default_factory=list)
    accessed_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "source_type": self.source_type.value,
            "author": self.author,
            "year": self.year,
            "publisher": self.publisher,
            "confidence": self.confidence.value,
            "key_points": self.key_points,
            "accessed_date": self.accessed_date
        }

@dataclass
class ResearchFinding:
    topic: str
    summary: str
    key_concepts: List[str] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    key_questions: List[str] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "summary": self.summary,
            "key_concepts": self.key_concepts,
            "key_facts": self.key_facts,
            "key_questions": self.key_questions,
            "references": [r.to_dict() for r in self.references],
            "confidence": self.confidence.value,
            "notes": self.notes,
            "created_at": self.created_at
        }
    
    def to_markdown(self) -> str:
        md = f"# Research on {self.topic}\n\n"
        md += f"## Summary\n{self.summary}\n\n"
        
        if self.key_concepts:
            md += "## Key Concepts\n"
            for concept in self.key_concepts:
                md += f"- {concept}\n"
            md += "\n"
        
        if self.key_facts:
            md += "## Key Facts\n"
            for fact in self.key_facts:
                md += f"- {fact}\n"
            md += "\n"
        
        if self.references:
            md += "## References\n"
            for ref in self.references:
                md += f"- {ref.title}"
                if ref.author:
                    md += f" by {ref.author}"
                if ref.year:
                    md += f" ({ref.year})"
                if ref.url:
                    md += f"\n  {ref.url}"
                md += "\n"
            md += "\n"
        
        if self.key_questions:
            md += "## Key Questions\n"
            for q in self.key_questions:
                md += f"- {q}\n"
            md += "\n"
        
        md += f"\n*Confidence Level: {self.confidence.value}*\n"
        md += f"*Researched: {self.created_at}*\n"
        
        return md

@dataclass
class ResearchResult:
    topic: str
    findings: List[ResearchFinding] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    summary: str = ""
    status: str = "pending"
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "findings": [f.to_dict() for f in self.findings],
            "references": [r.to_dict() for r in self.references],
            "summary": self.summary,
            "status": self.status,
            "errors": self.errors,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_markdown(self) -> str:
        md = f"# Research Report: {self.topic}\n\n"
        
        if self.summary:
            md += f"## Executive Summary\n{self.summary}\n\n"
        
        if self.findings:
            md += "## Research Findings\n"
            for finding in self.findings:
                md += f"\n### {finding.topic}\n"
                md += f"{finding.summary}\n\n"
                if finding.key_concepts:
                    md += "**Key Concepts:**\n"
                    for concept in finding.key_concepts:
                        md += f"- {concept}\n"
                    md += "\n"
        
        if self.references:
            md += "## References\n"
            for ref in self.references:
                md += f"- {ref.title}"
                if ref.author:
                    md += f" by {ref.author}"
                if ref.year:
                    md += f" ({ref.year})"
                if ref.url:
                    md += f"\n  {ref.url}"
                md += "\n"
        
        if self.errors:
            md += "\n## Errors\n"
            for error in self.errors:
                md += f"- {error}\n"
        
        md += f"\n*Status: {self.status}*\n"
        md += f"*Created: {self.created_at}*\n"
        md += f"*Updated: {self.updated_at}*\n"
        
        return md
