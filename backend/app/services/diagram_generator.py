import json
import logging
import math
import re
import textwrap
from pathlib import Path
from typing import Dict, List, Optional

from PIL import Image, ImageDraw, ImageFont

from app.core.config import settings
from app.services.asset_policy import select_diagram_candidate_slides
from app.services.llm import LLMService

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Generate actual presentation diagrams only when they improve understanding."""

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    async def generate_diagrams(self, job_id: str, topic: str, slides: List[Dict]) -> List[Dict]:
        diagrams: List[Dict] = []
        candidates = select_diagram_candidate_slides(topic, slides, limit=2)

        for index, slide in enumerate(candidates, start=1):
            spec = await self._build_diagram_spec(topic, slide)
            if not spec:
                spec = self._fallback_spec_from_slide(slide)
            if not spec:
                continue

            image_path = self._render_diagram(job_id, index, spec)
            if not image_path:
                continue

            diagrams.append(
                {
                    "title": spec["title"],
                    "type": spec["diagram_type"],
                    "description": spec["description"],
                    "slide_number": slide.get("number"),
                    "image_path": image_path,
                    "nodes": spec["nodes"],
                    "edges": spec["edges"],
                    "layout": spec["layout"],
                }
            )

        return diagrams

    async def _build_diagram_spec(self, topic: str, slide: Dict) -> Optional[Dict]:
        try:
            system_prompt = f"""You design educational presentation diagrams for Vynetra.

Return ONLY valid JSON with this structure:
{{
  "title": "Diagram title",
  "description": "What the diagram explains",
  "diagram_type": "flowchart",
  "layout": "vertical_flow",
  "nodes": [
    {{"id": "n1", "label": "Label"}}
  ],
  "edges": [
    {{"from": "n1", "to": "n2", "label": "optional"}}
  ]
}}

