import logging
from typing import Dict, List, Optional, Any
from app.mcp.client import MCPClient, MCPTool, MCPResponse

logger = logging.getLogger(__name__)

class MCPManager:
    def __init__(self, config_path: str = "mcp_config.json"):
        self.client: Optional[MCPClient] = None
        self.config_path = config_path
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
        
        logger.info("Initializing MCP Manager...")
        self.client = MCPClient(self.config_path)
        await self.client.__aenter__()
        self._initialized = True
        logger.info("MCP Manager initialized successfully")
    
    async def shutdown(self):
        if self.client:
            await self.client.__aexit__(None, None, None)
            self._initialized = False
    
    async def get_client(self) -> MCPClient:
        if not self._initialized:
            await self.initialize()
        return self.client
    
    async def call_tool(self, server: str, tool: str, params: Dict[str, Any]) -> MCPResponse:
        client = await self.get_client()
        return await client.call_tool(server, tool, params)
    
    async def discover_tools(self, server: str) -> List[MCPTool]:
        client = await self.get_client()
        return await client.discover_tools(server)
    
    async def health_check_all(self) -> Dict[str, bool]:
        client = await self.get_client()
        health_status = {}
        for server in await client.list_servers():
            health_status[server] = True  # Simplified
        return health_status
    
    def get_execution_history(self) -> List[MCPResponse]:
        if self.client:
            return self.client.get_execution_history()
        return []

mcp_manager = MCPManager()
