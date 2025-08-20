import logging
import sys
from pathlib import Path
from app.config import settings

# Create logs directory if it doesn't exist
Path("logs").mkdir(exist_ok=True)


def setup_logging():
    """Setup application logging"""
    
    # Create logger
    logger = logging.getLogger("vector_nova")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Create file handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Set up FastAPI logging
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.handlers = []
    uvicorn_logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "vector_nova") -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)
