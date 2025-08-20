import time
from typing import List, Dict, Any, Tuple
import asyncio

from app.services.vector_service import VectorService
from app.utils.embeddings import EmbeddingGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)


class SearchService:
    """Service for hybrid search operations"""
    
    def __init__(self):
        self.vector_service = VectorService()
        self.embedding_generator = EmbeddingGenerator()
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5, 
        search_type: str = "hybrid",
        user_id: int = None
    ) -> Tuple[List[Dict[str, Any]], int, float]:
        """Perform search based on query and search type"""
        start_time = time.time()
        
        try:
            if search_type == "semantic":
                results = await self._semantic_search(query, max_results)
            elif search_type == "keyword":
                results = await self._keyword_search(query, max_results)
            elif search_type == "hybrid":
                results = await self._hybrid_search(query, max_results)
            else:
                raise ValueError(f"Unsupported search type: {search_type}")
            
            search_time = time.time() - start_time
            
            logger.info(f"Search completed in {search_time:.3f}s for query: {query}")
            
            return results, len(results), search_time
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {str(e)}")
            raise
    
    async def _semantic_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embeddings([query])
            
            # Search similar documents
            results = await self.vector_service.search_similar(
                query_embedding[0], 
                limit=max_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            raise
    
    async def _keyword_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform keyword-based search"""
        try:
            # TODO: Implement keyword search
            # This could use Elasticsearch, PostgreSQL full-text search, etc.
            
            # For now, return mock results
            await asyncio.sleep(0.1)
            
            return [
                {
                    "document_id": "keyword_doc_1",
                    "chunk_id": "chunk_1",
                    "text": "Keyword search result...",
                    "score": 0.8,
                    "metadata": {"filename": "keyword_file.txt"}
                }
            ]
            
        except Exception as e:
            logger.error(f"Keyword search failed: {str(e)}")
            raise
    
    async def _hybrid_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and keyword search"""
        try:
            # Perform both searches
            semantic_results = await self._semantic_search(query, max_results)
            keyword_results = await self._keyword_search(query, max_results)
            
            # Combine and rank results
            combined_results = self._combine_results(semantic_results, keyword_results)
            
            # Return top results
            return combined_results[:max_results]
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            raise
    
    def _combine_results(
        self, 
        semantic_results: List[Dict[str, Any]], 
        keyword_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine and rank results from different search methods"""
        # Create a dictionary to track unique results
        unique_results = {}
        
        # Add semantic results with higher weight
        for result in semantic_results:
            doc_id = result["document_id"]
            if doc_id not in unique_results:
                unique_results[doc_id] = result
                unique_results[doc_id]["score"] *= 1.2  # Boost semantic results
        
        # Add keyword results
        for result in keyword_results:
            doc_id = result["document_id"]
            if doc_id in unique_results:
                # Average the scores if document appears in both
                unique_results[doc_id]["score"] = (
                    unique_results[doc_id]["score"] + result["score"]
                ) / 2
            else:
                unique_results[doc_id] = result
        
        # Sort by score and return
        sorted_results = sorted(
            unique_results.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )
        
        return sorted_results
    
    async def get_suggestions(self, query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        try:
            # TODO: Implement search suggestions
            # This could use query history, popular searches, etc.
            
            # For now, return mock suggestions
            suggestions = [
                f"{query} example",
                f"{query} tutorial",
                f"{query} guide",
                f"{query} documentation"
            ]
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Failed to get suggestions: {str(e)}")
            return []
