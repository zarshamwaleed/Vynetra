import logging
import os
import tempfile
import subprocess
import re
from typing import Dict, Any, Optional, List
from app.services.llm import LLMService
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import tempfile

logger = logging.getLogger(__name__)

class AnimationGenerator:
    """Generate educational animations"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    async def generate_animation(self, topic: str, slides: List[Dict]) -> Optional[Dict]:
        """Generate a comprehensive animation"""
        try:
            # Extract key concepts from slides
            concepts = []
            for slide in slides[:5]:
                title = slide.get("title", "")
                if title and len(title) > 10:
                    concepts.append(title[:40])
            
            if not concepts:
                concepts = [f"Concept {i+1}" for i in range(4)]
            
            # Generate video using OpenCV (no Manim required)
            video_path = await self._generate_video(topic, concepts)
            
            animation_data = {
                "title": f"Animation: {topic}",
                "description": f"Educational animation explaining {topic}",
                "video_path": video_path,
                "code": self._generate_manim_code(topic, concepts)
            }
            
            return animation_data
            
        except Exception as e:
            logger.error(f"Error generating animation: {e}")
            return None
    
    async def _generate_video(self, topic: str, concepts: List[str]) -> Optional[str]:
        """Generate a simple video using OpenCV"""
        try:
            # Create a temporary file for the video
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
            output_path = temp_file.name
            temp_file.close()
            
            # Video settings
            fps = 24
            duration = 8  # seconds
            total_frames = fps * duration
            width, height = 1280, 720
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            # Colors
            colors = [
                (139, 92, 246),   # Purple
                (59, 130, 246),   # Blue
                (16, 185, 129),   # Green
                (245, 158, 11),   # Yellow
                (236, 72, 153),   # Pink
            ]
            
            # Generate frames
            for frame_idx in range(total_frames):
                # Create blank frame
                img = np.zeros((height, width, 3), dtype=np.uint8)
                img[:] = (15, 23, 42)  # Dark blue background
                
                # Draw title (first 3 seconds)
                if frame_idx < fps * 2:
                    text = f"Understanding {topic[:30]}"
                    font_scale = 2
                    thickness = 3
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                    text_x = (width - text_size[0]) // 2
                    text_y = height // 2
                    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
                
                # Draw concepts (middle frames)
                elif frame_idx < fps * 6:
                    # Show concepts one by one
                    concept_idx = min((frame_idx - fps * 2) // (fps), len(concepts) - 1)
                    current_concept = concepts[concept_idx]
                    
                    # Draw concept box
                    color = colors[concept_idx % len(colors)]
                    box_x, box_y = 200, 150 + concept_idx * 80
                    box_w, box_h = 880, 60
                    cv2.rectangle(img, (box_x, box_y), (box_x + box_w, box_y + box_h), color, -1)
                    cv2.rectangle(img, (box_x, box_y), (box_x + box_w, box_y + box_h), (255, 255, 255), 2)
                    
                    # Draw text
                    text = current_concept[:35]
                    font_scale = 1.2
                    thickness = 2
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                    text_x = box_x + (box_w - text_size[0]) // 2
                    text_y = box_y + (box_h + text_size[1]) // 2
                    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness)
                    
                    # Draw connecting lines
                    if concept_idx > 0:
                        prev_y = 150 + (concept_idx - 1) * 80 + 60
                        curr_y = 150 + concept_idx * 80
                        cv2.line(img, (width // 2, prev_y), (width // 2, curr_y), (255, 255, 255), 3)
                
                # Final frame (last 2 seconds)
                else:
                    text = "✨ Ready to Learn!"
                    font_scale = 2.5
                    thickness = 4
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
                    text_x = (width - text_size[0]) // 2
                    text_y = height // 2
                    cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (34, 197, 94), thickness)
                
                # Write frame
                out.write(img)
            
            # Release video writer
            out.release()
            
            # Re-encode with proper codec
            temp_path = output_path
            final_path = temp_path.replace('.mp4', '_final.mp4')
            
            try:
                # Use ffmpeg to re-encode (if available)
                subprocess.run([
                    'ffmpeg', '-y', '-i', temp_path, 
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-pix_fmt', 'yuv420p', final_path
                ], capture_output=True, timeout=30)
                
                if os.path.exists(final_path) and os.path.getsize(final_path) > 0:
                    os.remove(temp_path)
                    return final_path
            except:
                pass
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return None
    
    def _generate_manim_code(self, topic: str, concepts: List[str]) -> str:
        """Generate Manim code as fallback"""
        concept_lines = []
        show_lines = []
        colors = ["BLUE", "YELLOW", "RED", "GREEN", "PURPLE", "ORANGE", "PINK", "TEAL"]
        
        for i, concept in enumerate(concepts[:6]):
            color = colors[i % len(colors)]
            concept_lines.append(f"        concept_{i} = Text('{concept[:25]}', color={color}, font_size=32)")
            show_lines.append(f"        self.play(Write(concept_{i}))")
        
        concept_code = "\n".join(concept_lines)
        show_code = "\n".join(show_lines)
        
        return f'''from manim import *
import numpy as np

class ConceptAnimation(Scene):
    def construct(self):
        title = Text("{topic[:40]}", color=WHITE, font_size=48)
        title.to_edge(UP)
        self.play(Write(title))
        self.wait(0.5)
        
        circle = Circle(color=BLUE, fill_opacity=0.2)
        square = Square(color=YELLOW, fill_opacity=0.2)
        triangle = Triangle(color=RED, fill_opacity=0.2)
        
        shapes = VGroup(circle, square, triangle)
        shapes.arrange(RIGHT, buff=1)
        shapes.next_to(title, DOWN, buff=0.5)
        
        self.play(Create(shapes))
        self.wait(0.5)
        
        self.play(
            circle.animate.scale(0.5),
            square.animate.rotate(PI/4),
            triangle.animate.shift(UP*0.5)
        )
        self.wait(0.5)
        
{concept_code}
        
        concepts_group = VGroup()
        for i in range({len(concepts[:6])}):
            concepts_group.add(eval(f"concept_{{i}}"))
        
        concepts_group.arrange(DOWN, buff=0.3)
        concepts_group.next_to(shapes, DOWN, buff=0.5)
        
        {show_code}
        self.wait(1)
        
        all_objects = [title, shapes]
        for i in range({len(concepts[:6])}):
            all_objects.append(eval(f"concept_{{i}}"))
        
        self.play(FadeOut(VGroup(*all_objects)))
        self.wait(0.5)
'''
