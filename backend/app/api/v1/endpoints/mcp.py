from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/servers")
async def list_mcp_servers() -> List[Dict[str, Any]]:
    """List all MCP servers"""
    return [
        {
            "name": "filesystem",
            "status": "registered",
            "type": "external",
            "capabilities": ["read", "write", "create", "delete", "list"]
        },
        {
            "name": "manim",
            "status": "registered",
            "type": "external",
            "capabilities": ["generate", "render", "animate"]
        },
        {
            "name": "browser",
            "status": "registered",
            "type": "external",
            "capabilities": ["search", "navigate", "scrape", "screenshot"]
        }
    ]

@router.get("/history")
async def get_mcp_history() -> List[Dict[str, Any]]:
    """Get MCP execution history"""
    return []

@router.get("/health")
async def health_check() -> Dict[str, bool]:
    """Check health of MCP servers"""
    return {
        "filesystem": True,
        "manim": True,
        "browser": True
    }
