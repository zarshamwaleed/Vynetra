import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import json

from groq import AsyncGroq
from app.services.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

class GroqProvider(BaseLLMProvider):
    """Groq LLM Provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "qwen-2.5-32b")
        self.client = None
    
    async def initialize(self) -> None:
        """Initialize the Groq client"""
        if self._initialized:
            return
        
        if not self.api_key:
            raise ValueError("Groq API key is required")
        
        self.client = AsyncGroq(api_key=self.api_key)
        self._initialized = True
        logger.info(f"Groq provider initialized with model: {self.model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Groq"""
        if not self._initialized:
            await self.initialize()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                text=response.choices[0].message.content,
                model=self.model,
                provider="groq",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream text from Groq"""
        if not self._initialized:
            await self.initialize()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"Groq stream error: {e}")
            raise
    
    async def embeddings(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """Generate embeddings (not directly supported by Groq)"""
        raise NotImplementedError("Embeddings are not directly supported by Groq")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Chat with Groq"""
        if not self._initialized:
            await self.initialize()
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return LLMResponse(
                text=response.choices[0].message.content,
                model=self.model,
                provider="groq",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            )
        except Exception as e:
            logger.error(f"Groq chat error: {e}")
            raise
