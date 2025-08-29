from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, Enum, ForeignKey
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base


class DocumentStatus(PyEnum):
    ADDED = "ADDED"
    USED = "USED"
    FAILED = "FAILED"


class DocumentType(PyEnum):
    TEXT_SNIPPET = "TEXT_SNIPPET"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.ADDED, nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    added_by = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
