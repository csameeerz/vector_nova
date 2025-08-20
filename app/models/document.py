from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    """Document model"""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    uploaded_by = Column(Integer, nullable=False)  # Foreign key to users.id
    status = Column(String, default="processing")  # processing, processed, failed
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)  # Store document metadata
    content_summary = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
