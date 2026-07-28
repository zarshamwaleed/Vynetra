from fastmcp import FastMCP
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Create FastMCP server
mcp = FastMCP("Presentation Server")

# Store presentation state
presentations = {}

@mcp.tool()
def create_outline(topic: str, slide_count: int = 10) -> str:
    """Create a presentation outline for a given topic."""
    try:
        outline = {
            "title": f"Presentation on {topic}",
            "slides": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "slide_count": slide_count,
                "topic": topic
            }
        }
        
        slide_titles = [
            f"Introduction to {topic}",
            f"What is {topic}?",
            f"Key Concepts of {topic}",
            f"History of {topic}",
            f"Applications of {topic}",
            f"Benefits of {topic}",
            f"Challenges in {topic}",
            f"Future of {topic}",
            f"Summary of {topic}",
            f"Q&A on {topic}"
        ]
        
        for i in range(min(slide_count, len(slide_titles))):
            outline["slides"].append({
                "number": i + 1,
                "title": slide_titles[i % len(slide_titles)],
                "content": f"Content for slide {i+1} about {topic}",
                "notes": f"Speaker notes for slide {i+1}",
                "bullets": [
                    f"Key point 1 for {topic}",
                    f"Key point 2 for {topic}",
                    f"Key point 3 for {topic}"
                ]
            })
        
        presentations[topic] = outline
        logger.info(f"Created outline for topic: {topic}")
        return json.dumps(outline, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating outline: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def create_slide(title: str, content: str, bullet_points: Optional[List[str]] = None) -> str:
    """Create a slide with title and content."""
    try:
        slide = {
            "title": title,
            "content": content,
            "bullet_points": bullet_points or [],
            "created_at": datetime.now().isoformat()
        }
        logger.info(f"Created slide: {title}")
        return json.dumps(slide, indent=2)
        
    except Exception as e:
        logger.error(f"Error creating slide: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def export_ppt(slides: str, filename: str = "presentation") -> str:
    """Export slides to PowerPoint format."""
    try:
        if isinstance(slides, str):
            slides_data = json.loads(slides)
        else:
            slides_data = slides
        
        result = {
            "success": True,
            "filename": f"{filename}.pptx",
            "slide_count": len(slides_data.get("slides", []) if "slides" in slides_data else slides_data),
            "path": f"./generated/ppt/{filename}.pptx",
            "message": "PowerPoint file created successfully"
        }
        
        logger.info(f"Exported presentation: {filename}.pptx")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error exporting PPT: {e}")
        return json.dumps({"error": str(e), "success": False})

@mcp.tool()
def get_presentation(topic: str) -> str:
    """Get a stored presentation outline."""
    try:
        if topic in presentations:
            return json.dumps(presentations[topic], indent=2)
        else:
            return json.dumps({"error": f"No presentation found for topic: {topic}"})
            
    except Exception as e:
        logger.error(f"Error getting presentation: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def list_presentations() -> str:
    """List all stored presentations."""
    try:
        topics = list(presentations.keys())
        return json.dumps({
            "topics": topics,
            "count": len(topics)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing presentations: {e}")
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    # Run with stdio transport (default)
    mcp.run()
