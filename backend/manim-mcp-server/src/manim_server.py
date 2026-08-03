import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Vynetra Manim Server")

MANIM_EXECUTABLE = os.getenv("MANIM_EXECUTABLE", "manim")
BASE_DIR = Path(__file__).resolve().parent / "media"
BASE_DIR.mkdir(parents=True, exist_ok=True)


def _quality_flag(quality: str) -> str:
    quality = (quality or "medium").lower()
    return {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
    }.get(quality, "-qm")


def _find_rendered_videos(render_dir: Path) -> list[str]:
    return sorted(str(path.resolve()) for path in render_dir.rglob("*.mp4"))


@mcp.tool()
def execute_manim_code(
    manim_code: str,
    scene_name: str = "Scene",
    output_dir: str = "",
    quality: str = "medium",
) -> str:
    """Execute Manim code and return JSON describing generated video files."""
    target_root = Path(output_dir).resolve() if output_dir else BASE_DIR / "manim_tmp"
    target_root.mkdir(parents=True, exist_ok=True)
    render_dir = target_root / f"{scene_name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
    render_dir.mkdir(parents=True, exist_ok=True)
    script_path = render_dir / "scene.py"

    try:
        with open(script_path, "w", encoding="utf-8") as script_file:
            script_file.write(manim_code)

        result = subprocess.run(
            [
                MANIM_EXECUTABLE,
                _quality_flag(quality),
                "--disable_caching",
                str(script_path),
            ],
            capture_output=True,
            text=True,
            cwd=render_dir,
        )

        video_files = _find_rendered_videos(render_dir)
        success = result.returncode == 0 and bool(video_files)

        return json.dumps(
            {
                "success": success,
                "scene_name": scene_name,
                "render_dir": str(render_dir.resolve()),
                "video_files": video_files,
                "stdout": result.stdout[-4000:],
                "stderr": result.stderr[-4000:],
            }
        )
    except Exception as exc:
        return json.dumps(
            {
                "success": False,
                "scene_name": scene_name,
                "render_dir": str(render_dir.resolve()),
                "video_files": [],
                "stdout": "",
                "stderr": str(exc),
            }
        )


@mcp.tool()
def cleanup_manim_temp_dir(directory: str) -> str:
    """Clean up the specified Manim temporary directory after execution."""
    try:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            return json.dumps({"success": True, "directory": directory})
        return json.dumps({"success": False, "directory": directory, "error": "Directory not found"})
    except Exception as exc:
        return json.dumps({"success": False, "directory": directory, "error": str(exc)})


if __name__ == "__main__":
    mcp.run(transport="stdio")




