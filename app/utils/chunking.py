import re
from typing import List, Dict, Any
from app.core.logging import get_logger

logger = get_logger(__name__)


class TextChunker:
    """Utility for chunking text into smaller pieces"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """Split text into overlapping chunks"""
        try:
            # Clean the text
            text = self._clean_text(text)
            
            # Split into sentences first
            sentences = self._split_into_sentences(text)
            
            chunks = []
            current_chunk = ""
            chunk_id = 0
            
            for sentence in sentences:
                # If adding this sentence would exceed chunk size
                if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                    # Save current chunk
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": current_chunk.strip(),
                        "start_char": len(" ".join(chunks)) if chunks else 0,
                        "end_char": len(" ".join(chunks)) + len(current_chunk.strip())
                    })
                    chunk_id += 1
                    
                    # Start new chunk with overlap
                    if self.overlap > 0:
                        # Get last few sentences for overlap
                        overlap_text = self._get_overlap_text(current_chunk)
                        current_chunk = overlap_text + " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    current_chunk += " " + sentence if current_chunk else sentence
            
            # Add the last chunk if it has content
            if current_chunk.strip():
                chunks.append({
                    "id": f"chunk_{chunk_id}",
                    "text": current_chunk.strip(),
                    "start_char": len(" ".join([c["text"] for c in chunks])) if chunks else 0,
                    "end_char": len(" ".join([c["text"] for c in chunks])) + len(current_chunk.strip())
                })
            
            logger.info(f"Created {len(chunks)} chunks from text of length {len(text)}")
            return chunks
            
        except Exception as e:
            logger.error(f"Text chunking failed: {str(e)}")
            # Return the entire text as one chunk if chunking fails
            return [{
                "id": "chunk_0",
                "text": text,
                "start_char": 0,
                "end_char": len(text)
            }]
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', '', text)
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting using punctuation
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the last part of text for overlap"""
        words = text.split()
        if len(words) <= 10:  # If text is short, return all
            return text
        
        # Return last 10 words
        return " ".join(words[-10:])
    
    def chunk_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """Split text by paragraphs"""
        try:
            paragraphs = text.split('\n\n')
            chunks = []
            
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    chunks.append({
                        "id": f"paragraph_{i}",
                        "text": paragraph.strip(),
                        "type": "paragraph"
                    })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Paragraph chunking failed: {str(e)}")
            return [{"id": "paragraph_0", "text": text, "type": "paragraph"}]
    
    def chunk_by_sections(self, text: str) -> List[Dict[str, Any]]:
        """Split text by sections (headers)"""
        try:
            # Look for common header patterns
            header_pattern = r'^(#{1,6}|\d+\.|\w+\.)\s+(.+)$'
            
            sections = []
            current_section = {"title": "Introduction", "content": "", "level": 0}
            
            lines = text.split('\n')
            
            for line in lines:
                header_match = re.match(header_pattern, line.strip())
                
                if header_match:
                    # Save current section
                    if current_section["content"].strip():
                        sections.append(current_section)
                    
                    # Start new section
                    current_section = {
                        "title": header_match.group(2),
                        "content": "",
                        "level": len(header_match.group(1)) if header_match.group(1).startswith('#') else 1
                    }
                else:
                    current_section["content"] += line + "\n"
            
            # Add the last section
            if current_section["content"].strip():
                sections.append(current_section)
            
            # Convert to chunks format
            chunks = []
            for i, section in enumerate(sections):
                chunks.append({
                    "id": f"section_{i}",
                    "text": f"{section['title']}\n\n{section['content']}",
                    "type": "section",
                    "title": section["title"],
                    "level": section["level"]
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Section chunking failed: {str(e)}")
            return [{"id": "section_0", "text": text, "type": "section"}]
