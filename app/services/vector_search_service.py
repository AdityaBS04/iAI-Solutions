"""
Vector Search Service
Handles vector database search operations for RAG functionality
"""

from typing import List, Dict, Any, Optional
from app.core.vector_store import VectorStoreManager
from app.core.embeddings import EmbeddingGenerator
from app.models.data_models import SearchQuery, VectorSearchResult
from app.utils.exceptions import SearchError
from config import settings

class VectorSearchService:
    """Service for vector-based search operations"""
    
    def __init__(self):
        self.vector_store = VectorStoreManager(persist_directory=settings.vector_db_path)
        self.embedding_generator = EmbeddingGenerator()
    
    def search_similar_invoices(self, 
                               query_embedding: List[float],
                               filters: Optional[Dict[str, str]] = None,
                               max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar invoices using vector similarity
        
        Args:
            query_embedding: Query vector embedding
            filters: Optional metadata filters
            max_results: Maximum number of results
            
        Returns:
            List of similar invoice documents
        """
        try:
            results = self.vector_store.search_similar(
                query_embedding=query_embedding,
                n_results=max_results,
                filters=filters
            )
            
            return results
            
        except Exception as e:
            raise SearchError(f"Vector search failed: {str(e)}")
    
    def search_by_text(self, 
                      query_text: str,
                      filters: Optional[Dict[str, str]] = None,
                      max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search invoices using text query (generates embedding automatically)
        
        Args:
            query_text: Text query to search for
            filters: Optional metadata filters
            max_results: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            # Generate embedding for query text
            query_embedding = self.embedding_generator.generate_embedding(query_text)
            
            # Perform vector search
            return self.search_similar_invoices(
                query_embedding=query_embedding,
                filters=filters,
                max_results=max_results
            )
            
        except Exception as e:
            raise SearchError(f"Text search failed: {str(e)}")
    
    def search_by_metadata(self, 
                          filters: Dict[str, str],
                          max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search invoices by metadata filters only (no vector similarity)
        
        Args:
            filters: Metadata filters to apply
            max_results: Maximum number of results
            
        Returns:
            List of matching documents
        """
        try:
            results = self.vector_store.search_by_metadata(
                filters=filters,
                n_results=max_results
            )
            
            return results
            
        except Exception as e:
            raise SearchError(f"Metadata search failed: {str(e)}")
    
    def search_by_employee(self, 
                          employee_name: str,
                          max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search invoices for a specific employee
        
        Args:
            employee_name: Name of employee
            max_results: Maximum number of results
            
        Returns:
            List of employee's invoices
        """
        return self.search_by_metadata(
            filters={"employee_name": employee_name},
            max_results=max_results
        )
    
    def search_by_status(self, 
                        status: str,
                        max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search invoices by reimbursement status
        
        Args:
            status: Reimbursement status to filter by
            max_results: Maximum number of results
            
        Returns:
            List of invoices with matching status
        """
        return self.search_by_metadata(
            filters={"status": status},
            max_results=max_results
        )
    
    def get_all_invoices(self, max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Get all stored invoices
        
        Args:
            max_results: Maximum number of results
            
        Returns:
            List of all stored invoices
        """
        return self.search_by_metadata(
            filters={},  # No filters = get all
            max_results=max_results
        )
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the search index
        
        Returns:
            Search index statistics
        """
        try:
            stats = self.vector_store.get_collection_stats()
            return {
                "total_documents": stats.get("document_count", 0),
                "collection_name": stats.get("collection_name", "unknown"),
                "status": stats.get("status", "unknown"),
                "embedding_model": self.embedding_generator.model_name
            }
            
        except Exception as e:
            return {
                "total_documents": 0,
                "collection_name": "unknown",
                "status": "error",
                "error": str(e),
                "embedding_model": "unknown"
            }