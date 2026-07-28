from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.settings_service import settings_service

router = APIRouter()

class SettingsUpdate(BaseModel):
    llm_provider: Optional[str] = None
    llm_model: Optional[Dict[str, str]] = None
    theme: Optional[str] = None
    slide_count: Optional[int] = None
    audience: Optional[str] = None
    tone: Optional[str] = None
    animation_quality: Optional[str] = None
    auto_save: Optional[bool] = None
    show_timeline: Optional[bool] = None
    enable_animations: Optional[bool] = None
    enable_diagrams: Optional[bool] = None

@router.get("/")
async def get_settings() -> Dict[str, Any]:
    """Get all settings"""
    return settings_service.get_settings()

@router.get("/{key}")
async def get_setting(key: str) -> Dict[str, Any]:
    """Get a specific setting"""
    value = settings_service.get_setting(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return {key: value}

@router.post("/")
async def update_settings(updates: SettingsUpdate) -> Dict[str, Any]:
    """Update settings"""
    # Convert to dict, removing None values
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    if not update_dict:
        raise HTTPException(status_code=400, detail="No valid settings to update")
    
    result = settings_service.update_settings(update_dict)
    return {"status": "success", "settings": result}

@router.post("/reset")
async def reset_settings() -> Dict[str, Any]:
    """Reset settings to defaults"""
    result = settings_service.reset_settings()
    return {"status": "success", "settings": result}

@router.get("/available/providers")
async def get_available_providers() -> Dict[str, Any]:
    """Get available LLM providers with their models"""
    return {
        "providers": [
            {
                "name": "groq",
                "label": "Groq Cloud",
                "description": "Fast inference with free tier",
                "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768", "gemma2-9b-it"],
                "available": True
            },
            {
                "name": "gemini",
                "label": "Google Gemini",
                "description": "Google's latest models",
                "models": ["models/gemini-2.5-flash", "models/gemini-2.0-flash"],
                "available": True
            },
            {
                "name": "openrouter",
                "label": "OpenRouter",
                "description": "Access to multiple models",
                "models": ["qwen/qwen-2.5-32b:free", "meta-llama/llama-3.3-70b-instruct:free"],
                "available": True
            },
            {
                "name": "ollama",
                "label": "Ollama (Local)",
                "description": "Run models locally",
                "models": ["tinyllama", "qwen3:8b", "llama3.2"],
                "available": True
            }
        ]
    }
