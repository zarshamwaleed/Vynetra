from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import logging
import asyncio
from fastapi.responses import FileResponse, JSONResponse
import os
import tempfile
import json
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import io

from app.services.timeline_service import timeline_service
from app.services.llm import LLMService
from app.services.diagram_generator import DiagramGenerator
from app.services.animation_generator import AnimationGenerator

router = APIRouter()
logger = logging.getLogger(__name__)

class GenerateRequest(BaseModel):
    prompt: str
    slide_count: Optional[int] = 10
    audience: Optional[str] = "general"
    tone: Optional[str] = "educational"

generated_content = {}

@router.post("/generate")
async def generate_presentation(request: GenerateRequest, background_tasks: BackgroundTasks):
    try:
        job_id = str(uuid.uuid4())
        logger.info(f"Generation started for job: {job_id}")
        logger.info(f"Prompt: {request.prompt[:100]}...")
        
        timeline_service.create_job(job_id, request.prompt)
        background_tasks.add_task(
            simulate_generation, 
            job_id, 
            request.prompt, 
            request.slide_count
        )
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Presentation generation started for: {request.prompt[:50]}..."
        }
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def simulate_generation(job_id: str, prompt: str, slide_count: int = 10):
    try:
        llm = LLMService(provider="groq")
        diagram_gen = DiagramGenerator(llm)
        animation_gen = AnimationGenerator(llm)
        
        # Step 1: Planning
        timeline_service.update_step(job_id, "planning", "in_progress", "Analyzing prompt...")
        await asyncio.sleep(0.5)
        timeline_service.update_step(job_id, "planning", "completed", "Planning complete")
        
        # Step 2: Generate content
        timeline_service.update_step(job_id, "research", "in_progress", "Generating content...")
        
        system_prompt = f"""You are a presentation expert. Create a detailed presentation outline with {slide_count} slides about: {prompt}

        Return ONLY valid JSON with this structure:
        {{
            "title": "Presentation Title",
            "slides": [
                {{
                    "number": 1,
                    "title": "Slide Title",
                    "content": "Main content for the slide",
                    "bullet_points": ["Key point 1", "Key point 2", "Key point 3"],
                    "speaker_notes": "Speaker notes for this slide"
                }}
            ],
            "key_concepts": ["Concept 1", "Concept 2", "Concept 3"]
        }}
        
        Make the content educational and informative.
        """
        
        response = await llm.generate(
            prompt=f"Create a presentation about: {prompt}",
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=4096
        )
        
        import re
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if json_match:
            content_data = json.loads(json_match.group())
        else:
            content_data = {"title": prompt, "slides": [], "key_concepts": []}
        
        timeline_service.update_step(job_id, "research", "completed", "Research complete")
        
        # Step 3: Generate diagrams
        timeline_service.update_step(job_id, "diagrams", "in_progress", "Creating diagrams...")
        
        diagrams = await diagram_gen.generate_diagrams(prompt, content_data.get("slides", []))
        
        generated_content[job_id] = generated_content.get(job_id, {})
        generated_content[job_id]["diagrams"] = diagrams
        
        timeline_service.update_step(job_id, "diagrams", "completed", f"{len(diagrams)} diagrams created")
        
        # Step 4: Generate animation
        timeline_service.update_step(job_id, "animation", "in_progress", "Creating educational animation...")
        
        animation = await animation_gen.generate_animation(prompt, content_data.get("slides", []))
        if animation:
            generated_content[job_id]["animation"] = animation
        
        timeline_service.update_step(job_id, "animation", "completed", "Animation created")
        
        # Step 5: Build PowerPoint
        timeline_service.update_step(job_id, "ppt", "in_progress", "Building PowerPoint...")
        await generate_pptx(job_id, content_data, prompt, diagrams)
        timeline_service.update_step(job_id, "ppt", "completed", "PowerPoint created")
        
        # Step 6: Generate PDF
        timeline_service.update_step(job_id, "pdf", "in_progress", "Exporting to PDF...")
        await generate_pdf(job_id, content_data, prompt, diagrams)
        timeline_service.update_step(job_id, "pdf", "completed", "PDF exported")
        
        # Step 7: Generate Speaker Notes
        timeline_service.update_step(job_id, "notes", "in_progress", "Generating speaker notes...")
        await generate_notes(job_id, content_data, prompt)
        timeline_service.update_step(job_id, "notes", "completed", "Speaker notes ready")
        
        # Step 8: Complete
        timeline_service.update_step(job_id, "complete", "completed", "Presentation ready!")
        
        generated_content[job_id]["slides"] = content_data.get("slides", [])
        generated_content[job_id]["title"] = content_data.get("title", prompt)
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        timeline_service.update_step(job_id, "complete", "failed", f"Error: {str(e)}")

async def generate_pptx(job_id: str, content_data: dict, prompt: str, diagrams: list):
    try:
        prs = Presentation()
        
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = content_data.get("title", f"Presentation on {prompt}")
        if len(slide.placeholders) > 1:
            slide.placeholders[1].text = f"Generated by Vynetra AI\n{prompt}"
        
        slides_data = content_data.get("slides", [])
        if not slides_data:
            slides_data = [
                {"number": 1, "title": f"Introduction to {prompt}", "content": f"Welcome to this presentation about {prompt}.", "bullet_points": ["Key concept 1", "Key concept 2", "Key concept 3"]},
            ]
        
        for slide_data in slides_data[:8]:
            slide_layout = prs.slide_layouts[1]
            slide = prs.slides.add_slide(slide_layout)
            slide.shapes.title.text = slide_data.get("title", f"Slide {slide_data.get('number', 0)}")
            
            content = slide.placeholders[1]
            text = slide_data.get("content", "")
            bullet_points = slide_data.get("bullet_points", [])
            
            if bullet_points:
                content.text = text + "\n\n" + "\n".join(["• " + bp for bp in bullet_points])
            else:
                content.text = text
        
        # Add diagrams
        for diagram in diagrams[:2]:
            try:
                if diagram.get("image_path") and os.path.exists(diagram["image_path"]):
                    slide_layout = prs.slide_layouts[5]
                    slide = prs.slides.add_slide(slide_layout)
                    slide.shapes.title.text = diagram.get("title", "Diagram")
                    left = Inches(1.5)
                    top = Inches(1.5)
                    width = Inches(9)
                    slide.shapes.add_picture(diagram["image_path"], left, top, width=width)
            except:
                pass
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pptx")
        prs.save(temp_file.name)
        temp_file.close()
        
        generated_content[job_id]["pptx_path"] = temp_file.name
        
        logger.info(f"PPTX generated for job: {job_id}")
        
    except Exception as e:
        logger.error(f"Error generating PPTX: {e}")

async def generate_pdf(job_id: str, content_data: dict, prompt: str, diagrams: list):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=24, alignment=TA_CENTER, spaceAfter=20)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading1'], fontSize=16, spaceAfter=10)
        body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=11, alignment=TA_LEFT, spaceAfter=8)
        bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=11, leftIndent=20, spaceAfter=4)
        
        story = []
        
        story.append(Paragraph(content_data.get("title", f"Presentation on {prompt}"), title_style))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"Topic: {prompt}", styles['Normal']))
        story.append(Spacer(1, 12))
        story.append(Paragraph("Generated by Vynetra AI", styles['Normal']))
        story.append(PageBreak())
        
        slides_data = content_data.get("slides", [])
        for slide_data in slides_data[:8]:
            story.append(Paragraph(f"Slide {slide_data.get('number', 0)}: {slide_data.get('title', 'Slide')}", heading_style))
            story.append(Paragraph(slide_data.get("content", ""), body_style))
            for bp in slide_data.get("bullet_points", []):
                story.append(Paragraph(f"• {bp}", bullet_style))
            story.append(Spacer(1, 12))
            story.append(PageBreak())
        
        # Add diagrams
        for diagram in diagrams[:2]:
            try:
                if diagram.get("image_path") and os.path.exists(diagram["image_path"]):
                    story.append(Paragraph(diagram.get("title", "Diagram"), heading_style))
                    img = Image(diagram["image_path"], width=400, height=250)
                    story.append(img)
                    story.append(Spacer(1, 12))
                    story.append(PageBreak())
            except:
                pass
        
        doc.build(story)
        temp_file.close()
        
        generated_content[job_id]["pdf_path"] = temp_file.name
        
        logger.info(f"PDF generated for job: {job_id}")
        
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")

