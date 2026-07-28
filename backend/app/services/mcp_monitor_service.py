import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class MCPMonitorService:
    '''Service for monitoring MCP servers and their activity'''
    
    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = defaultdict(int)
    
    def register_server(self, name: str, url: str, capabilities: List[str]) -> None:
        '''Register an MCP server for monitoring'''
        self.servers[name] = {
            "name": name,
            "url": url,
            "capabilities": capabilities,
            "status": "registered",
            "tools": [],
            "last_heartbeat": datetime.now().isoformat(),
            "uptime": 0,
            "total_calls": 0,
            "avg_response_time": 0
        }
        logger.info(f"Server registered: {name}")
    
    def update_server_status(self, name: str, status: str) -> None:
        '''Update server status'''
        if name in self.servers:
            self.servers[name]["status"] = status
            self.servers[name]["last_heartbeat"] = datetime.now().isoformat()
    
    def add_tools(self, server_name: str, tools: List[Dict[str, Any]]) -> None:
        '''Add tools for a server'''
        if server_name in self.servers:
            self.servers[server_name]["tools"] = tools
            self.servers[server_name]["status"] = "discovered"
    
    def record_execution(
        self,
        server: str,
        tool: str,
        params: Dict[str, Any],
        response: Any,
        execution_time: float,
        success: bool = True
    ) -> None:
        '''Record a tool execution'''
        entry = {
            "id": len(self.execution_history) + 1,
            "server": server,
            "tool": tool,
            "params": params,
            "response": response,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.execution_history.append(entry)
        
        # Update metrics
        if server in self.servers:
            self.servers[server]["total_calls"] += 1
            current_avg = self.servers[server]["avg_response_time"]
            total_calls = self.servers[server]["total_calls"]
            self.servers[server]["avg_response_time"] = (
                (current_avg * (total_calls - 1) + execution_time) / total_calls
            )
        
        self.metrics["total_executions"] += 1
        self.metrics["successful_executions"] += 1 if success else 0
        self.metrics["failed_executions"] += 0 if success else 1
        
        logger.info(f"Execution recorded: {server}.{tool} ({execution_time:.3f}s)")
    
    def get_servers(self) -> List[Dict[str, Any]]:
        '''Get all registered servers'''
        return list(self.servers.values())
    
    def get_server(self, name: str) -> Optional[Dict[str, Any]]:
        '''Get a specific server'''
        return self.servers.get(name)
    
    def get_execution_history(
        self,
        limit: int = 100,
        server: Optional[str] = None,
        tool: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        '''Get execution history with filters'''
        history = self.execution_history
        
        if server:
            history = [h for h in history if h["server"] == server]
        if tool:
            history = [h for h in history if h["tool"] == tool]
        
        return history[-limit:]
    
    def get_metrics(self) -> Dict[str, Any]:
        '''Get aggregate metrics'''
        total_executions = self.metrics["total_executions"]
        successful = self.metrics["successful_executions"]
        failed = self.metrics["failed_executions"]
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": (
                (successful / total_executions * 100) if total_executions > 0 else 0
            ),
            "total_servers": len(self.servers),
            "servers": [
                {
                    "name": s["name"],
                    "status": s["status"],
                    "total_calls": s["total_calls"],
                    "avg_response_time": s["avg_response_time"],
                    "tools_count": len(s["tools"])
                }
                for s in self.servers.values()
            ]
        }
    
    def get_tools_summary(self) -> Dict[str, List[str]]:
        '''Get summary of all tools across servers'''
        summary = {}
        for server_name, server in self.servers.items():
            summary[server_name] = [t.get("name", "unknown") for t in server.get("tools", [])]
        return summary
    
    def clear_history(self) -> None:
        '''Clear execution history'''
        self.execution_history = []
        logger.info("Execution history cleared")

# Singleton instance
mcp_monitor = MCPMonitorService()
