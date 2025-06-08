"""
File handling utilities for Invoice Reimbursement System
"""

import os
import shutil
import tempfile
import zipfile
from typing import List, Optional
from pathlib import Path
from config import settings

class FileUtils:
    """Utility class for file operations"""
    
    @staticmethod
    def validate_file_size(file_path: str, max_size_mb: Optional[int] = None) -> bool:
        """
        Validate file size against maximum allowed size
        
        Args:
            file_path: Path to file
            max_size_mb: Maximum size in MB (uses settings default if None)
            
        Returns:
            True if file size is valid
        """
        max_size = (max_size_mb or settings.max_file_size_mb) * 1024 * 1024
        
        try:
            file_size = os.path.getsize(file_path)
            return file_size <= max_size
        except OSError:
            return False
    
    @staticmethod
    def validate_file_extension(file_path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """
        Validate file extension against allowed types
        
        Args:
            file_path: Path to file
            allowed_extensions: List of allowed extensions (uses settings default if None)
            
        Returns:
            True if extension is allowed
        """
        allowed = allowed_extensions or settings.allowed_file_types
        file_extension = Path(file_path).suffix.lower().lstrip('.')
        
        return file_extension in [ext.lower() for ext in allowed]
    
    @staticmethod
    def create_temp_directory() -> str:
        """
        Create a temporary directory for file processing
        
        Returns:
            Path to temporary directory
        """
        return tempfile.mkdtemp()
    
    @staticmethod
    def cleanup_temp_directory(temp_dir: str) -> bool:
        """
        Clean up temporary directory
        
        Args:
            temp_dir: Path to temporary directory
            
        Returns:
            True if cleanup successful
        """
        try:
            shutil.rmtree(temp_dir)
            return True
        except Exception:
            return False
    
    @staticmethod
    def extract_zip_file(zip_path: str, extract_to: str) -> List[str]:
        """
        Extract ZIP file and return list of extracted files
        
        Args:
            zip_path: Path to ZIP file
            extract_to: Directory to extract to
            
        Returns:
            List of extracted file paths
        """
        extracted_files = []
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
                
                # Get list of extracted files
                for root, dirs, files in os.walk(extract_to):
                    for file in files:
                        extracted_files.append(os.path.join(root, file))
                        
            return extracted_files
            
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file format")
        except Exception as e:
            raise Exception(f"ZIP extraction failed: {str(e)}")
    
    @staticmethod
    def filter_pdf_files(file_paths: List[str]) -> List[str]:
        """
        Filter list to only include PDF files
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of PDF file paths only
        """
        return [path for path in file_paths if path.lower().endswith('.pdf')]
    
    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get information about a file
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        try:
            stat = os.stat(file_path)
            return {
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "extension": Path(file_path).suffix.lower(),
                "modified": stat.st_mtime,
                "exists": True
            }
        except OSError:
            return {
                "name": os.path.basename(file_path),
                "exists": False,
                "error": "File not found or inaccessible"
            }
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Ensure directory exists, create if it doesn't
        
        Args:
            directory_path: Path to directory
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception:
            return False
    
    @staticmethod
    def safe_filename(filename: str) -> str:
        """
        Create a safe filename by removing/replacing problematic characters
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        # Remove or replace problematic characters
        import re
        
        # Keep only alphanumeric, dots, hyphens, and underscores
        safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Remove multiple consecutive underscores/dots
        safe_name = re.sub(r'[_\.]{2,}', '_', safe_name)
        
        # Ensure it doesn't start with a dot
        safe_name = safe_name.lstrip('.')
        
        # Limit length
        if len(safe_name) > 100:
            name_part, ext = os.path.splitext(safe_name)
            safe_name = name_part[:95] + ext
        
        return safe_name or "unnamed_file"