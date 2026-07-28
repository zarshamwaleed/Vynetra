from fastapi import APIRouter
from app.api.v1.endpoints import health, presentations, mcp, mcp_monitor, llm, timeline, history, settings

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(presentations.router, prefix="/presentations", tags=["presentations"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(mcp_monitor.router, prefix="/mcp-monitor", tags=["mcp-monitor"])
api_router.include_router(llm.router, prefix="/llm", tags=["llm"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["timeline"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
