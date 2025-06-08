import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug_mode: bool = True
    
    # Google Gemini Configuration
    gemini_api_key: str = ""
    
    # Vector Database Configuration
    vector_db_path: str = "./data/vector_db"
    collection_name: str = "invoice_analysis"
    
    # Embedding Model
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # LLM Configuration
    default_llm_model: str = "gemini-pro"
    max_tokens: int = 1000
    temperature: float = 0.1
    
    # File Upload Limits
    max_file_size_mb: int = 50
    allowed_file_types: List[str] = ["pdf", "zip"]
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()