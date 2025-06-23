"""
LLM Client for Invoice Reimbursement System
Handles Gemini AI integration for invoice analysis and chatbot responses
"""

import google.generativeai as genai
from typing import Dict, List, Optional, Any
from config import settings

class LLMClient:
    """Handle Gemini LLM interactions"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key (uses settings if not provided)
        """
        api_key = api_key or settings.gemini_api_key
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.default_llm_model)
        self.generation_config = {
            "max_output_tokens": settings.max_tokens,
            "temperature": settings.temperature,
        }
    
    def analyze_invoice(self, invoice_text: str, policy_text: str, employee_name: str) -> Dict[str, Any]:
        """
        Analyze invoice against company policy using Gemini
        
        Args:
            invoice_text: Extracted text from invoice PDF
            policy_text: Company reimbursement policy text
            employee_name: Name of employee submitting invoice
            
        Returns:
            Analysis result with status and reasoning
        """
        
        prompt = f"""
You are an AI assistant analyzing employee expense reimbursements. 

COMPANY POLICY:
{policy_text}

EMPLOYEE INVOICE:
Employee: {employee_name}
Invoice Text: {invoice_text}

TASK: Analyze this invoice against the company policy and determine reimbursement status.

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "status": "Fully Reimbursed" | "Partially Reimbursed" | "Declined",
    "reason": "Detailed explanation of the decision",
    "reimbursable_amount": "Amount eligible for reimbursement",
    "total_amount": "Total invoice amount",
    "policy_violations": ["List any policy violations"],
    "compliance_notes": "Additional compliance information"
}}

Be thorough and explain your reasoning clearly.
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            # Parse response (simplified - should add JSON parsing)
            response_text = response.text
            
            # TODO: Add proper JSON parsing here
            return {
                "status": "Pending Analysis",
                "reason": "LLM analysis completed but needs JSON parsing",
                "raw_response": response_text,
                "reimbursable_amount": "0.00",
                "total_amount": "0.00",
                "policy_violations": [],
                "compliance_notes": "Analysis completed"
            }
            
        except Exception as e:
            return {
                "status": "Analysis Failed",
                "reason": f"LLM analysis error: {str(e)}",
                "reimbursable_amount": "0.00",
                "total_amount": "0.00",
                "policy_violations": ["Technical error"],
                "compliance_notes": "System error occurred"
            }
    
    def generate_chat_response(self, user_query: str, context_data: List[Dict], chat_history: List[Dict]) -> str:
        """
        Generate chatbot response using RAG context
        
        Args:
            user_query: User's question
            context_data: Retrieved invoice data from vector search
            chat_history: Previous conversation messages
            
        Returns:
            Generated response
        """
        
        # Build context from retrieved data
        context_text = ""
        if context_data:
            context_text = "\n".join([
                f"Invoice {item.get('invoice_id', 'Unknown')}: {item.get('summary', 'No summary')}"
                for item in context_data
            ])
        
        # Build chat history context
        history_text = ""
        if chat_history:
            recent_history = chat_history[-4:]  # Last 4 messages for context
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in recent_history
            ])
        
        prompt = f"""
You are a helpful AI assistant for an Invoice Reimbursement System. Answer user questions about processed invoices.

PREVIOUS CONVERSATION:
{history_text}

RELEVANT INVOICE DATA:
{context_text}

USER QUESTION: {user_query}

INSTRUCTIONS:
- Provide helpful, accurate responses about invoice data
- Use markdown formatting for better readability
- If no relevant data is found, politely explain and suggest alternatives
- Be conversational and helpful
- Reference specific invoice details when available

RESPONSE:
"""
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            return f"I apologize, but I encountered an error while processing your question: {str(e)}. Please try asking again or rephrase your question."
    
    def test_connection(self) -> bool:
        """
        Test Gemini API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_response = self.model.generate_content(
                "Hello, this is a test message. Please respond with 'Connection successful'."
            )
            return "successful" in test_response.text.lower()
            
        except Exception:
            return False