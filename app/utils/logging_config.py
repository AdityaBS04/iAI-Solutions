"""
Logging configuration for Invoice Reimbursement System
"""

import logging
import logging.handlers
import os
from datetime import datetime
from config import settings

def setup_logging(log_level: str = None, log_file: str = None) -> logging.Logger:
    """
    Set up logging configuration for the application
    
    Args:
        log_level: Logging level (uses settings default if None)
        log_file: Log file path (uses settings default if None)
        
    Returns:
        Configured logger instance
    """
    
    # Use settings defaults if not provided
    level = log_level or settings.log_level
    file_path = log_file or settings.log_file
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger("invoice_system")
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if file_path:
        try:
            # Ensure log directory exists
            log_dir = os.path.dirname(file_path)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Rotating file handler (10MB max, keep 5 backups)
            file_handler = logging.handlers.RotatingFileHandler(
                file_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Failed to set up file logging: {str(e)}")
    
    # Log startup message
    logger.info("Logging system initialized")
    logger.info(f"Log level: {level}")
    logger.info(f"Log file: {file_path if file_path else 'Console only'}")
    
    return logger

def get_logger(name: str = "invoice_system") -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

def log_request(endpoint: str, method: str, user_data: dict = None):
    """
    Log API request information
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
        user_data: Optional user data to log
    """
    logger = get_logger()
    
    log_data = {
        "endpoint": endpoint,
        "method": method,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_data:
        log_data.update(user_data)
    
    logger.info(f"API Request: {log_data}")

def log_processing_time(operation: str, duration: float, details: dict = None):
    """
    Log processing time for operations
    
    Args:
        operation: Name of operation
        duration: Duration in seconds
        details: Optional additional details
    """
    logger = get_logger()
    
    log_data = {
        "operation": operation,
        "duration_seconds": round(duration, 3),
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    logger.info(f"Processing Time: {log_data}")

def log_error(error: Exception, context: str = None, extra_data: dict = None):
    """
    Log error information with context
    
    Args:
        error: Exception that occurred
        context: Context where error occurred
        extra_data: Additional data to log
    """
    logger = get_logger()
    
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat()
    }
    
    if context:
        log_data["context"] = context
    
    if extra_data:
        log_data.update(extra_data)
    
    logger.error(f"Error: {log_data}", exc_info=True)