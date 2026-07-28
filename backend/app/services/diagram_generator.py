import logging
import os
import json
import re
import tempfile
from typing import Dict, Any, List, Optional
from app.services.llm import LLMService

logger = logging.getLogger(__name__)

class DiagramGenerator:
    """Generate meaningful diagrams using Mermaid"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def generate_diagrams(self, topic: str, slides: List[Dict]) -> List[Dict]:
        """Generate diagrams based on content"""
        diagrams = []
        
        # Generate flowchart
        flowchart = await self._generate_flowchart(topic, slides)
        if flowchart:
            diagrams.append(flowchart)
        
        # Generate architecture/process diagram
        if len(slides) > 3:
            process_diagram = await self._generate_process_diagram(topic, slides)
            if process_diagram:
                diagrams.append(process_diagram)
        
        return diagrams
    
    async def _generate_flowchart(self, topic: str, slides: List[Dict]) -> Optional[Dict]:
        """Generate a meaningful flowchart"""
        try:
            # Extract key concepts from slides
            concepts = []
            for slide in slides[:5]:
                title = slide.get("title", "")
                if title and "introduction" not in title.lower():
                    concepts.append(title)
            
            if not concepts:
                concepts = [f"Step {i+1}" for i in range(4)]
            
            system_prompt = f"""You are a diagram expert. Create a Mermaid flowchart showing the process or concepts related to: {topic}

            The flowchart should show the flow of concepts or steps.
            Use the following concepts: {', '.join(concepts[:4])}

            Return ONLY valid JSON with this structure:
            {{
                "title": "Flowchart: {topic}",
                "type": "flowchart",
                "code": "graph TD\\n    A[Start] --> B[Process]\\n    B --> C[Decision]\\n    C -->|Yes| D[End]\\n    C -->|No| B",
                "description": "Flowchart showing the process of {topic}"
            }}
            
            Make the flowchart meaningful with proper labels based on the topic.
            Use arrows (-->) and decisions with labels.
            """
            
            response = await self.llm.generate(
                prompt=f"Create a flowchart for: {topic}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1024
            )
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
            
        except Exception as e:
            logger.error(f"Error generating flowchart: {e}")
            return self._create_fallback_flowchart(topic)
    
    async def _generate_process_diagram(self, topic: str, slides: List[Dict]) -> Optional[Dict]:
        """Generate a process/architecture diagram"""
        try:
            # Extract key steps
            steps = []
            for slide in slides[:6]:
                title = slide.get("title", "")
                if title and title not in ["Introduction", "Summary", "Conclusion", "Q&A"]:
                    steps.append(title)
            
            if len(steps) < 3:
                steps = [f"Step {i+1}" for i in range(4)]
            
            system_prompt = f"""You are a diagram expert. Create a Mermaid architecture or process diagram for: {topic}

            Show the main components or steps in the process.
            Steps to include: {', '.join(steps[:5])}

            Return ONLY valid JSON with this structure:
            {{
                "title": "Process Diagram: {topic}",
                "type": "process",
                "code": "graph LR\\n    A[Component 1] --> B[Component 2]\\n    B --> C[Component 3]\\n    C --> D[Component 4]",
                "description": "Architecture diagram of {topic}"
            }}
            
            Create a meaningful diagram with proper labels.
            """
            
            response = await self.llm.generate(
                prompt=f"Create a process diagram for: {topic}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1024
            )
            
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return None
            
        except Exception as e:
            logger.error(f"Error generating process diagram: {e}")
            return None
    
    def _create_fallback_flowchart(self, topic: str) -> Dict:
        """Create fallback flowchart"""
        code = f"""graph TD
    A[Start: {topic}] --> B[Understand Requirements]
    B --> C[Design Solution]
    C --> D[Implement]
    D --> E[Test]
    E --> F[Deploy]
    F --> G[Monitor & Optimize]
    G --> H[End]"""
        
        return {
            "title": f"Flowchart: {topic}",
            "type": "flowchart",
            "code": code,
            "description": f"Process flow for {topic}"
        }
