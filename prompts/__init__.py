"""
Prompts package for Invoice Reimbursement System
Contains system prompts for LLM interactions
"""

from .invoice_analysis_prompt import InvoiceAnalysisPrompt
from .chatbot_prompt import ChatbotPrompt

__all__ = [
    "InvoiceAnalysisPrompt",
    "ChatbotPrompt"
]