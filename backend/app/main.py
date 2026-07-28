import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.database import init_db
from app.api.v1.api import api_router
from app.services.mcp_monitor_service import mcp_monitor

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Vynetra...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    # Register default MCP servers for monitoring
    mcp_monitor.register_server(
        "filesystem",
        "http://localhost:8001",
        ["read", "write", "create", "delete", "list"]
    )
    mcp_monitor.register_server(
        "manim",
        "http://localhost:8002",
        ["generate", "render", "animate"]
    )
    mcp_monitor.register_server(
        "browser",
        "http://localhost:8005",
        ["search", "navigate", "scrape", "screenshot"]
    )
    logger.info("✅ MCP servers registered for monitoring")
    
    yield
    
    logger.info("Shutting down Vynetra...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="AI Presentation Creator using Multi-Agent AI & MCP",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "status": "running",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "ok",
            "database": "ok",
        }
    }
