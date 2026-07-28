import logging
from typing import List, Dict, Any, Optional, AsyncGenerator
from google import genai
from google.genai import types

from app.services.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM Provider using the new google-genai library"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model_name = config.get("model", "gemini-2.0-flash-exp")
        self.client = None
    
    async def initialize(self) -> None:
        if self._initialized:
            return
        
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        try:
            # Use the new google-genai client
            self.client = genai.Client(api_key=self.api_key)
            self._initialized = True
            logger.info(f"Gemini provider initialized with model: {self.model_name} using new API")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        if not self._initialized:
            await self.initialize()
        
        try:
            # Build the request
            contents = prompt
            if system_prompt:
                contents = f"{system_prompt}\n\n{prompt}"
            
            # Generate content using the new client
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            return LLMResponse(
                text=response.text,
                model=self.model_name,
                provider="gemini",
                usage={
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            )
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        if not self._initialized:
            await self.initialize()
        
        try:
            contents = prompt
            if system_prompt:
                contents = f"{system_prompt}\n\n{prompt}"
            
            # Stream using the new client
            async for chunk in await self.client.aio.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            ):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            raise
    
    async def embeddings(self, text: str, **kwargs) -> List[float]:
        raise NotImplementedError("Embeddings not directly supported")
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> LLMResponse:
        if not self._initialized:
            await self.initialize()
        
        try:
            # Build prompt from messages
            prompt = ""
            for msg in messages:
                if msg["role"] == "user":
                    prompt += f"User: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    prompt += f"Assistant: {msg['content']}\n"
                elif msg["role"] == "system":
                    prompt += f"System: {msg['content']}\n"
            
            return await self.generate(prompt, temperature=temperature, max_tokens=max_tokens, **kwargs)
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise
