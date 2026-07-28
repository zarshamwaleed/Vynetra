from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uuid
import logging

from app.services.timeline_service import timeline_service

router = APIRouter()
logger = logging.getLogger(__name__)

class TimelineResponse(BaseModel):
    job_id: str
    prompt: str
    status: str
    progress: int
    current_step: str
    steps: Dict[str, Any]
    created_at: str
    updated_at: str

@router.post("/create")
async def create_timeline(prompt: str) -> Dict[str, Any]:
    """Create a new timeline job"""
    job_id = str(uuid.uuid4())
    timeline_service.create_job(job_id, prompt)
    return {
        "job_id": job_id,
        "status": "created",
        "message": "Timeline created successfully"
    }

@router.get("/{job_id}")
async def get_timeline(job_id: str) -> Dict[str, Any]:
    """Get timeline for a job"""
    result = timeline_service.get_timeline(job_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.post("/{job_id}/step/{step}")
async def update_step(
    job_id: str,
    step: str,
    status: str,
    message: str = ""
) -> Dict[str, Any]:
    """Update a step status"""
    result = timeline_service.update_step(job_id, step, status, message)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@router.get("/{job_id}/progress")
async def get_progress(job_id: str) -> Dict[str, Any]:
    """Get progress for a job"""
    timeline = timeline_service.get_timeline(job_id)
    if "error" in timeline:
        raise HTTPException(status_code=404, detail=timeline["error"])
    return {
        "job_id": job_id,
        "progress": timeline["progress"],
        "current_step": timeline["current_step"],
        "status": timeline["status"]
    }

@router.get("/jobs/recent")
async def list_recent_jobs(limit: int = 20) -> List[Dict[str, Any]]:
    """List recent jobs"""
    return timeline_service.list_jobs(limit)

@router.delete("/{job_id}")
async def delete_timeline(job_id: str) -> Dict[str, Any]:
    """Delete a timeline job"""
    # Implement deletion logic
    return {"status": "deleted", "job_id": job_id}
