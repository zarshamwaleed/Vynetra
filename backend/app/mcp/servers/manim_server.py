import json
import logging
import subprocess
import tempfile
import os
import shutil
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

logger = logging.getLogger(__name__)

app = FastAPI(title="Simple Manim MCP Server", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory
OUTPUT_DIR = Path("./generated/animations")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": "generate_animation",
                "description": "Generate a Manim animation from Python code",
                "parameters": {
                    "code": {"type": "string", "required": True, "description": "Manim Python code"},
                    "scene_name": {"type": "string", "default": "SquareToCircle", "description": "Scene class name"},
                    "output_dir": {"type": "string", "default": "./generated/animations", "description": "Output directory"}
                }
            },
            {
                "name": "render_animation",
                "description": "Render a Manim animation from a script file",
                "parameters": {
                    "script_path": {"type": "string", "required": True, "description": "Path to the Manim script"}
                }
            }
        ]
    }

@app.post("/call/generate_animation")
async def call_generate_animation(params: Dict[str, Any]):
    try:
        code = params.get("code", "")
        scene_name = params.get("scene_name", "SquareToCircle")
        output_dir = params.get("output_dir", "./generated/animations")
        
        if not code:
            return {
                "success": False,
                "error": "Code parameter is required"
            }
        
        # Create temp file with the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(code)
            script_path = f.name
        
        # Create output directory
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Run manim
        try:
            result = subprocess.run(
                ["manim", "-p", "-ql", script_path, scene_name],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.getcwd()
            )
            
            success = result.returncode == 0
            
            # Find the generated video
            video_files = []
            media_dir = Path("./media")
            if media_dir.exists():
                for video in media_dir.rglob("*.mp4"):
                    video_files.append(str(video))
            
            return {
                "success": success,
                "result": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "video_files": video_files,
                    "output_dir": output_dir
                }
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Manim execution timed out (60 seconds)"
            }
        finally:
            # Clean up temp file
            try:
                os.unlink(script_path)
            except:
                pass
            
    except Exception as e:
        logger.error(f"Error generating animation: {e}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/call/render_animation")
async def call_render_animation(params: Dict[str, Any]):
    try:
        script_path = params.get("script_path")
        if not script_path:
            return {
                "success": False,
                "error": "script_path parameter is required"
            }
        
        if not Path(script_path).exists():
            return {
                "success": False,
                "error": f"Script file not found: {script_path}"
            }
        
        # Run manim
        result = subprocess.run(
            ["manim", "-p", "-ql", script_path],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=os.getcwd()
        )
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "result": {
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Manim execution timed out (60 seconds)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/health")
async def health():
    return {"status": "healthy", "manim_installed": shutil.which("manim") is not None}

@app.get("/")
async def root():
    return {
        "name": "Simple Manim MCP Server",
        "version": "1.0.0",
        "status": "running",
        "manim_installed": shutil.which("manim") is not None
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Manim MCP Server...")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    uvicorn.run(app, host="0.0.0.0", port=8002)
