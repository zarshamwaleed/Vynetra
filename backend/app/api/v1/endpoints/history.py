from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from app.core.database import get_db
from app.services.history_service import HistoryService
from app.models import Presentation, Asset

router = APIRouter()

class HistoryResponse(BaseModel):
    id: int
    presentation_id: int
    presentation_title: str
    action: str
    status: str
    message: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: str

@router.get("/")
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    action: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
) -> List[HistoryResponse]:
    """Get all history entries with filters"""
    service = HistoryService(db)
    history = service.get_all_history(limit=limit, offset=offset, action=action, status=status)
    return [HistoryResponse(**h) for h in history]

@router.get("/presentations")
async def get_presentations_history(
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all presentations with their history"""
    presentations = db.query(Presentation).order_by(Presentation.created_at.desc()).all()
    
    result = []
    for pres in presentations:
        # Get latest history entry
        latest_history = db.query(History).filter(
            History.presentation_id == pres.id
        ).order_by(History.created_at.desc()).first()
        
        # Count assets
        asset_count = db.query(Asset).filter(Asset.presentation_id == pres.id).count()
        
        result.append({
            "id": pres.id,
            "title": pres.title,
            "prompt": pres.prompt,
            "status": pres.status,
            "slide_count": pres.slide_count,
            "created_at": pres.created_at.isoformat(),
            "updated_at": pres.updated_at.isoformat(),
            "latest_action": latest_history.action if latest_history else "created",
            "latest_status": latest_history.status if latest_history else "success",
            "asset_count": asset_count
        })
    
    return result

@router.get("/presentations/{presentation_id}")
async def get_presentation_history(
    presentation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed history for a specific presentation"""
    presentation = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    service = HistoryService(db)
    history = service.get_presentation_history(presentation_id)
    
    # Get assets
    assets = db.query(Asset).filter(Asset.presentation_id == presentation_id).all()
    
    return {
        "presentation": {
            "id": presentation.id,
            "title": presentation.title,
            "prompt": presentation.prompt,
            "status": presentation.status,
            "slide_count": presentation.slide_count,
            "created_at": presentation.created_at.isoformat(),
            "updated_at": presentation.updated_at.isoformat()
        },
        "history": [
            {
                "id": h.id,
                "action": h.action,
                "status": h.status,
                "message": h.message,
                "metadata": h.history_metadata,
                "created_at": h.created_at.isoformat()
            }
            for h in history
        ],
        "assets": [
            {
                "id": a.id,
                "name": a.name,
                "type": a.type,
                "path": a.path,
                "size": a.size,
                "created_at": a.created_at.isoformat()
            }
            for a in assets
        ]
    }

@router.get("/stats")
async def get_history_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get history statistics"""
    service = HistoryService(db)
    return service.get_history_stats()

@router.delete("/presentations/{presentation_id}/history")
async def delete_presentation_history(
    presentation_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Delete all history entries for a presentation"""
    presentation = db.query(Presentation).filter(Presentation.id == presentation_id).first()
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    service = HistoryService(db)
    count = service.delete_presentation_history(presentation_id)
    
    return {"message": f"Deleted {count} history entries", "presentation_id": presentation_id}
