import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import httpx

from app.services.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter LLM Provider"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "qwen/qwen-2.5-32b")
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = None
    
    async def initialize(self) -> None:
        """Initialize the OpenRouter client"""
        if self._initialized:
            return
        
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.client = httpx.AsyncClient(
            timeout=120.0,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": "Vynetra"
            }
        )
        self._initialized = True
        logger.info(f"OpenRouter provider initialized with model: {self.model}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate text using OpenRouter"""
        if not self._initialized:
            await self.initialize()
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data["choices"][0]["message"]["content"],
                model=self.model,
                provider="openrouter",
                usage={
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("total_tokens", 0)
                }
            )
        except Exception as e:
            logger.error(f"OpenRouter generation error: {e}")
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream text from OpenRouter"""
        if not self._initialized:
            await self.initialize()
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk.get("choices"):
                                delta = chunk["choices"][0].get("delta", {})
                                if delta.get("content"):
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"OpenRouter stream error: {e}")
            raise
    
    async def embeddings(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """Generate embeddings (not directly supported by OpenRouter)"""
        raise NotImplementedError("Embeddings are not directly supported by OpenRouter")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Chat with OpenRouter"""
        if not self._initialized:
            await self.initialize()
        
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data["choices"][0]["message"]["content"],
                model=self.model,
                provider="openrouter",
                usage={
                    "prompt_tokens": data.get("usage", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("usage", {}).get("completion_tokens", 0),
                    "total_tokens": data.get("usage", {}).get("total_tokens", 0)
                }
            )
        except Exception as e:
            logger.error(f"OpenRouter chat error: {e}")
            raise
