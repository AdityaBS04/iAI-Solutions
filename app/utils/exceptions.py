"""
Custom exceptions for Invoice Reimbursement System
"""

class InvoiceSystemError(Exception):
    """Base exception for invoice system errors"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)

class ProcessingError(InvoiceSystemError):
    """Exception raised during invoice processing"""
    def __init__(self, message: str, error_code: str = "PROCESSING_ERROR"):
        super().__init__(message, error_code)

class ChatError(InvoiceSystemError):
    """Exception raised during chat processing"""
    def __init__(self, message: str, error_code: str = "CHAT_ERROR"):
        super().__init__(message, error_code)

class SearchError(InvoiceSystemError):
    """Exception raised during vector search operations"""
    def __init__(self, message: str, error_code: str = "SEARCH_ERROR"):
        super().__init__(message, error_code)

class FileError(InvoiceSystemError):
    """Exception raised during file operations"""
    def __init__(self, message: str, error_code: str = "FILE_ERROR"):
        super().__init__(message, error_code)

class ValidationError(InvoiceSystemError):
    """Exception raised during data validation"""
    def __init__(self, message: str, error_code: str = "VALIDATION_ERROR"):
        super().__init__(message, error_code)

class LLMError(InvoiceSystemError):
    """Exception raised during LLM operations"""
    def __init__(self, message: str, error_code: str = "LLM_ERROR"):
        super().__init__(message, error_code)

class VectorStoreError(InvoiceSystemError):
    """Exception raised during vector store operations"""
    def __init__(self, message: str, error_code: str = "VECTOR_STORE_ERROR"):
        super().__init__(message, error_code)