Rules:
- Use the topic "{topic}" and this slide as the source of truth.
- Build a meaningful diagram only for structure, flow, architecture, relationships, or algorithm steps.
- Use 3 to 6 concise nodes.
- Prefer layouts: vertical_flow, horizontal_flow, hub_spoke, layered.
- Keep labels short and professional.
- Do not create placeholders or generic diagrams.
"""

            response = await self.llm.generate(
                prompt=json.dumps(
                    {
                        "topic": topic,
                        "slide": {
                            "number": slide.get("number"),
                            "title": slide.get("title", ""),
                            "content": slide.get("content", ""),
                            "bullet_points": slide.get("bullet_points", [])[:5],
                        },
                    }
                ),
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=1400,
            )

            json_match = re.search(r"\{.*\}", response.text, re.DOTALL)
            if not json_match:
                return None

            parsed = json.loads(json_match.group())
            if self._is_valid_spec(parsed):
                return parsed
            return None
        except Exception as e:
            logger.error("Error generating diagram spec: %s", e)
            return None

    def _fallback_spec_from_slide(self, slide: Dict) -> Optional[Dict]:
        labels = [slide.get("title", "").strip()]
        labels.extend([bullet.strip() for bullet in slide.get("bullet_points", []) if bullet.strip()])
        labels = [label[:42] for label in labels if label][:5]

        if len(labels) < 3:
            return None

        nodes = [{"id": f"n{i+1}", "label": label} for i, label in enumerate(labels)]
        edges = [{"from": f"n{i+1}", "to": f"n{i+2}", "label": ""} for i in range(len(labels) - 1)]

        return {
            "title": f"{slide.get('title', 'Concept')} Flow",
            "description": f"Diagram summarising the key flow for {slide.get('title', 'this slide')}.",
            "diagram_type": "flowchart",
            "layout": "vertical_flow",
            "nodes": nodes,
            "edges": edges,
        }

    def _is_valid_spec(self, spec: Dict) -> bool:
        nodes = spec.get("nodes", [])
        edges = spec.get("edges", [])
        return (
            isinstance(spec, dict)
            and spec.get("title")
            and spec.get("description")
            and spec.get("diagram_type")
            and spec.get("layout")
            and isinstance(nodes, list)
            and len(nodes) >= 3
            and isinstance(edges, list)
            and len(edges) >= 2
        )

    def _render_diagram(self, job_id: str, index: int, spec: Dict) -> Optional[str]:
        try:
            output_dir = Path(settings.STORAGE_PATH).resolve() / "presentations" / job_id / "diagrams"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"diagram_{index}.png"

            image = Image.new("RGB", (1600, 900), "#F8FAFC")
            draw = ImageDraw.Draw(image)

            title_font = self._load_font(42, bold=True)
            body_font = self._load_font(24)
            label_font = self._load_font(20)

            draw.text((80, 50), spec["title"], fill="#0F172A", font=title_font)
            draw.text((80, 110), spec["description"], fill="#475569", font=body_font)

            positions = self._layout_nodes(spec["nodes"], spec["layout"])
            self._draw_edges(draw, spec["edges"], positions, label_font)
            self._draw_nodes(draw, spec["nodes"], positions, body_font)

            image.save(output_path)
            return str(output_path.resolve())
        except Exception as e:
            logger.error("Error rendering diagram: %s", e)
            return None

    def _layout_nodes(self, nodes: List[Dict], layout: str) -> Dict[str, Dict[str, float]]:
        layout = (layout or "vertical_flow").lower()
        node_ids = [node["id"] for node in nodes]

        if layout == "horizontal_flow":
            return self._horizontal_positions(node_ids)
        if layout == "hub_spoke":
            return self._hub_spoke_positions(node_ids)
        if layout == "layered":
            return self._layered_positions(node_ids)
        return self._vertical_positions(node_ids)

    def _vertical_positions(self, node_ids: List[str]) -> Dict[str, Dict[str, float]]:
        positions = {}
        start_y = 220
        gap = 140
        for idx, node_id in enumerate(node_ids):
            positions[node_id] = {"x": 800, "y": start_y + idx * gap}
        return positions

    def _horizontal_positions(self, node_ids: List[str]) -> Dict[str, Dict[str, float]]:
        positions = {}
        count = max(len(node_ids), 1)
        gap = 1300 / count
        for idx, node_id in enumerate(node_ids):
            positions[node_id] = {"x": 180 + gap * idx + gap / 2, "y": 470}
        return positions

    def _hub_spoke_positions(self, node_ids: List[str]) -> Dict[str, Dict[str, float]]:
        positions = {}
        if not node_ids:
            return positions

        positions[node_ids[0]] = {"x": 800, "y": 470}
        radius = 260
        spoke_count = max(len(node_ids) - 1, 1)
        for idx, node_id in enumerate(node_ids[1:]):
            angle = (2 * math.pi * idx) / spoke_count
            positions[node_id] = {
                "x": 800 + radius * math.cos(angle),
                "y": 470 + radius * math.sin(angle),
            }
        return positions

    def _layered_positions(self, node_ids: List[str]) -> Dict[str, Dict[str, float]]:
        positions = {}
        rows = [node_ids[i:i + 2] for i in range(0, len(node_ids), 2)]
        for row_index, row in enumerate(rows):
            y = 260 + row_index * 180
            gap = 1100 / max(len(row), 1)
            for idx, node_id in enumerate(row):
                positions[node_id] = {"x": 250 + gap * idx + gap / 2, "y": y}
        return positions

    def _draw_nodes(self, draw: ImageDraw.ImageDraw, nodes: List[Dict], positions: Dict[str, Dict[str, float]], font):
        width = 260
        height = 92
        for node in nodes:
            position = positions.get(node["id"])
            if not position:
                continue
            x = position["x"]
            y = position["y"]
            bounds = (x - width / 2, y - height / 2, x + width / 2, y + height / 2)
            draw.rounded_rectangle(bounds, radius=24, fill="#E2E8F0", outline="#6366F1", width=4)

            wrapped = textwrap.fill(node.get("label", ""), width=20)
            bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=6)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            draw.multiline_text(
                (x - text_w / 2, y - text_h / 2),
                wrapped,
                fill="#0F172A",
                font=font,
                spacing=6,
                align="center",
            )

    def _draw_edges(self, draw: ImageDraw.ImageDraw, edges: List[Dict], positions: Dict[str, Dict[str, float]], font):
        for edge in edges:
            start = positions.get(edge.get("from"))
            end = positions.get(edge.get("to"))
            if not start or not end:
                continue

            start_xy = (start["x"], start["y"])
            end_xy = (end["x"], end["y"])
            draw.line([start_xy, end_xy], fill="#334155", width=5)
            self._draw_arrowhead(draw, start_xy, end_xy)

            label = (edge.get("label") or "").strip()
            if label:
                mid_x = (start["x"] + end["x"]) / 2
                mid_y = (start["y"] + end["y"]) / 2
                bbox = draw.textbbox((0, 0), label, font=font)
                padding = 8
                draw.rounded_rectangle(
                    (
                        mid_x - (bbox[2] - bbox[0]) / 2 - padding,
                        mid_y - (bbox[3] - bbox[1]) / 2 - padding,
                        mid_x + (bbox[2] - bbox[0]) / 2 + padding,
                        mid_y + (bbox[3] - bbox[1]) / 2 + padding,
                    ),
                    radius=12,
                    fill="#FFFFFF",
                    outline="#CBD5E1",
                )
                draw.text((mid_x - (bbox[2] - bbox[0]) / 2, mid_y - (bbox[3] - bbox[1]) / 2), label, fill="#334155", font=font)

    def _draw_arrowhead(self, draw: ImageDraw.ImageDraw, start_xy, end_xy):
        angle = math.atan2(end_xy[1] - start_xy[1], end_xy[0] - start_xy[0])
        size = 16
        left = (
            end_xy[0] - size * math.cos(angle - math.pi / 6),
            end_xy[1] - size * math.sin(angle - math.pi / 6),
        )
        right = (
            end_xy[0] - size * math.cos(angle + math.pi / 6),
            end_xy[1] - size * math.sin(angle + math.pi / 6),
        )
        draw.polygon([end_xy, left, right], fill="#334155")

    def _load_font(self, size: int, bold: bool = False):
        candidates = [
            "arialbd.ttf" if bold else "arial.ttf",
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
        return ImageFont.load_default()
