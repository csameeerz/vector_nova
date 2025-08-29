from sqlalchemy import Column, Integer, DateTime, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from app.database import Base


class QueryStatus(PyEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    ANSWERED = "ANSWERED"
    FAILED = "FAILED"


class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    status = Column(Enum(QueryStatus), default=QueryStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
