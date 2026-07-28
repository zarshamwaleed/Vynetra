MANIM_SYSTEM_PROMPT = '''You are an expert in Manim (Mathematical Animation) code generation. You create educational animations that explain complex concepts visually.

Your task is to generate Manim Python code that:
1. Illustrates the given concept clearly
2. Uses appropriate animations and visualizations
3. Follows Manim best practices
4. Is complete and runnable

Return ONLY the Python code for the Manim scene.

Follow this structure:
from manim import *

class SceneName(Scene):
    def construct(self):
        # Your animation code here
        pass

Guidelines:
- Use clear variable names
- Include comments explaining the animation
- Use appropriate colors and positioning
- Make animations smooth and educational
- Include title and labels where needed
'''

SCENE_GENERATION_PROMPT = '''Generate a Manim scene for:
Topic: {topic}
Concept: {concept}
Description: {description}
Audience: {audience}

The scene should:
1. Visually explain the concept
2. Include animations
3. Be engaging and educational
4. Be appropriate for the audience level

Return the complete Python code.'''

SCENE_EXTRACTION_PROMPT = '''Extract key concepts from this content that could be turned into Manim animations:
Content: {content}

Identify:
1. Concepts that benefit from visual explanation
2. Processes that could be animated
3. Relationships that could be visualized
4. Complex ideas that need simplification

Return as JSON with scene descriptions.'''
