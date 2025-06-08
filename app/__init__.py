"""
App package for Invoice Reimbursement System
Contains all application logic including API endpoints, core services, and models
"""

from .api import invoice_router, chatbot_router
from .core import PDFProcessor, LLMClient, EmbeddingGenerator, VectorStoreManager
from .models import (
    InvoiceAnalysisRequest, ChatRequest, 
    InvoiceAnalysisResponse, ChatResponse, InvoiceData,
    InvoiceRecord, AnalysisResult, SearchQuery
)
from .services import InvoiceAnalysisService, ChatbotService, VectorSearchService
from .utils import FileUtils, setup_logging, ProcessingError, ChatError, SearchError

__version__ = "1.0.0"
__author__ = "AI/ML Intern"
__description__ = "Invoice Reimbursement System with LLM analysis and RAG chatbot"

__all__ = [
    # API routers
    "invoice_router",
    "chatbot_router",
    
    # Core components
    "PDFProcessor",
    "LLMClient", 
    "EmbeddingGenerator",
    "VectorStoreManager",
    
    # Models
    "InvoiceAnalysisRequest",
    "ChatRequest",
    "InvoiceAnalysisResponse", 
    "ChatResponse",
    "InvoiceData",
    "InvoiceRecord",
    "AnalysisResult",
    "SearchQuery",
    
    # Services
    "InvoiceAnalysisService",
    "ChatbotService",
    "VectorSearchService",
    
    # Utilities
    "FileUtils",
    "setup_logging",
    "ProcessingError",
    "ChatError", 
    "SearchError"
]