"""
API Dependencies for Invoice Reimbursement System
Provides dependency injection for FastAPI endpoints
"""

from fastapi import Depends, HTTPException, UploadFile
from functools import lru_cache
import os
from config import settings

# Global instances (will be initialized once)
_vector_store = None
_llm_client = None

@lru_cache()
def get_settings():
    """Get application settings (cached)"""
    return settings

def get_vector_store():
    """
    Dependency to get vector store instance
    Initializes ChromaDB if not already done
    """
    global _vector_store
    
    if _vector_store is None:
        try:
            import chromadb
            _vector_store = chromadb.Client()
            print("✓ Vector store dependency initialized")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Vector store initialization failed: {str(e)}"
            )
    
    return _vector_store

def get_llm_client():
    """
    Dependency to get LLM client instance
    Initializes Gemini client if not already done
    """
    global _llm_client
    
    if _llm_client is None:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            _llm_client = genai
            print("✓ LLM client dependency initialized")
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"LLM client initialization failed: {str(e)}"
            )
    
    return _llm_client

def validate_file_size(file: UploadFile) -> UploadFile:
    """
    Dependency to validate uploaded file size
    """
    if hasattr(file, 'size') and file.size:
        max_size = settings.max_file_size_mb * 1024 * 1024  # Convert MB to bytes
        
        if file.size > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size {file.size} bytes exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )
    
    return file

def validate_file_type(file: UploadFile, allowed_extensions: list) -> UploadFile:
    """
    Dependency to validate file type
    """
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required"
        )
    
    file_extension = file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type .{file_extension} not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )
    
    return file

def get_current_session_id() -> str:
    """
    Dependency to get or create session ID
    For now returns default, can be enhanced with JWT tokens
    """
    return "default_session"