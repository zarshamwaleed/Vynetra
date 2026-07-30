import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:  # pragma: no cover - handled gracefully at runtime
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


class ManimMCPClient:
    """Small adapter for invoking the vendored Manim MCP server over stdio."""

    def __init__(self):
        self.backend_root = Path(__file__).resolve().parents[2]
        self.server_script = self.backend_root / "manim-mcp-server" / "src" / "manim_server.py"

    @property
    def available(self) -> bool:
        return bool(ClientSession and StdioServerParameters and stdio_client and self.server_script.exists())

    async def render_code(
        self,
        manim_code: str,
        scene_name: str,
        output_dir: Optional[str] = None,
        quality: str = "medium",
    ) -> Dict[str, Any]:
        if not self.available:
            raise RuntimeError("The MCP Python client or vendored Manim MCP server is unavailable.")

        env = {
            "MANIM_EXECUTABLE": os.getenv("MANIM_EXECUTABLE", "manim"),
        }

        server_params = StdioServerParameters(
            command="python",
            args=[str(self.server_script)],
            env=env,
        )

        arguments = {
            "manim_code": manim_code,
            "scene_name": scene_name,
            "quality": quality,
        }
        if output_dir:
            arguments["output_dir"] = output_dir

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("execute_manim_code", arguments=arguments)
                payload = self._extract_payload(result)

        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected response received from the Manim MCP server.")

        return payload

    def _extract_payload(self, result: Any) -> Dict[str, Any]:
        if result is None:
            return {}

        if hasattr(result, "content"):
            for item in result.content:
                if hasattr(item, "text"):
                    text = item.text
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"success": False, "message": text}

        if isinstance(result, dict):
            return result

        return {"success": False, "message": str(result)}