async def generate_notes(job_id: str, content_data: dict, prompt: str):
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        content = []
        
        content.append("=" * 60)
        content.append(f"SPEAKER NOTES: {content_data.get('title', prompt)}")
        content.append("=" * 60)
        content.append("")
        
        slides_data = content_data.get("slides", [])
        for slide_data in slides_data[:10]:
            title = slide_data.get("title", f"Slide {slide_data.get('number', 0)}")
            notes = slide_data.get("speaker_notes", slide_data.get("content", ""))
            
            content.append("")
            content.append(f"SLIDE {slide_data.get('number', 0)}: {title}")
            content.append("-" * 40)
            content.append(notes)
            content.append("")
        
        content.append("")
        content.append("=" * 60)
        content.append(f"Generated by Vynetra AI")
        content.append(f"Job ID: {job_id}")
        content.append("=" * 60)
        
        full_content = "\n".join(content)
        temp_file.write(full_content.encode('utf-8'))
        temp_file.close()
        
        generated_content[job_id]["notes_path"] = temp_file.name
        
        logger.info(f"Notes generated for job: {job_id}")
        
    except Exception as e:
        logger.error(f"Error generating notes: {e}")

@router.get("/{job_id}/content")
async def get_content(job_id: str):
    if job_id in generated_content:
        return {
            "job_id": job_id,
            "title": generated_content[job_id].get("title", ""),
            "slides": generated_content[job_id].get("slides", []),
            "diagrams": generated_content[job_id].get("diagrams", []),
            "animation": generated_content[job_id].get("animation", {})
        }
    return {
        "job_id": job_id,
        "error": "Content not found"
    }

@router.get("/{job_id}/download/{file_type}")
async def download_file(job_id: str, file_type: str):
    try:
        if job_id in generated_content:
            if file_type == "pptx" and "pptx_path" in generated_content[job_id]:
                return FileResponse(
                    generated_content[job_id]["pptx_path"],
                    media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    filename=f"presentation_{job_id}.pptx"
                )
            elif file_type == "pdf" and "pdf_path" in generated_content[job_id]:
                return FileResponse(
                    generated_content[job_id]["pdf_path"],
                    media_type="application/pdf",
                    filename=f"presentation_{job_id}.pdf"
                )
            elif file_type == "notes" and "notes_path" in generated_content[job_id]:
                return FileResponse(
                    generated_content[job_id]["notes_path"],
                    media_type="text/plain",
                    filename=f"speaker_notes_{job_id}.txt"
                )
            elif file_type == "animation":
                if "animation" in generated_content[job_id]:
                    anim = generated_content[job_id]["animation"]
                    if anim:
                        # Check if video exists
                        if anim.get("video_path") and os.path.exists(anim["video_path"]):
                            return FileResponse(
                                anim["video_path"],
                                media_type="video/mp4",
                                filename=f"animation_{job_id}.mp4"
                            )
                        # If no video, return a placeholder message
                        else:
                            # Create a simple text file explaining
                            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
                            content = f"Animation for: {generated_content[job_id].get('title', 'Presentation')}\n\n"
                            content += "Video generation is currently being processed.\n"
                            content += "Please check back later or install Manim for video rendering.\n\n"
                            content += "Manim code that would be rendered:\n"
                            content += "-" * 40 + "\n"
                            content += anim.get("code", "No code available")
                            temp_file.write(content.encode('utf-8'))
                            temp_file.close()
                            return FileResponse(
                                temp_file.name,
                                media_type="text/plain",
                                filename=f"animation_info_{job_id}.txt"
                            )
        
        return JSONResponse(
            status_code=404,
            content={"error": "File not found"}
        )
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@router.get("/{job_id}/status")
async def get_status(job_id: str):
    timeline = timeline_service.get_timeline(job_id)
    if "error" in timeline:
        return {
            "job_id": job_id,
            "status": "not_found",
            "progress": 0,
            "message": "Job not found"
        }
    
    return {
        "job_id": job_id,
        "status": timeline["status"],
        "progress": timeline["progress"],
        "current_step": timeline["current_step"],
        "message": f"Processing: {timeline.get('current_step', 'starting')}"
    }

@router.get("/")
async def list_presentations():
    return {
        "presentations": [],
        "total": 0
    }
