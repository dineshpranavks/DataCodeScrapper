import logging
import sys
from config import LOG_LEVEL, LOG_FILE

def setup_logger(name: str) -> logging.Logger:
    """
    Setup and return a logger with file and stream handlers.
    """
    logger = logging.getLogger(name)
    
    # Only configure if no handlers are present to avoid duplication
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File Handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        
        # Stream Handler (Stdout)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
    return logger

def clean_text(text: str) -> str:
    """Helper to clean scraped text by removing extra whitespaces."""
    return " ".join(text.split())
