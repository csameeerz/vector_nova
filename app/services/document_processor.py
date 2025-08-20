import asyncio
from typing import List
from fastapi import UploadFile
import os
from pathlib import Path

from app.utils.chunking import TextChunker
from app.utils.embeddings import EmbeddingGenerator
from app.services.vector_service import VectorService
from app.core.logging import get_logger

logger = get_logger(__name__)


class DocumentProcessor:
    """Service for processing and ingesting documents"""
    
    def __init__(self):
        self.chunker = TextChunker()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_service = VectorService()
        
        # Create upload directory
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
    
    async def process_document(self, document_id: str, file: UploadFile) -> dict:
        """Process a document and store it in the vector database"""
        try:
            # Save file temporarily
            file_path = self.upload_dir / f"{document_id}_{file.filename}"
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Extract text from document
            text_content = await self._extract_text(file_path, file.content_type)
            
            # Chunk the text
            chunks = self.chunker.chunk_text(text_content)
            
            # Generate embeddings for chunks
            embeddings = await self.embedding_generator.generate_embeddings(
                [chunk["text"] for chunk in chunks]
            )
            
            # Store in vector database
            await self.vector_service.store_document(
                document_id=document_id,
                chunks=chunks,
                embeddings=embeddings,
                metadata={
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "file_size": len(content)
                }
            )
            
            # Clean up temporary file
            os.remove(file_path)
            
            logger.info(f"Successfully processed document {document_id}")
            return {
                "document_id": document_id,
                "chunks_count": len(chunks),
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {str(e)}")
            raise
    
    async def _extract_text(self, file_path: Path, content_type: str) -> str:
        """Extract text from different file types"""
        try:
            if content_type == "text/plain":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            
            elif content_type == "application/pdf":
                # TODO: Implement PDF text extraction
                # You can use PyPDF2, pdfplumber, or other libraries
                return "PDF text extraction not implemented yet"
            
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # TODO: Implement DOCX text extraction
                # You can use python-docx library
                return "DOCX text extraction not implemented yet"
            
            elif content_type == "text/markdown":
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
                
        except Exception as e:
            logger.error(f"Failed to extract text from {file_path}: {str(e)}")
            raise
