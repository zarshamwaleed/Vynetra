import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from enum import Enum

from app.services.llm.base import BaseLLMProvider, LLMResponse
from app.services.llm.groq_provider import GroqProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openrouter_provider import OpenRouterProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProviderType(str, Enum):
    GROQ = "groq"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"

class LLMService:
    def __init__(
        self,
        provider: str = "groq",
        config: Optional[Dict[str, Any]] = None
    ):
        self.provider_type = provider.lower()
        self.config = config or {}
        self._provider: Optional[BaseLLMProvider] = None
        self._initialized = False
    
    async def _get_provider(self) -> BaseLLMProvider:
        if self._provider and self._initialized:
            return self._provider
        
        provider_config = self._build_config()
        
        providers = {
            LLMProviderType.GROQ: GroqProvider,
            LLMProviderType.GEMINI: GeminiProvider,
            LLMProviderType.OLLAMA: OllamaProvider,
            LLMProviderType.OPENROUTER: OpenRouterProvider
        }
        
        provider_class = providers.get(self.provider_type)
        if not provider_class:
            raise ValueError(f"Unsupported provider: {self.provider_type}")
        
        self._provider = provider_class(provider_config)
        await self._provider.initialize()
        self._initialized = True
        
        logger.info(f"LLM Service initialized with provider: {self.provider_type}")
        return self._provider
    
    def _build_config(self) -> Dict[str, Any]:
        if self.provider_type == LLMProviderType.GROQ:
            return {
                "api_key": self.config.get("api_key") or settings.GROQ_API_KEY,
                "model": self.config.get("model") or settings.GROQ_MODEL
            }
        elif self.provider_type == LLMProviderType.GEMINI:
            return {
                "api_key": self.config.get("api_key") or settings.GOOGLE_API_KEY,
                "model": self.config.get("model") or settings.GEMINI_MODEL
            }
        elif self.provider_type == LLMProviderType.OLLAMA:
            return {
                "base_url": self.config.get("base_url") or settings.OLLAMA_BASE_URL,
                "model": self.config.get("model") or settings.OLLAMA_MODEL
            }
        elif self.provider_type == LLMProviderType.OPENROUTER:
            return {
                "api_key": self.config.get("api_key") or settings.OPENROUTER_API_KEY,
                "model": self.config.get("model") or settings.OPENROUTER_MODEL
            }
        else:
            return {}
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        provider = await self._get_provider()
        return await provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        provider = await self._get_provider()
        async for chunk in provider.stream(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ):
            yield chunk
    
    async def embeddings(
        self,
        text: str,
        **kwargs
    ) -> List[float]:
        provider = await self._get_provider()
        return await provider.embeddings(text=text, **kwargs)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        provider = await self._get_provider()
        return await provider.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    @classmethod
    async def create(
        cls,
        provider: str = "groq",
        config: Optional[Dict[str, Any]] = None
    ) -> "LLMService":
        service = cls(provider=provider, config=config)
        await service._get_provider()
        return service
