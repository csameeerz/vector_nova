from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Query(Base):
    """Query history model"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Foreign key to users.id
    query_text = Column(Text, nullable=False)
    search_type = Column(String, default="hybrid")  # hybrid, semantic, keyword
    results_count = Column(Integer, default=0)
    search_time = Column(Integer, nullable=True)  # Search time in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())
