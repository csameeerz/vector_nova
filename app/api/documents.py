from fastapi import APIRouter, Depends, HTTPException
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import uuid

from app.database import get_db
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.user import User
from app.dependencies import get_current_active_user

router = APIRouter()


class CreateDocumentRequest(BaseModel):
    title: str
    content: str


@router.post("/add")
def create_document(
    payload: CreateDocumentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    document = Document(
        id=str(uuid.uuid4()),
        title=payload.title,
        content=payload.content,
        document_type=DocumentType.TEXT_SNIPPET,
        status=DocumentStatus.ADDED,
        added_by=current_user.id,
    )
    db.add(document)
    db.commit()
    
    background_tasks.add_task(_enqueue_document_processing, document.id)
    
    return {
        "id": document.id,
        "title": document.title,
        "status": document.status.value,
    }


def _enqueue_document_processing(document_id: str) -> None:
    # TODO: Send a Celery task to process and index the document in Qdrant
    # Example: celery_app.send_task("tasks.process_document", args=[document_id])
    return None


@router.get("/list", response_model=List[dict])
def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    documents = db.query(Document).filter(
        Document.added_by == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "content": doc.content,
            "document_type": doc.document_type.value,
            "status": doc.status.value,
            "added_at": doc.added_at,
        }
        for doc in documents
    ]


@router.get("/{document_id}/get")
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.added_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": document.id,
        "title": document.title,
        "content": document.content,
        "document_type": document.document_type.value,
        "status": document.status.value,
        "added_at": document.added_at,
    }


@router.delete("/{document_id}/delete")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.added_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
