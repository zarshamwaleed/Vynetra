from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass

@dataclass
class LLMResponse:
    """Response from LLM"""
    text: str
    model: str
    provider: str
    usage: Dict[str, int]  # tokens, etc.
    metadata: Optional[Dict[str, Any]] = None

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider (API keys, clients, etc.)"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate text from the LLM"""
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream text from the LLM"""
        pass
    
    @abstractmethod
    async def embeddings(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """Generate embeddings for text"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Chat with the LLM using a message history"""
        pass
