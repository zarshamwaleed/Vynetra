from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    provider: Optional[str] = "groq"
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096

class GenerateResponse(BaseModel):
    text: str
    provider: str
    model: str
    usage: Dict[str, int]

@router.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """Generate text using the LLM service"""
    # This is a placeholder - in production, this would call the actual LLM service
    return GenerateResponse(
        text=f"Generated response for: {request.prompt[:50]}...",
        provider=request.provider,
        model="llama-3.3-70b-versatile",
        usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    )

@router.get("/providers")
async def list_providers():
    """List available LLM providers"""
    return {
        "providers": [
            {"name": "groq", "description": "Groq Cloud - Fast inference", "available": True},
            {"name": "gemini", "description": "Google Gemini AI", "available": False},
            {"name": "openrouter", "description": "OpenRouter - Multiple models", "available": False},
            {"name": "ollama", "description": "Ollama - Local models", "available": False}
        ],
        "default": "groq"
    }
