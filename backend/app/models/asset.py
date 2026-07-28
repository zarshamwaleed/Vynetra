from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    presentation_id = Column(Integer, ForeignKey("presentations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    path = Column(String(512), nullable=False)
    size = Column(Float, nullable=True)
    mime_type = Column(String(100), nullable=True)
    asset_metadata = Column(JSON, nullable=True)  # Changed from 'metadata' to 'asset_metadata'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    presentation = relationship("Presentation", back_populates="assets")
