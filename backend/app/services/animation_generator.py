import json
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from app.core.config import settings
from app.services.asset_policy import select_animation_focus, should_generate_animation
from app.services.llm import LLMService
from app.services.manim_mcp_client import ManimMCPClient

logger = logging.getLogger(__name__)


class AnimationGenerator:
    """Generate educational animations only for topics that benefit from visual explanation."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.mcp = ManimMCPClient()

    async def generate_animation(self, job_id: str, topic: str, slides: List[Dict]) -> Optional[Dict]:
        """Generate a Manim animation through the vendored MCP server."""
        try:
            eligible, reason = should_generate_animation(topic, slides)
            if not eligible:
                logger.info("Skipping animation for '%s': %s", topic, reason)
                return None

            if not self.mcp.available:
                logger.warning("Skipping animation because the Manim MCP client is unavailable.")
                return None

            focus = select_animation_focus(topic, slides)
            plan = await self._build_animation_plan(topic, focus, slides)
            if not plan:
                return None

            if not self._is_high_quality_script(plan["code"]):
                logger.warning("Rejected low-quality animation script for '%s'", topic)
                return None

            output_dir = Path(settings.STORAGE_PATH).resolve() / "presentations" / job_id / "animations"
            output_dir.mkdir(parents=True, exist_ok=True)

            render_result = await self.mcp.render_code(
                manim_code=plan["code"],
                scene_name=plan["scene_name"],
                output_dir=str(output_dir),
                quality="medium",
            )

            if not render_result.get("success"):
                logger.warning("Manim MCP render failed: %s", render_result.get("stderr", "unknown error"))
                return None

            video_files = render_result.get("video_files", [])
            if not video_files:
                return None

            final_video_path = self._persist_video(job_id, Path(video_files[0]))
            if not final_video_path:
                return None

            return {
                "title": plan["title"],
                "description": plan["description"],
                "focus": focus,
                "video_path": final_video_path,
                "code": plan["code"],
                "scene_name": plan["scene_name"],
            }
        except Exception as e:
            logger.error(f"Error generating animation: {e}")
            return None

    async def _build_animation_plan(self, topic: str, focus: str, slides: List[Dict]) -> Optional[Dict]:
        slide_summary = []
        for slide in slides[:5]:
            bullets = ", ".join(slide.get("bullet_points", [])[:4])
            slide_summary.append(
                {
                    "title": slide.get("title", ""),
                    "content": slide.get("content", ""),
                    "bullets": bullets,
                }
            )

        system_prompt = f"""You create educational Manim scenes for Vynetra.

Return ONLY valid JSON with this structure:
{{
  "title": "Short animation title",
  "description": "What the animation visually teaches",
  "scene_name": "SceneClassName",
  "code": "full executable Manim Python code"
}}

Rules:
- Build a visual explanation for the topic "{topic}" with focus "{focus}".
- Use geometry, axes, vectors, graphs, arrows, matrices, nodes, highlights, or motion to teach the concept.
- Text must be minimal and supportive only.
- Do not create heading-only or text-only animations.
- Do not use pure title cards, bullet lists, or sequences of Write(Text(...)).
- Keep the animation self-contained with one scene class.
- The code must import from manim and render successfully on its own.
"""

        response = await self.llm.generate(
            prompt=f"Create a Manim animation plan for {focus}. Slides: {json.dumps(slide_summary)}",
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=2600,
        )

        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if not match:
            return None

        try:
            parsed = json.loads(match.group())
        except json.JSONDecodeError:
            return None

        if not parsed.get("code") or not parsed.get("scene_name"):
            return None

        return parsed

    def _is_high_quality_script(self, code: str) -> bool:
        normalized = code or ""
        lowered = normalized.lower()

        if "from manim import" not in lowered:
            return False

        text_constructs = len(re.findall(r"\b(text|title|markuptext)\s*\(", normalized, re.IGNORECASE))
        text_only_plays = len(
            re.findall(
                r"(Write|FadeIn|Create)\s*\(\s*(Text|Title|MarkupText)\s*\(",
                normalized,
                re.IGNORECASE,
            )
        )
        visual_constructs = len(
            re.findall(
                r"\b(Axes|NumberPlane|Circle|Square|Rectangle|Arrow|Vector|Dot|Line|Matrix|BarChart|VGroup|Graph|FunctionGraph|Polygon)\b",
                normalized,
            )
        )

        if text_only_plays > 0 and visual_constructs < 2:
            return False

        if text_constructs > max(3, visual_constructs):
            return False

        return visual_constructs >= 2

    def _persist_video(self, job_id: str, source_path: Path) -> Optional[str]:
        if not source_path.exists():
            return None

        target_dir = Path(settings.STORAGE_PATH).resolve() / "presentations" / job_id / "animations"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{source_path.stem}.mp4"
        shutil.copy2(source_path, target_path)
        return str(target_path.resolve())
