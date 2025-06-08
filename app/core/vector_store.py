"""
Vector Store Manager for Invoice Reimbursement System
Handles ChromaDB operations for storing and searching invoice embeddings
"""

import chromadb
from typing import Dict, List, Any, Optional
import uuid
from config import settings

class VectorStoreManager:
    """Manage vector database operations using ChromaDB"""
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        Initialize ChromaDB client
        
        Args:
            persist_directory: Directory to persist database (optional)
        """
        try:
            if persist_directory:
                self.client = chromadb.PersistentClient(path=persist_directory)
            else:
                self.client = chromadb.Client()
            
            # Get or create collection for invoices
            self.collection = self.client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"description": "Invoice analysis embeddings"}
            )
            
            print(f"✓ Vector store initialized with collection: {settings.collection_name}")
            
        except Exception as e:
            raise Exception(f"Vector store initialization failed: {str(e)}")
    
    def add_invoice(self, invoice_data: Dict[str, Any], embedding: List[float]) -> str:
        """
        Add invoice analysis to vector store
        
        Args:
            invoice_data: Invoice information and analysis results
            embedding: Vector embedding for the invoice
            
        Returns:
            Document ID of stored invoice
        """
        try:
            # Generate unique ID for the invoice
            doc_id = str(uuid.uuid4())
            
            # Prepare metadata (ChromaDB requires string values)
            metadata = {
                "invoice_id": str(invoice_data.get("invoice_id", "unknown")),
                "employee_name": str(invoice_data.get("employee_name", "unknown")),
                "status": str(invoice_data.get("status", "unknown")),
                "date": str(invoice_data.get("date", "unknown")),
                "amount": str(invoice_data.get("reimbursable_amount", "0.00")),
                "file_name": str(invoice_data.get("file_name", "unknown"))
            }
            
            # Prepare document text (combination of relevant fields)
            document_text = f"""
            Invoice ID: {invoice_data.get('invoice_id', 'N/A')}
            Employee: {invoice_data.get('employee_name', 'N/A')}
            Status: {invoice_data.get('status', 'N/A')}
            Reason: {invoice_data.get('reason', 'N/A')}
            Amount: {invoice_data.get('reimbursable_amount', 'N/A')}
            """.strip()
            
            # Add to collection
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[document_text],
                metadatas=[metadata]
            )
            
            return doc_id
            
        except Exception as e:
            raise Exception(f"Failed to add invoice to vector store: {str(e)}")
    
    def search_similar(self, query_embedding: List[float], n_results: int = 5, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Search for similar invoices using vector similarity
        
        Args:
            query_embedding: Query vector embedding
            n_results: Number of results to return
            filters: Metadata filters (optional)
            
        Returns:
            List of similar invoice documents
        """
        try:
            # Prepare where clause for filtering
            where_clause = None
            if filters:
                where_clause = {}
                for key, value in filters.items():
                    if value is not None and value != "":
                        where_clause[key] = str(value)
            
            # Perform vector search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    result = {
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Vector search failed: {str(e)}")
    
    def search_by_metadata(self, filters: Dict[str, str], n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search invoices by metadata filters only
        
        Args:
            filters: Metadata filters
            n_results: Number of results to return
            
        Returns:
            List of matching invoice documents
        """
        try:
            # Convert filters to string values
            where_clause = {}
            for key, value in filters.items():
                if value is not None and value != "":
                    where_clause[key] = str(value)
            
            if not where_clause:
                # Get all documents if no filters
                results = self.collection.get()
            else:
                results = self.collection.get(
                    where=where_clause,
                    limit=n_results
                )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    result = {
                        "id": results['ids'][i],
                        "document": results['documents'][i] if results['documents'] else None,
                        "metadata": results['metadatas'][i] if results['metadatas'] else {}
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            raise Exception(f"Metadata search failed: {str(e)}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the collection
        
        Returns:
            Collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.collection_name,
                "document_count": count,
                "status": "healthy"
            }
            
        except Exception as e:
            return {
                "collection_name": settings.collection_name,
                "document_count": 0,
                "status": "error",
                "error": str(e)
            }
    
    def delete_invoice(self, doc_id: str) -> bool:
        """
        Delete invoice from vector store
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[doc_id])
            return True
            
        except Exception as e:
            print(f"Failed to delete invoice {doc_id}: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from collection
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(settings.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=settings.collection_name,
                metadata={"description": "Invoice analysis embeddings"}
            )
            return True
            
        except Exception as e:
            print(f"Failed to clear collection: {str(e)}")
            return False