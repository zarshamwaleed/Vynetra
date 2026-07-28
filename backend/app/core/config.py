from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import os
from pathlib import Path

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    PROJECT_NAME: str = "Vynetra"
    PROJECT_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    BACKEND_PORT: int = 8000
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production-12345", min_length=32)
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/vynetra"
    REDIS_URL: str = "redis://redis:6379/0"
    
    # LLM Configuration
    LLM_PROVIDER: str = "GROQ"
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GOOGLE_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "models/gemini-2.5-flash"  # Working model!
    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: str = "qwen/qwen-2.5-32b:free"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "tinyllama"
    
    # MCP Servers
    MCP_FILESYSTEM_PORT: int = 8001
    MCP_MANIM_PORT: int = 8002
    MCP_POWERPOINT_PORT: int = 8003
    MCP_PDF_PORT: int = 8004
    MCP_BROWSER_PORT: int = 8005
    
    STORAGE_PATH: str = "./generated"
    LOG_LEVEL: str = "INFO"
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

def load_env():
    env_paths = [
        Path(".env"),
        Path("../.env"),
        Path("D:/Vynetra/.env"),
        Path("D:/Vynetra/backend/.env")
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            print(f"✅ Loading .env from: {env_path}")
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' not in line:
                        continue
                    try:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
                    except ValueError:
                        continue
            break

load_env()
settings = Settings()
