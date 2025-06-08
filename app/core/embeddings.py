"""
Embedding Generation for Invoice Reimbursement System
Creates vector embeddings for text content using sentence-transformers
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import numpy as np
from config import settings

class EmbeddingGenerator:
    """Generate embeddings for text content"""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize embedding model
        
        Args:
            model_name: Name of sentence transformer model
        """
        self.model_name = model_name or settings.embedding_model
        try:
            self.model = SentenceTransformer(self.model_name)
            print(f"✓ Embedding model loaded: {self.model_name}")
        except Exception as e:
            raise Exception(f"Failed to load embedding model: {str(e)}")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of embedding values
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            embedding = self.model.encode(text.strip())
            return embedding.tolist()
            
        except Exception as e:
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        try:
            if not texts:
                return []
            
            # Filter out empty texts
            clean_texts = [text.strip() for text in texts if text and text.strip()]
            
            if not clean_texts:
                raise ValueError("No valid texts provided")
            
            embeddings = self.model.encode(clean_texts)
            return embeddings.tolist()
            
        except Exception as e:
            raise Exception(f"Batch embedding generation failed: {str(e)}")
    
    def create_invoice_embedding(self, invoice_data: Dict[str, Any]) -> List[float]:
        """
        Create embedding specifically for invoice data
        
        Args:
            invoice_data: Invoice information dictionary
            
        Returns:
            Invoice embedding vector
        """
        try:
            # Combine relevant invoice fields for embedding
            text_parts = []
            
            if 'raw_text' in invoice_data:
                text_parts.append(invoice_data['raw_text'])
            
            if 'reason' in invoice_data:
                text_parts.append(f"Reason: {invoice_data['reason']}")
            
            if 'status' in invoice_data:
                text_parts.append(f"Status: {invoice_data['status']}")
            
            if 'employee_name' in invoice_data:
                text_parts.append(f"Employee: {invoice_data['employee_name']}")
            
            # Combine all text parts
            combined_text = " ".join(text_parts)
            
            return self.generate_embedding(combined_text)
            
        except Exception as e:
            raise Exception(f"Invoice embedding creation failed: {str(e)}")
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score (0-1, higher is more similar)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
            
        except Exception as e:
            raise Exception(f"Similarity computation failed: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the embedding model
        
        Returns:
            Model information dictionary
        """
        try:
            return {
                "model_name": self.model_name,
                "embedding_dimension": self.model.get_sentence_embedding_dimension(),
                "max_seq_length": getattr(self.model, 'max_seq_length', 'Unknown'),
                "model_type": type(self.model).__name__
            }
        except Exception as e:
            return {
                "model_name": self.model_name,
                "error": str(e)
            }