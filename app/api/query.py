from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.query import Query
from app.dependencies import get_current_active_user
from app.services.search_service import SearchService

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    max_results: int = 5
    search_type: str = "hybrid"  # hybrid, semantic, keyword


class QueryResponse(BaseModel):
    query: str
    results: List[dict]
    total_results: int
    search_time: float


@router.post("/search", response_model=QueryResponse)
async def search_documents(
    query_request: QueryRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search documents using the knowledge base"""
    try:
        search_service = SearchService()
        
        # Perform search
        results, total_results, search_time = await search_service.search(
            query=query_request.query,
            max_results=query_request.max_results,
            search_type=query_request.search_type,
            user_id=current_user.id
        )
        
        # Save query history
        query_record = Query(
            user_id=current_user.id,
            query_text=query_request.query,
            search_type=query_request.search_type,
            results_count=len(results)
        )
        db.add(query_record)
        db.commit()
        
        return QueryResponse(
            query=query_request.query,
            results=results,
            total_results=total_results,
            search_time=search_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )


@router.get("/history", response_model=List[dict])
async def get_query_history(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's query history"""
    queries = db.query(Query).filter(
        Query.user_id == current_user.id
    ).order_by(Query.created_at.desc()).offset(skip).limit(limit).all()
    
    return [
        {
            "id": query.id,
            "query_text": query.query_text,
            "search_type": query.search_type,
            "results_count": query.results_count,
            "created_at": query.created_at
        }
        for query in queries
    ]


@router.get("/suggestions")
async def get_search_suggestions(
    query: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get search suggestions based on partial query"""
    try:
        search_service = SearchService()
        suggestions = await search_service.get_suggestions(query)
        
        return {
            "query": query,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestions: {str(e)}"
        )


@router.post("/feedback")
async def submit_search_feedback(
    query_id: int,
    result_id: str,
    feedback_type: str,  # relevant, irrelevant, helpful
    feedback_text: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit feedback for search results"""
    # Find the query
    query = db.query(Query).filter(
        Query.id == query_id,
        Query.user_id == current_user.id
    ).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found"
        )
    
    # Save feedback (you might want to create a separate feedback model)
    # For now, we'll just return success
    return {
        "message": "Feedback submitted successfully",
        "query_id": query_id,
        "result_id": result_id,
        "feedback_type": feedback_type
    }
