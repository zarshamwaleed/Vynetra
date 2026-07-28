from fastmcp import FastMCP
import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

mcp = FastMCP("Citation Server")

citations = []
os.makedirs("./generated/references", exist_ok=True)

@mcp.tool()
def generate_references(sources: str) -> str:
    """Generate formatted references from sources."""
    try:
        if isinstance(sources, str):
            sources_data = json.loads(sources)
        else:
            sources_data = sources
        
        formatted = {
            "apa": [],
            "mla": [],
            "chicago": [],
            "ieee": [],
            "harvard": []
        }
        
        for source in sources_data.get("sources", []):
            title = source.get("title", "Untitled")
            author = source.get("author", "Unknown")
            year = source.get("year", "n.d.")
            publisher = source.get("publisher", "")
            
            formatted["apa"].append(f"{author} ({year}). {title}. {publisher}.")
            formatted["mla"].append(f"{author}. \"{title}.\" {publisher}, {year}.")
            formatted["chicago"].append(f"{author}. \"{title}.\" {publisher}, {year}.")
            formatted["ieee"].append(f"{author}, \"{title},\" {publisher}, {year}.")
            formatted["harvard"].append(f"{author} ({year}) {title}. {publisher}.")
        
        result = {
            "success": True,
            "formatted": formatted,
            "source_count": len(sources_data.get("sources", [])),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info(f"Generated {len(sources_data.get('sources', []))} references")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating references: {e}")
        return json.dumps({"error": str(e), "success": False})

@mcp.tool()
def add_citation(title: str, author: str, year: str, publisher: str = "", url: str = "") -> str:
    """Add a citation to the library."""
    try:
        citation = {
            "title": title,
            "author": author,
            "year": year,
            "publisher": publisher,
            "url": url,
            "added_at": datetime.now().isoformat()
        }
        
        citations.append(citation)
        
        result = {
            "success": True,
            "citation": citation,
            "total_citations": len(citations)
        }
        
        logger.info(f"Added citation: {title}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error adding citation: {e}")
        return json.dumps({"error": str(e), "success": False})

@mcp.tool()
def list_citations() -> str:
    """List all stored citations."""
    try:
        return json.dumps({
            "citations": citations,
            "count": len(citations)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing citations: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def clear_citations() -> str:
    """Clear all stored citations."""
    try:
        global citations
        count = len(citations)
        citations = []
        
        result = {
            "success": True,
            "cleared": count,
            "message": f"Cleared {count} citations"
        }
        
        logger.info(f"Cleared {count} citations")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error clearing citations: {e}")
        return json.dumps({"error": str(e), "success": False})

if __name__ == "__main__":
    mcp.run()
