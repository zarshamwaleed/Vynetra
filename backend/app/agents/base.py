from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from app.agents.state import AgentState

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    '''Base class for all agents'''
    
    def __init__(self, name: str, llm_service):
        self.name = name
        self.llm = llm_service
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    @abstractmethod
    async def process(self, state: AgentState) -> AgentState:
        '''Process the current state and return updated state'''
        pass
    
    async def _log_step(self, state: AgentState, message: str):
        '''Log a step and update state'''
        state.current_agent = self.name
        self.logger.info(f"[{self.name}] {message}")
    
    async def _add_error(self, state: AgentState, error: str):
        '''Add an error to the state'''
        state.errors.append(f"{self.name}: {error}")
        state.status = "failed"
        self.logger.error(f"[{self.name}] {error}")
