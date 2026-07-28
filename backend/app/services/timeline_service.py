import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)

class TimelineStep(str, Enum):
    PLANNING = "planning"
    RESEARCH = "research"
    SLIDES = "slides"
    DIAGRAMS = "diagrams"
    ANIMATION = "animation"
    PPT = "ppt"
    PDF = "pdf"
    COMPLETE = "complete"

class TimelineStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TimelineService:
    '''Service for tracking generation progress'''
    
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
    
    def create_job(self, job_id: str, prompt: str) -> str:
        '''Create a new timeline job'''
        self.jobs[job_id] = {
            "job_id": job_id,
            "prompt": prompt,
            "status": "started",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "steps": {
                "planning": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "research": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "slides": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "diagrams": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "animation": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "ppt": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "pdf": {"status": "pending", "started_at": None, "completed_at": None, "message": ""},
                "complete": {"status": "pending", "started_at": None, "completed_at": None, "message": ""}
            },
            "current_step": "",
            "progress": 0,
            "total_steps": 8
        }
        logger.info(f"Timeline created for job: {job_id}")
        return job_id
    
    def update_step(
        self,
        job_id: str,
        step: str,
        status: str,
        message: str = ""
    ) -> Dict[str, Any]:
        '''Update a step status'''
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.jobs[job_id]
        step_data = job["steps"].get(step)
        if not step_data:
            return {"error": f"Step {step} not found"}
        
        step_data["status"] = status
        step_data["message"] = message
        
        if status == "in_progress" and not step_data["started_at"]:
            step_data["started_at"] = datetime.now().isoformat()
        elif status == "completed":
            step_data["completed_at"] = datetime.now().isoformat()
            job["current_step"] = step
        elif status == "failed":
            step_data["completed_at"] = datetime.now().isoformat()
            job["status"] = "failed"
        
        job["updated_at"] = datetime.now().isoformat()
        job["progress"] = self._calculate_progress(job)
        
        return job
    
    def _calculate_progress(self, job: Dict[str, Any]) -> int:
        '''Calculate overall progress percentage'''
        completed = sum(1 for s in job["steps"].values() if s["status"] == "completed")
        total = len(job["steps"])
        return int((completed / total) * 100)
    
    def get_timeline(self, job_id: str) -> Dict[str, Any]:
        '''Get the full timeline for a job'''
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        
        job = self.jobs[job_id]
        return {
            "job_id": job["job_id"],
            "prompt": job["prompt"],
            "status": job["status"],
            "progress": job["progress"],
            "current_step": job["current_step"],
            "steps": job["steps"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"]
        }
    
    def get_step_status(self, job_id: str, step: str) -> Dict[str, Any]:
        '''Get status of a specific step'''
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        job = self.jobs[job_id]
        return job["steps"].get(step, {"error": f"Step {step} not found"})
    
    def list_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        '''List recent jobs'''
        jobs = list(self.jobs.values())
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        return jobs[:limit]

# Singleton instance
timeline_service = TimelineService()
