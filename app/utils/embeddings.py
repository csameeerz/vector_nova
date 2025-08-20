from typing import List
import numpy as np
import asyncio
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Utility for generating text embeddings"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        # TODO: Initialize embedding model (OpenAI, sentence-transformers, etc.)
        self.model = None
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts"""
        try:
            # TODO: Implement actual embedding generation
            # This is a placeholder implementation
            
            logger.info(f"Generating embeddings for {len(texts)} texts")
            
            # Simulate embedding generation
            await asyncio.sleep(0.1)
            
            # Return mock embeddings
            embeddings = []
            for text in texts:
                # Generate a mock embedding vector
                embedding = np.random.normal(0, 1, self.dimension).tolist()
                embeddings.append(embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def generate_single_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Similarity calculation failed: {str(e)}")
            return 0.0
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        document_embeddings: List[List[float]], 
        top_k: int = 5
    ) -> List[tuple]:
        """Find the most similar documents to a query"""
        try:
            similarities = []
            
            for i, doc_embedding in enumerate(document_embeddings):
                similarity = self.calculate_similarity(query_embedding, doc_embedding)
                similarities.append((i, similarity))
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Return top k results
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Most similar search failed: {str(e)}")
            return []
    
    def batch_generate_embeddings(
        self, 
        texts: List[str], 
        batch_size: int = 32
    ) -> List[List[float]]:
        """Generate embeddings in batches"""
        try:
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                batch_embeddings = asyncio.run(self.generate_embeddings(batch))
                all_embeddings.extend(batch_embeddings)
                
                logger.info(f"Processed batch {i//batch_size + 1}/{(len(texts) + batch_size - 1)//batch_size}")
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Batch embedding generation failed: {str(e)}")
            raise
    
    def normalize_embeddings(self, embeddings: List[List[float]]) -> List[List[float]]:
        """Normalize embeddings to unit vectors"""
        try:
            normalized = []
            
            for embedding in embeddings:
                vec = np.array(embedding)
                norm = np.linalg.norm(vec)
                
                if norm > 0:
                    normalized_vec = (vec / norm).tolist()
                else:
                    normalized_vec = embedding
                
                normalized.append(normalized_vec)
            
            return normalized
            
        except Exception as e:
            logger.error(f"Embedding normalization failed: {str(e)}")
            return embeddings
