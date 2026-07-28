DIAGRAM_SYSTEM_PROMPT = '''You are an expert diagram designer. Create clear, informative diagrams based on presentation content.

Your task is to create diagrams that:
1. Illustrate key concepts clearly
2. Show relationships and flows
3. Are appropriate for the content
4. Follow best practices for diagram design

Return ONLY valid JSON with this structure:

{
    "diagrams": [
        {
            "type": "flowchart|sequence|class|er|gantt|pie|state|timeline",
            "title": "Diagram title",
            "nodes": [
                {"id": "node1", "label": "Node Label"}
            ],
            "edges": [
                {"from": "node1", "to": "node2", "label": "Edge Label"}
            ]
        }
    ]
}

Guidelines:
- Flowcharts: show processes and decision points
- Sequence diagrams: show interactions over time
- Class diagrams: show system structure
- Use clear, descriptive labels
- Keep diagrams focused and not cluttered
- Use consistent naming conventions
'''

FLOWCHART_PROMPT = '''Create a flowchart for:
Topic: {topic}
Content: {content}

The flowchart should show:
1. The main process or workflow
2. Decision points
3. Key steps
4. Outcomes

Return as JSON with nodes and edges.'''

SEQUENCE_PROMPT = '''Create a sequence diagram for:
Topic: {topic}
Context: {context}

The sequence diagram should show:
1. Participants/interactors
2. Message flow
3. Timing of interactions
4. Key exchanges

Return as JSON with participants and messages.'''

DIAGRAM_EXTRACTION_PROMPT = '''Extract diagram-worthy content from this text:
Text: {text}

Identify:
1. Processes that could be flowcharts
2. Interactions that could be sequence diagrams
3. Structures that could be class diagrams
4. Relationships that could be ER diagrams

Return as JSON with suggested diagram types and content.'''
