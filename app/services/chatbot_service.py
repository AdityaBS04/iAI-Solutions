"""
Chatbot Service
Business logic for RAG-based chatbot interactions
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.llm_client import LLMClient
from app.core.embeddings import EmbeddingGenerator
from app.services.vector_search_service import VectorSearchService
from app.models.data_models import ChatContext, SearchQuery
from app.utils.exceptions import ChatError

class ChatbotService:
    """Service for handling chatbot interactions and RAG responses"""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.embedding_generator = EmbeddingGenerator()
        self.vector_search = VectorSearchService()
        self.chat_sessions: Dict[str, ChatContext] = {}
    
    async def process_chat_message(self, 
                                 message: str, 
                                 session_id: str = "default") -> Dict[str, Any]:
        """
        Process user chat message and generate response
        
        Args:
            message: User's message
            session_id: Chat session identifier
            
        Returns:
            Chat response with context
        """
        try:
            # Initialize session if not exists
            if session_id not in self.chat_sessions:
                self.chat_sessions[session_id] = ChatContext(session_id=session_id)
            
            session = self.chat_sessions[session_id]
            
            # Add user message to history
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat()
            }
            session.messages.append(user_message)
            
            # Perform vector search for relevant context
            context_data = await self._retrieve_context(message)
            
            # Generate response using LLM
            response = self.llm_client.generate_chat_response(
                user_query=message,
                context_data=context_data,
                chat_history=session.messages[-10:]  # Last 10 messages for context
            )
            
            # Add assistant response to history
            assistant_message = {
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
            session.messages.append(assistant_message)
            
            # Update session context
            session.last_query = message
            session.retrieved_documents = context_data
            
            return {
                "response": response,
                "session_id": session_id,
                "query": message,
                "timestamp": datetime.now().isoformat(),
                "context_used": len(context_data) > 0,
                "retrieved_count": len(context_data)
            }
            
        except Exception as e:
            raise ChatError(f"Chat processing failed: {str(e)}")
    
    async def _retrieve_context(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context from vector database
        
        Args:
            query: User query
            
        Returns:
            List of relevant documents
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_generator.generate_embedding(query)
            
            # Extract filters from query (simple keyword matching)
            filters = self._extract_filters_from_query(query)
            
            # Search vector database
            search_results = self.vector_search.search_similar_invoices(
                query_embedding=query_embedding,
                filters=filters,
                max_results=5
            )
            
            # Format results for LLM context
            context_data = []
            for result in search_results:
                context_item = {
                    "invoice_id": result.get("metadata", {}).get("invoice_id", "Unknown"),
                    "employee_name": result.get("metadata", {}).get("employee_name", "Unknown"),
                    "status": result.get("metadata", {}).get("status", "Unknown"),
                    "amount": result.get("metadata", {}).get("amount", "0.00"),
                    "date": result.get("metadata", {}).get("date", "Unknown"),
                    "summary": result.get("document", "No details available"),
                    "similarity": result.get("distance", 0.0)
                }
                context_data.append(context_item)
            
            return context_data
            
        except Exception as e:
            print(f"Context retrieval error: {str(e)}")
            return []  # Return empty context on error
    
    def _extract_filters_from_query(self, query: str) -> Dict[str, str]:
        """
        Extract metadata filters from user query using simple keyword matching
        
        Args:
            query: User query string
            
        Returns:
            Dictionary of extracted filters
        """
        filters = {}
        query_lower = query.lower()
        
        # Extract employee names (simple approach - look for names after "for" or "by")
        import re
        
        # Look for employee names
        name_patterns = [
            r"for\s+([A-Za-z\s]+?)(?:\s|$|,|\?)",
            r"by\s+([A-Za-z\s]+?)(?:\s|$|,|\?)",
            r"employee\s+([A-Za-z\s]+?)(?:\s|$|,|\?)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query_lower)
            if match:
                employee_name = match.group(1).strip()
                if len(employee_name) > 1:  # Avoid single letters
                    filters["employee_name"] = employee_name.title()
                break
        
        # Extract status keywords
        status_keywords = {
            "approved": "Fully Reimbursed",
            "declined": "Declined", 
            "rejected": "Declined",
            "partial": "Partially Reimbursed",
            "pending": "Pending Analysis"
        }
        
        for keyword, status in status_keywords.items():
            if keyword in query_lower:
                filters["status"] = status
                break
        
        return filters
    
    def get_chat_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get chat history for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Chat history data
        """
        if session_id in self.chat_sessions:
            session = self.chat_sessions[session_id]
            return {
                "session_id": session_id,
                "history": session.messages,
                "message_count": len(session.messages),
                "last_query": session.last_query
            }
        else:
            return {
                "session_id": session_id,
                "history": [],
                "message_count": 0,
                "last_query": None
            }
    
    def clear_chat_history(self, session_id: str) -> bool:
        """
        Clear chat history for a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if cleared successfully
        """
        if session_id in self.chat_sessions:
            del self.chat_sessions[session_id]
            return True
        return False
    
    def get_active_sessions(self) -> List[str]:
        """
        Get list of active session IDs
        
        Returns:
            List of active session identifiers
        """
        return list(self.chat_sessions.keys())