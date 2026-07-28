from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Presentation(Base):
    __tablename__ = "presentations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    style = Column(String(50), default="modern")
    slide_count = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    
    slides = relationship("Slide", back_populates="presentation", cascade="all, delete-orphan")
    assets = relationship("Asset", back_populates="presentation", cascade="all, delete-orphan")
    history = relationship("History", back_populates="presentation", cascade="all, delete-orphan")
