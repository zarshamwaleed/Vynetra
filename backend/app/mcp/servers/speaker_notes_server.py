from fastmcp import FastMCP
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

mcp = FastMCP("Speaker Notes Server")

os.makedirs("./generated/notes", exist_ok=True)

@mcp.tool()
def generate_notes(slide_title: str, content: str, audience: str = "general") -> str:
    """Generate speaker notes for a slide."""
    try:
        notes_templates = {
            "general": [
                f"Introduction to {slide_title}",
                f"Key points to emphasize: {content[:100]}...",
                "Engage the audience with questions",
                "Provide real-world examples"
            ],
            "expert": [
                f"Deep dive into {slide_title}",
                f"Technical details: {content[:150]}...",
                "Discuss advanced concepts",
                "Share research findings"
            ],
            "beginner": [
                f"Simple explanation of {slide_title}",
                f"Break down: {content[:100]}...",
                "Use analogies and simple examples",
                "Check for understanding frequently"
            ],
            "executive": [
                f"Strategic importance of {slide_title}",
                f"Business impact: {content[:100]}...",
                "Focus on ROI and outcomes",
                "Keep it concise and action-oriented"
            ]
        }
        
        notes = notes_templates.get(audience, notes_templates["general"])
        
        speaker_notes = {
            "slide_title": slide_title,
            "audience": audience,
            "key_points": notes,
            "duration_estimate": f"{len(notes) * 30} seconds",
            "tone": "Professional",
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"Generated notes for: {slide_title}")
        return json.dumps(speaker_notes, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating notes: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def generate_full_notes(slides: str, audience: str = "general") -> str:
    """Generate speaker notes for multiple slides."""
    try:
        if isinstance(slides, str):
            slides_data = json.loads(slides)
        else:
            slides_data = slides
        
        if "slides" in slides_data:
            slides_list = slides_data["slides"]
        else:
            slides_list = slides_data
        
        all_notes = []
        for slide in slides_list:
            title = slide.get("title", "Untitled")
            content = slide.get("content", "")
            notes = json.loads(generate_notes(title, content, audience))
            all_notes.append(notes)
        
        full_notes = {
            "title": slides_data.get("title", "Presentation"),
            "audience": audience,
            "total_slides": len(all_notes),
            "notes": all_notes,
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Generated full notes for {len(all_notes)} slides")
        return json.dumps(full_notes, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating full notes: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def export_notes(notes: str, format: str = "markdown") -> str:
    """Export speaker notes to a file."""
    try:
        if isinstance(notes, str):
            notes_data = json.loads(notes)
        else:
            notes_data = notes
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"./generated/notes/speaker_notes_{timestamp}.{format}"
        
        os.makedirs("./generated/notes", exist_ok=True)
        
        if format == "markdown":
            content = f"# Speaker Notes\n\n"
            content += f"## {notes_data.get('title', 'Presentation')}\n\n"
            for slide_notes in notes_data.get("notes", []):
                content += f"### {slide_notes.get('slide_title', 'Slide')}\n\n"
                for point in slide_notes.get("key_points", []):
                    content += f"- {point}\n"
                content += f"\n*Duration: {slide_notes.get('duration_estimate', 'N/A')}*\n\n"
        else:
            content = json.dumps(notes_data, indent=2)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        result = {
            "success": True,
            "path": output_path,
            "format": format,
            "message": f"Notes exported successfully to {output_path}"
        }
        
        logger.info(f"Exported notes to: {output_path}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error exporting notes: {e}")
        return json.dumps({"error": str(e), "success": False})

if __name__ == "__main__":
    mcp.run()
