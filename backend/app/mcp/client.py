import asyncio
import json
import logging
import subprocess
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import httpx
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    name: str
    description: str
    parameters: Dict[str, Any]
    server: str

@dataclass
class MCPRequest:
    server: str
    tool: str
    params: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class MCPResponse:
    request: MCPRequest
    result: Any
    execution_time: float
    error: Optional[str] = None
    success: bool = True

class MCPClient:
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, List[MCPTool]] = {}
        self.execution_history: List[MCPResponse] = []
        self._client = httpx.AsyncClient(timeout=60.0)
        self._processes: Dict[str, subprocess.Popen] = {}
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict:
        # Try multiple locations
        possible_paths = [
            config_path,
            "mcp_config.json",
            "../mcp_config.json",
            "./mcp_config.json"
        ]
        
        for path in possible_paths:
            if path and Path(path).exists():
                try:
                    with open(path) as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in {path}, using default config")
                    break
                except Exception as e:
                    logger.warning(f"Error loading {path}: {e}")
                    break
        
        # Default configuration
        logger.info("Using default MCP configuration")
        return {
            "mcpServers": {
                "filesystem": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "./generated"],
                    "enabled": True,
                    "type": "external",
                    "capabilities": ["read", "write", "create", "delete", "list"]
                },
                "browser": {
                    "command": "npx",
                    "args": ["-y", "mcpbrowser@latest"],
                    "enabled": True,
                    "type": "external",
                    "capabilities": ["search", "navigate", "scrape", "screenshot"]
                },
                "manim": {
                    "command": "python",
                    "args": [],
                    "enabled": False,
                    "type": "external",
                    "capabilities": ["generate", "render", "animate"]
                },
                "presentation": {
                    "command": "python",
                    "args": [],
                    "enabled": True,
                    "type": "custom",
                    "capabilities": ["create_outline", "create_slide", "export_ppt"]
                }
            }
        }
    
    async def __aenter__(self):
        await self.start_all_servers()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_all_servers()
        await self._client.aclose()
    
    async def start_all_servers(self):
        """Start all enabled MCP servers"""
        logger.info("Starting all MCP servers...")
        
        for server_name, config in self.config.get("mcpServers", {}).items():
            if config.get("enabled", True):
                await self.start_server(server_name, config)
        
        logger.info("All MCP servers started")
    
    async def start_server(self, server_name: str, config: Dict):
        """Start a specific MCP server"""
        try:
            logger.info(f"Starting MCP server: {server_name}")
            
            # For external servers, we'll use subprocess
            if config.get("type") == "external" and config.get("command"):
                env = os.environ.copy()
                env.update(config.get("env", {}))
                
                process = subprocess.Popen(
                    [config["command"]] + config.get("args", []),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                self._processes[server_name] = process
                
                # Register server
                self.servers[server_name] = {
                    "name": server_name,
                    "status": "running",
                    "type": config.get("type"),
                    "capabilities": config.get("capabilities", ["*"])
                }
                
                logger.info(f"MCP server {server_name} started successfully")
            else:
                # Custom servers or servers without command
                self.servers[server_name] = {
                    "name": server_name,
                    "status": "ready",
                    "type": config.get("type", "custom"),
                    "capabilities": config.get("capabilities", ["*"])
                }
                
        except Exception as e:
            logger.error(f"Failed to start MCP server {server_name}: {e}")
            self.servers[server_name] = {
                "name": server_name,
                "status": "error",
                "error": str(e),
                "type": config.get("type", "unknown")
            }
    
    async def stop_all_servers(self):
        """Stop all running MCP servers"""
        logger.info("Stopping all MCP servers...")
        
        for server_name, process in self._processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped MCP server: {server_name}")
            except Exception as e:
                logger.warning(f"Error stopping {server_name}: {e}")
                process.kill()
        
        self._processes.clear()
    
    async def discover_tools(self, server_name: str) -> List[MCPTool]:
        """Discover available tools on an MCP server"""
        if server_name not in self.servers:
            raise ValueError(f"Unknown MCP server: {server_name}")
        
        server = self.servers[server_name]
        
        # For now, return tools from capabilities
        tools = []
        for cap in server.get("capabilities", []):
            tools.append(MCPTool(
                name=cap,
                description=f"Tool: {cap}",
                parameters={},
                server=server_name
            ))
        
        self.tools[server_name] = tools
        server["tools"] = tools
        server["status"] = "discovered"
        
        logger.info(f"Discovered {len(tools)} tools on {server_name}")
        return tools
    
    async def call_tool(self, server: str, tool: str, params: Dict[str, Any]) -> MCPResponse:
        """Call a tool on an MCP server"""
        if server not in self.servers:
            raise ValueError(f"Unknown MCP server: {server}")
        
        request = MCPRequest(server=server, tool=tool, params=params)
        start_time = datetime.now()
        
        try:
            # Execute the tool
            result = await self._execute_tool(server, tool, params)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            response = MCPResponse(
                request=request,
                result=result,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            response = MCPResponse(
                request=request,
                result=None,
                execution_time=execution_time,
                error=str(e),
                success=False
            )
        
        self.execution_history.append(response)
        logger.info(f"MCP Call: {server}.{tool} - {response.execution_time:.2f}s")
        
        return response
    
    async def _execute_tool(self, server: str, tool: str, params: Dict[str, Any]) -> Any:
        """Execute a tool"""
        # For now, return simulated results
        if server == "filesystem":
            return await self._filesystem_tool(tool, params)
        elif server == "browser":
            return await self._browser_tool(tool, params)
        elif server == "manim":
            return await self._manim_tool(tool, params)
        elif server == "presentation":
            return await self._presentation_tool(tool, params)
        else:
            return {"message": f"Tool {tool} executed on {server}", "params": params}
    
    async def _filesystem_tool(self, tool: str, params: Dict) -> Any:
        """Execute filesystem tools"""
        if tool == "list" or tool == "list_files":
            path = params.get("path", ".")
            return {"files": ["file1.txt", "file2.txt", "folder/"], "path": path}
        elif tool == "read" or tool == "read_file":
            path = params.get("path")
            return {"content": f"Content of {path}", "path": path}
        elif tool == "write" or tool == "write_file":
            path = params.get("path")
            content = params.get("content", "")
            return {"success": True, "path": path, "size": len(content)}
        else:
            return {"message": f"Filesystem tool {tool} executed"}
    
    async def _browser_tool(self, tool: str, params: Dict) -> Any:
        """Execute browser tools"""
        if tool == "navigate":
            url = params.get("url")
            return {"page_title": f"Title of {url}", "url": url}
        elif tool == "search":
            query = params.get("query")
            return {"results": [{"title": f"Result 1 for {query}", "url": "http://example.com"}]}
        elif tool == "scrape":
            url = params.get("url")
            return {"content": f"Scraped content from {url}"}
        else:
            return {"message": f"Browser tool {tool} executed"}
    
    async def _manim_tool(self, tool: str, params: Dict) -> Any:
        """Execute manim tools"""
        if tool == "generate":
            code = params.get("code", "")
            return {"video_file": "output.mp4", "success": True, "code_length": len(code)}
        elif tool == "render":
            script_path = params.get("script_path")
            return {"video_file": "rendered.mp4", "success": True}
        else:
            return {"message": f"Manim tool {tool} executed"}
    
    async def _presentation_tool(self, tool: str, params: Dict) -> Any:
        """Execute presentation tools"""
        if tool == "create_outline":
            topic = params.get("topic", "AI")
            slide_count = params.get("slide_count", 10)
            return {
                "title": f"Presentation on {topic}",
                "slides": [
                    {"number": i+1, "title": f"Slide {i+1}"}
                    for i in range(slide_count)
                ]
            }
        elif tool == "create_slide":
            title = params.get("title", "Untitled")
            content = params.get("content", "")
            return {
                "title": title,
                "content": content,
                "bullets": content.split("\n") if content else []
            }
        elif tool == "export_ppt":
            slides = params.get("slides", [])
            filename = params.get("filename", "presentation")
            return {
                "file": f"{filename}.pptx",
                "slide_count": len(slides)
            }
        else:
            return {"message": f"Presentation tool {tool} executed"}
    
    async def list_servers(self) -> List[str]:
        return list(self.servers.keys())
    
    async def get_server_status(self, server: str) -> Dict[str, Any]:
        if server not in self.servers:
            raise ValueError(f"Unknown MCP server: {server}")
        return self.servers[server]
    
    def get_execution_history(self) -> List[MCPResponse]:
        return self.execution_history
    
    def clear_history(self):
        self.execution_history.clear()
