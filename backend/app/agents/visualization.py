import json
import logging
import os
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.agents.base import BaseAgent
from app.agents.state import AgentState
from app.agents.schemas.diagram_schema import (
    DiagramType, GraphvizType, DiagramFormat, DiagramResult,
    MermaidDiagram, GraphvizDiagram, DiagramNode, DiagramEdge
)
from app.agents.prompts.diagram_prompts import (
    DIAGRAM_SYSTEM_PROMPT, FLOWCHART_PROMPT, SEQUENCE_PROMPT,
    DIAGRAM_EXTRACTION_PROMPT
)

logger = logging.getLogger(__name__)

class VisualizationAgent(BaseAgent):
    '''Enhanced Visualization Agent for diagram generation'''
    
    def __init__(self, llm_service, mcp_client=None):
        super().__init__("Visualization", llm_service)
        self.mcp = mcp_client
    
    async def process(self, state: AgentState) -> AgentState:
        await self._log_step(state, "Generating diagrams...")
        
        try:
            # Get content and topic
            slides = state.slides
            topic = state.topic or state.prompt[:50]
            
            # Generate diagrams based on content
            diagrams = []
            
            # Extract diagram-worthy content
            content_text = self._extract_content_text(slides)
            
            # Generate flowchart
            flowchart = await self._generate_flowchart(topic, content_text)
            if flowchart:
                diagrams.append(flowchart.to_dict())
            
            # Generate sequence diagram if applicable
            sequence = await self._generate_sequence(topic, content_text)
            if sequence:
                diagrams.append(sequence.to_dict())
            
            # Create result
            diagram_result = DiagramResult(
                topic=topic,
                diagrams=diagrams,
                total_diagrams=len(diagrams),
                status="completed"
            )
            
            # Update state
            state.visualizations = diagram_result.to_dict()
            state.diagrams = diagrams
            state.progress = 75
            
            # Save to file
            await self._save_diagrams(diagram_result)
            
            await self._log_step(
                state,
                f"Generated {len(diagrams)} diagrams"
            )
            
        except Exception as e:
            await self._add_error(state, f"Visualization error: {str(e)}")
            logger.error(f"Visualization error details: {e}", exc_info=True)
        
        return state
    
    def _extract_content_text(self, slides: List[Dict[str, Any]]) -> str:
        '''Extract text content from slides for diagram generation'''
        text = ""
        for slide in slides[:5]:  # Limit to first 5 slides
            if slide.get('content'):
                text += slide['content'] + "\n"
            if slide.get('bullet_points'):
                text += "\n".join(slide['bullet_points']) + "\n"
            if slide.get('explanation'):
                text += slide['explanation'] + "\n"
        return text[:2000]  # Limit to 2000 characters
    
    async def _generate_flowchart(
        self,
        topic: str,
        content_text: str
    ) -> Optional[MermaidDiagram]:
        '''Generate a flowchart diagram'''
        try:
            prompt = FLOWCHART_PROMPT.format(
                topic=topic,
                content=content_text[:1000]  # Limit content
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=DIAGRAM_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=2048
            )
            
            data = self._parse_json(response.text)
            
            if data and data.get('nodes') and data.get('edges'):
                # Create nodes
                nodes = []
                for node_data in data.get('nodes', []):
                    node = DiagramNode(
                        id=node_data.get('id', f"n{len(nodes)+1}"),
                        label=node_data.get('label', 'Node')
                    )
                    nodes.append(node)
                
                # Create edges
                edges = []
                for edge_data in data.get('edges', []):
                    edge = DiagramEdge(
                        from_id=edge_data.get('from', ''),
                        to_id=edge_data.get('to', ''),
                        label=edge_data.get('label')
                    )
                    edges.append(edge)
                
                # Create diagram
                diagram = MermaidDiagram(
                    type=DiagramType.FLOWCHART,
                    title=data.get('title', f"{topic} Process Flow"),
                    nodes=nodes,
                    edges=edges
                )
                diagram.generate_code()
                return diagram
            else:
                # Create a default flowchart
                return self._create_default_flowchart(topic)
                
        except Exception as e:
            logger.warning(f"Flowchart generation failed: {e}")
            return self._create_default_flowchart(topic)
    
    async def _generate_sequence(
        self,
        topic: str,
        content_text: str
    ) -> Optional[MermaidDiagram]:
        '''Generate a sequence diagram'''
        try:
            prompt = SEQUENCE_PROMPT.format(
                topic=topic,
                context=content_text[:500]
            )
            
            response = await self.llm.generate(
                prompt=prompt,
                system_prompt=DIAGRAM_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=1024
            )
            
            data = self._parse_json(response.text)
            
            if data and data.get('participants') and data.get('messages'):
                # Create participants as nodes
                nodes = []
                for p in data.get('participants', []):
                    node = DiagramNode(
                        id=p.get('id', f"p{len(nodes)+1}"),
                        label=p.get('label', 'Participant')
                    )
                    nodes.append(node)
                
                # Create messages as edges
                edges = []
                for msg in data.get('messages', []):
                    edge = DiagramEdge(
                        from_id=msg.get('from', ''),
                        to_id=msg.get('to', ''),
                        label=msg.get('message', '')
                    )
                    edges.append(edge)
                
                if nodes and edges:
                    diagram = MermaidDiagram(
                        type=DiagramType.SEQUENCE,
                        title=data.get('title', f"{topic} Sequence"),
                        nodes=nodes,
                        edges=edges
                    )
                    diagram.generate_code()
                    return diagram
            
            return None
            
        except Exception as e:
            logger.warning(f"Sequence diagram generation failed: {e}")
            return None
    
    def _create_default_flowchart(self, topic: str) -> MermaidDiagram:
        '''Create a default flowchart'''
        nodes = [
            DiagramNode(id="start", label="Start"),
            DiagramNode(id="process", label="Process"),
            DiagramNode(id="decision", label="Decision"),
            DiagramNode(id="end", label="End")
        ]
        
        edges = [
            DiagramEdge(from_id="start", to_id="process", label="Begin"),
            DiagramEdge(from_id="process", to_id="decision", label="Process"),
            DiagramEdge(from_id="decision", to_id="end", label="Complete")
        ]
        
        diagram = MermaidDiagram(
            type=DiagramType.FLOWCHART,
            title=f"{topic} Flowchart",
            nodes=nodes,
            edges=edges
        )
        diagram.generate_code()
        return diagram
    
    async def _save_diagrams(self, result: DiagramResult):
        '''Save diagrams to file'''
        try:
            # Create directories
            os.makedirs("./generated/diagrams", exist_ok=True)
            
            # Save as markdown with embedded diagrams
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            md_path = f"./generated/diagrams/diagrams_{timestamp}.md"
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(result.to_markdown())
            
            # Also save as JSON
            json_path = f"./generated/diagrams/diagrams_{timestamp}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2)
            
            logger.info(f"Diagrams saved to: {md_path} and {json_path}")
            
        except Exception as e:
            logger.warning(f"Failed to save diagrams: {e}")
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        '''Parse JSON from LLM response'''
        try:
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return {}
