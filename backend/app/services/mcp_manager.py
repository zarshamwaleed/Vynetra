class MCPManager:
    def __init__(self):
        self.servers = {}
        self._initialized = False
    
    async def start_all(self):
        if not self._initialized:
            self.servers = {"filesystem": {"status": "running"}, "manim": {"status": "running"}}
            self._initialized = True
    
    async def stop_all(self):
        self._initialized = False
    
    async def health_check(self):
        return {name: info["status"] == "running" for name, info in self.servers.items()}

mcp_manager = MCPManager()
