from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.database import get_db
from app.models.document import Document
from app.models.user import User
from app.dependencies import get_current_active_user
from app.services.document_processor import DocumentProcessor

router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process a document"""
    # Validate file type
    if not file.filename or not any(
        file.filename.endswith(ext) for ext in [".pdf", ".txt", ".docx", ".md"]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Supported: .pdf, .txt, .docx, .md"
        )
    
    # Create document record
    document = Document(
        id=str(uuid.uuid4()),
        filename=file.filename,
        content_type=file.content_type,
        uploaded_by=current_user.id,
        status="processing"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document (async)
    try:
        processor = DocumentProcessor()
        await processor.process_document(document.id, file)
        
        document.status = "processed"
        db.commit()
        
        return {
            "message": "Document uploaded and processed successfully",
            "document_id": document.id,
            "filename": document.filename
        }
    except Exception as e:
        document.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


@router.get("/", response_model=List[dict])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all documents for the current user"""
    documents = db.query(Document).filter(
        Document.uploaded_by == current_user.id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "content_type": doc.content_type,
            "status": doc.status,
            "uploaded_at": doc.uploaded_at,
            "processed_at": doc.processed_at
        }
        for doc in documents
    ]


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.uploaded_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return {
        "id": document.id,
        "filename": document.filename,
        "content_type": document.content_type,
        "status": document.status,
        "uploaded_at": document.uploaded_at,
        "processed_at": document.processed_at,
        "metadata": document.metadata
    }


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.uploaded_by == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
