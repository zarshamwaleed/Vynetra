from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.services.mcp_monitor_service import mcp_monitor

router = APIRouter()

class ServerRegistration(BaseModel):
    name: str
    url: str
    capabilities: List[str]

class ToolExecution(BaseModel):
    server: str
    tool: str
    params: Dict[str, Any]
    response: Any
    execution_time: float
    success: bool = True

@router.get("/servers")
async def get_servers() -> List[Dict[str, Any]]:
    """Get all registered MCP servers"""
    return mcp_monitor.get_servers()

@router.get("/servers/{server_name}")
async def get_server(server_name: str) -> Dict[str, Any]:
    """Get a specific server by name"""
    server = mcp_monitor.get_server(server_name)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
    return server

@router.post("/servers/register")
async def register_server(registration: ServerRegistration) -> Dict[str, Any]:
    """Register a new MCP server"""
    mcp_monitor.register_server(
        registration.name,
        registration.url,
        registration.capabilities
    )
    return {"status": "registered", "server": registration.name}

@router.post("/servers/{server_name}/tools")
async def update_tools(server_name: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Update tools for a server"""
    mcp_monitor.add_tools(server_name, tools)
    return {"status": "updated", "server": server_name, "tools_count": len(tools)}

@router.post("/executions/record")
async def record_execution(execution: ToolExecution) -> Dict[str, Any]:
    """Record a tool execution"""
    mcp_monitor.record_execution(
        server=execution.server,
        tool=execution.tool,
        params=execution.params,
        response=execution.response,
        execution_time=execution.execution_time,
        success=execution.success
    )
    return {"status": "recorded"}

@router.get("/executions")
async def get_executions(
    limit: int = Query(100, ge=1, le=1000),
    server: Optional[str] = None,
    tool: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Get execution history"""
    return mcp_monitor.get_execution_history(limit=limit, server=server, tool=tool)

@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """Get aggregate metrics"""
    return mcp_monitor.get_metrics()

@router.get("/tools")
async def get_tools_summary() -> Dict[str, List[str]]:
    """Get summary of all tools"""
    return mcp_monitor.get_tools_summary()

@router.delete("/history")
async def clear_history() -> Dict[str, Any]:
    """Clear execution history"""
    mcp_monitor.clear_history()
    return {"status": "cleared"}
