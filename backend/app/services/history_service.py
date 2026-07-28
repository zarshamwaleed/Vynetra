import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Presentation, History, Asset

logger = logging.getLogger(__name__)

class HistoryService:
    '''Service for managing presentation history'''
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_history_entry(
        self,
        presentation_id: int,
        action: str,
        status: str = "success",
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> History:
        '''Create a history entry'''
        history = History(
            presentation_id=presentation_id,
            action=action,
            status=status,
            message=message,
            history_metadata=metadata or {}
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        logger.info(f"History entry created for presentation {presentation_id}: {action}")
        return history
    
    def get_presentation_history(self, presentation_id: int) -> List[History]:
        '''Get all history entries for a presentation'''
        return self.db.query(History).filter(
            History.presentation_id == presentation_id
        ).order_by(desc(History.created_at)).all()
    
    def get_all_history(
        self,
        limit: int = 50,
        offset: int = 0,
        action: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        '''Get all history entries with filters'''
        query = self.db.query(History).join(Presentation)
        
        if action:
            query = query.filter(History.action == action)
        if status:
            query = query.filter(History.status == status)
        
        history_entries = query.order_by(desc(History.created_at)).offset(offset).limit(limit).all()
        
        result = []
        for entry in history_entries:
            result.append({
                "id": entry.id,
                "presentation_id": entry.presentation_id,
                "action": entry.action,
                "status": entry.status,
                "message": entry.message,
                "metadata": entry.history_metadata,
                "created_at": entry.created_at.isoformat(),
                "presentation_title": entry.presentation.title if entry.presentation else "Unknown"
            })
        
        return result
    
    def get_history_stats(self) -> Dict[str, Any]:
        '''Get statistics about history entries'''
        total = self.db.query(History).count()
        by_action = {}
        by_status = {}
        
        for action in ["created", "generated", "exported", "downloaded", "deleted"]:
            count = self.db.query(History).filter(History.action == action).count()
            if count > 0:
                by_action[action] = count
        
        for status in ["success", "failed", "pending"]:
            count = self.db.query(History).filter(History.status == status).count()
            if count > 0:
                by_status[status] = count
        
        return {
            "total": total,
            "by_action": by_action,
            "by_status": by_status
        }
    
    def delete_presentation_history(self, presentation_id: int) -> int:
        '''Delete all history entries for a presentation'''
        count = self.db.query(History).filter(
            History.presentation_id == presentation_id
        ).delete()
        self.db.commit()
        logger.info(f"Deleted {count} history entries for presentation {presentation_id}")
        return count
