from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class DiagramType(str, Enum):
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    ER = "er"
    GANTT = "gantt"
    PIE = "pie"
    STATE = "state"
    TIMELINE = "timeline"

class GraphvizType(str, Enum):
    DOT = "dot"
    NEATO = "neato"
    FDP = "fdp"
    SFDP = "sfdp"
    TWOPI = "twopi"
    CIRCO = "circo"

class DiagramFormat(str, Enum):
    PNG = "png"
    SVG = "svg"
    PDF = "pdf"
    MMD = "mmd"  # Mermaid markdown
    DOT = "dot"   # Graphviz source

@dataclass
class DiagramNode:
    id: str
    label: str
    shape: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None

@dataclass
class DiagramEdge:
    from_id: str
    to_id: str
    label: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None

@dataclass
class MermaidDiagram:
    type: DiagramType
    title: str
    nodes: List[DiagramNode] = field(default_factory=list)
    edges: List[DiagramEdge] = field(default_factory=list)
    code: str = ""
    format: DiagramFormat = DiagramFormat.MMD
    
    def generate_code(self) -> str:
        '''Generate Mermaid code'''
        if self.type == DiagramType.FLOWCHART:
            code = f"flowchart TD\n"
            for node in self.nodes:
                code += f"    {node.id}[\"{node.label}\"]\n"
            for edge in self.edges:
                code += f"    {edge.from_id} --> {edge.to_id}"
                if edge.label:
                    code += f" |{edge.label}|"
                code += "\n"
            self.code = code
            return code
            
        elif self.type == DiagramType.SEQUENCE:
            code = f"sequenceDiagram\n"
            for node in self.nodes:
                code += f"    participant {node.id} as {node.label}\n"
            for edge in self.edges:
                code += f"    {edge.from_id}->>{edge.to_id}: {edge.label or ''}\n"
            self.code = code
            return code
            
        elif self.type == DiagramType.CLASS:
            code = f"classDiagram\n"
            for node in self.nodes:
                code += f"    class {node.id} {{\n"
                code += f"        +{node.label}\n"
                code += f"    }}\n"
            for edge in self.edges:
                code += f"    {edge.from_id} <|-- {edge.to_id}\n"
            self.code = code
            return code
            
        else:
            code = f"graph LR\n"
            for node in self.nodes:
                code += f"    {node.id}[\"{node.label}\"]\n"
            for edge in self.edges:
                code += f"    {edge.from_id} --> {edge.to_id}\n"
            self.code = code
            return code
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "title": self.title,
            "nodes": [{"id": n.id, "label": n.label} for n in self.nodes],
            "edges": [{"from": e.from_id, "to": e.to_id, "label": e.label} for e in self.edges],
            "code": self.code
        }

@dataclass
class GraphvizDiagram:
    type: GraphvizType
    title: str
    nodes: List[DiagramNode] = field(default_factory=list)
    edges: List[DiagramEdge] = field(default_factory=list)
    code: str = ""
    format: DiagramFormat = DiagramFormat.DOT
    
    def generate_code(self) -> str:
        '''Generate Graphviz DOT code'''
        code = f"// {self.title}\n"
        code += f"digraph G {{\n"
        code += f"    label=\"{self.title}\"\n"
        code += f"    node [shape=box, style=filled, fillcolor=lightblue]\n"
        
        for node in self.nodes:
            code += f"    {node.id} [label=\"{node.label}\"]\n"
        
        for edge in self.edges:
            code += f"    {edge.from_id} -> {edge.to_id}"
            if edge.label:
                code += f" [label=\"{edge.label}\"]"
            code += "\n"
        
        code += "}\n"
        self.code = code
        return code
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "title": self.title,
            "nodes": [{"id": n.id, "label": n.label} for n in self.nodes],
            "edges": [{"from": e.from_id, "to": e.to_id, "label": e.label} for e in self.edges],
            "code": self.code
        }

@dataclass
class DiagramResult:
    topic: str
    diagrams: List[Dict[str, Any]] = field(default_factory=list)
    total_diagrams: int = 0
    status: str = "pending"
    errors: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "diagrams": self.diagrams,
            "total_diagrams": self.total_diagrams,
            "status": self.status,
            "errors": self.errors,
            "created_at": self.created_at
        }
    
    def to_markdown(self) -> str:
        md = f"# Diagrams for: {self.topic}\n\n"
        md += f"**Total Diagrams:** {self.total_diagrams}\n"
        md += f"**Status:** {self.status}\n\n"
        
        for i, diagram in enumerate(self.diagrams, 1):
            md += f"## Diagram {i}: {diagram.get('title', 'Untitled')}\n\n"
            md += f"**Type:** {diagram.get('type', 'N/A')}\n\n"
            md += "`mermaid\n"
            md += diagram.get('code', '')
            md += "\n`\n\n"
        
        if self.errors:
            md += "## Errors\n"
            for error in self.errors:
                md += f"- {error}\n"
        
        return md
