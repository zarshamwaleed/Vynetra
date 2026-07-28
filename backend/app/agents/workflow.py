import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.supervisor import SupervisorAgent
from app.agents.planner import PlannerAgent
from app.agents.research import ResearchAgent
from app.agents.content import ContentAgent
from app.agents.visualization import VisualizationAgent
from app.agents.presentation import PresentationAgent
from app.agents.export import ExportAgent
from app.services.llm import LLMService

logger = logging.getLogger(__name__)

class PresentationWorkflow:
    '''LangGraph workflow for presentation generation'''
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.supervisor = SupervisorAgent(llm_service)
        self.planner = PlannerAgent(llm_service)
        self.research = ResearchAgent(llm_service)
        self.content = ContentAgent(llm_service)
        self.visualization = VisualizationAgent(llm_service)
        self.presentation = PresentationAgent(llm_service)
        self.export = ExportAgent(llm_service)
        self.workflow = None
        self.app = None
    
    def build_workflow(self) -> StateGraph:
        '''Build the LangGraph workflow'''
        
        # Create the workflow graph
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("research", self._research_node)
        workflow.add_node("content", self._content_node)
        workflow.add_node("visualization", self._visualization_node)
        workflow.add_node("presentation", self._presentation_node)
        workflow.add_node("export", self._export_node)
        
        # Define the flow
        workflow.set_entry_point("supervisor")
        
        workflow.add_edge("supervisor", "planner")
        workflow.add_edge("planner", "research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "visualization")
        workflow.add_edge("visualization", "presentation")
        workflow.add_edge("presentation", "export")
        workflow.add_edge("export", END)
        
        self.workflow = workflow
        return workflow
    
    async def _supervisor_node(self, state: AgentState) -> AgentState:
        '''Supervisor node'''
        return await self.supervisor.process(state)
    
    async def _planner_node(self, state: AgentState) -> AgentState:
        '''Planner node'''
        return await self.planner.process(state)
    
    async def _research_node(self, state: AgentState) -> AgentState:
        '''Research node'''
        return await self.research.process(state)
    
    async def _content_node(self, state: AgentState) -> AgentState:
        '''Content node'''
        return await self.content.process(state)
    
    async def _visualization_node(self, state: AgentState) -> AgentState:
        '''Visualization node'''
        return await self.visualization.process(state)
    
    async def _presentation_node(self, state: AgentState) -> AgentState:
        '''Presentation node'''
        return await self.presentation.process(state)
    
    async def _export_node(self, state: AgentState) -> AgentState:
        '''Export node'''
        return await self.export.process(state)
    
    async def run(self, prompt: str) -> AgentState:
        '''Run the complete workflow'''
        logger.info(f"Starting presentation workflow for: {prompt[:50]}...")
        
        # Initialize state
        initial_state = AgentState(prompt=prompt)
        
        # Build and compile the workflow
        if not self.workflow:
            self.build_workflow()
        
        self.app = self.workflow.compile()
        
        # Run the workflow
        try:
            # Invoke the workflow with the initial state
            final_state = await self.app.ainvoke(initial_state)
            
            # Check if we got back an AgentState or a dict
            if isinstance(final_state, dict):
                # Convert dict to AgentState if needed
                state_dict = final_state
                final_state = AgentState(
                    prompt=state_dict.get("prompt", ""),
                    topic=state_dict.get("topic", ""),
                    outline=state_dict.get("outline", {}),
                    slide_count=state_dict.get("slide_count", 0),
                    research=state_dict.get("research", {}),
                    references=state_dict.get("references", []),
                    content=state_dict.get("content", {}),
                    slides=state_dict.get("slides", []),
                    visualizations=state_dict.get("visualizations", {}),
                    diagrams=state_dict.get("diagrams", []),
                    presentation=state_dict.get("presentation", {}),
                    presentation_path=state_dict.get("presentation_path", ""),
                    export=state_dict.get("export", {}),
                    export_paths=state_dict.get("export_paths", {}),
                    current_agent=state_dict.get("current_agent", ""),
                    errors=state_dict.get("errors", []),
                    status=state_dict.get("status", "pending"),
                    progress=state_dict.get("progress", 0)
                )
            
            if final_state.status == "completed":
                logger.info("Workflow completed successfully!")
            else:
                logger.warning(f"Workflow completed with errors: {final_state.errors}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            initial_state.status = "failed"
            initial_state.errors.append(str(e))
            return initial_state
    
    def get_state_summary(self, state: AgentState) -> Dict[str, Any]:
        '''Get a summary of the workflow state'''
        return {
            "status": state.status,
            "progress": state.progress,
            "current_agent": state.current_agent,
            "topic": state.topic,
            "slide_count": state.slide_count,
            "errors": state.errors,
            "presentation_path": state.presentation_path,
            "export_paths": state.export_paths
        }
