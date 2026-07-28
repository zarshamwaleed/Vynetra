import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import httpx

from app.services.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

class OllamaProvider(BaseLLMProvider):
    """Ollama LLM Provider (Local)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "qwen3:8b")
        self.client = None
    
    async def initialize(self) -> None:
        """Initialize the Ollama client"""
        if self._initialized:
            return
        
        self.client = httpx.AsyncClient(timeout=120.0)
        self._initialized = True
        logger.info(f"Ollama provider initialized with model: {self.model} at {self.base_url}")
    
    async def _check_ollama(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Generate text using Ollama"""
        if not self._initialized:
            await self.initialize()
        
        if not await self._check_ollama():
            raise ConnectionError("Ollama is not running. Please start Ollama first.")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt if system_prompt else "",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data.get("response", ""),
                model=self.model,
                provider="ollama",
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                },
                metadata=data
            )
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream text from Ollama"""
        if not self._initialized:
            await self.initialize()
        
        if not await self._check_ollama():
            raise ConnectionError("Ollama is not running. Please start Ollama first.")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt if system_prompt else "",
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
                **kwargs
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        data = json.loads(line)
                        if data.get("response"):
                            yield data["response"]
                        if data.get("done", False):
                            break
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            raise
    
    async def embeddings(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        """Generate embeddings using Ollama"""
        if not self._initialized:
            await self.initialize()
        
        if not await self._check_ollama():
            raise ConnectionError("Ollama is not running. Please start Ollama first.")
        
        try:
            payload = {
                "model": self.model,
                "prompt": text,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("embedding", [])
        except Exception as e:
            logger.error(f"Ollama embeddings error: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        """Chat with Ollama using message history"""
        if not self._initialized:
            await self.initialize()
        
        if not await self._check_ollama():
            raise ConnectionError("Ollama is not running. Please start Ollama first.")
        
        try:
            # Convert messages to Ollama format
            formatted_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    formatted_messages.append({"role": "system", "content": msg["content"]})
                elif msg["role"] == "user":
                    formatted_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    formatted_messages.append({"role": "assistant", "content": msg["content"]})
            
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data.get("message", {}).get("content", ""),
                model=self.model,
                provider="ollama",
                usage={
                    "prompt_tokens": data.get("prompt_eval_count", 0),
                    "completion_tokens": data.get("eval_count", 0),
                    "total_tokens": data.get("prompt_eval_count", 0) + data.get("eval_count", 0)
                }
            )
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
