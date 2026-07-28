from fastmcp import FastMCP
import json
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

mcp = FastMCP("Diagram Server")

# Create output directory
os.makedirs("./generated/diagrams", exist_ok=True)

@mcp.tool()
def generate_mermaid(diagram_type: str, title: str, elements: str) -> str:
    """Generate a Mermaid diagram."""
    try:
        if isinstance(elements, str):
            elements_data = json.loads(elements)
        else:
            elements_data = elements
        
        mermaid_code = f"%%{title}\n"
        
        if diagram_type == "flowchart":
            mermaid_code += f"flowchart TD\n"
            for node in elements_data.get("nodes", []):
                mermaid_code += f"    {node['id']}[\"{node['label']}\"]\n"
            for edge in elements_data.get("edges", []):
                mermaid_code += f"    {edge['from']} --> {edge['to']}\n"
        else:
            mermaid_code += f"graph LR\n"
            for element in elements_data.get("elements", []):
                mermaid_code += f"    {element['id']}[\"{element['label']}\"]\n"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"./generated/diagrams/mermaid_{timestamp}.mmd"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        
        result = {
            "success": True,
            "diagram_type": diagram_type,
            "title": title,
            "code": mermaid_code,
            "path": output_path,
            "timestamp": timestamp
        }
        
        logger.info(f"Generated Mermaid diagram: {title}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating Mermaid diagram: {e}")
        return json.dumps({"error": str(e), "success": False})

@mcp.tool()
def generate_graphviz(diagram_type: str, title: str, elements: str) -> str:
    """Generate a Graphviz diagram."""
    try:
        if isinstance(elements, str):
            elements_data = json.loads(elements)
        else:
            elements_data = elements
        
        dot_code = f"// {title}\n"
        dot_code += "digraph G {\n"
        dot_code += f"    label=\"{title}\"\n"
        dot_code += "    node [shape=box, style=filled, fillcolor=lightblue]\n"
        
        for node in elements_data.get("nodes", []):
            dot_code += f"    {node['id']} [label=\"{node['label']}\"]\n"
        
        for edge in elements_data.get("edges", []):
            dot_code += f"    {edge['from']} -> {edge['to']} [label=\"{edge.get('label', '')}\"]\n"
        
        dot_code += "}\n"
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"./generated/diagrams/graphviz_{timestamp}.dot"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dot_code)
        
        result = {
            "success": True,
            "diagram_type": diagram_type,
            "title": title,
            "code": dot_code,
            "path": output_path,
            "timestamp": timestamp
        }
        
        logger.info(f"Generated Graphviz diagram: {title}")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating Graphviz diagram: {e}")
        return json.dumps({"error": str(e), "success": False})

@mcp.tool()
def list_diagrams() -> str:
    """List all generated diagrams."""
    try:
        diagrams = []
        for file in os.listdir("./generated/diagrams"):
            if file.endswith(('.mmd', '.dot', '.png')):
                diagrams.append({
                    "name": file,
                    "path": f"./generated/diagrams/{file}"
                })
        
        return json.dumps({
            "diagrams": diagrams,
            "count": len(diagrams)
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error listing diagrams: {e}")
        return json.dumps({"error": str(e), "success": False})

if __name__ == "__main__":
    mcp.run()
