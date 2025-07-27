#!/usr/bin/env python3
"""
Logging configuration for Ask ET chatbot
"""

import logging
import logging.config
from pathlib import Path
from config import LOGGING_CONFIG, LOGS_DIR

def setup_logging():
    """Setup logging configuration"""
    # Ensure logs directory exists
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Configure logging
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Get logger
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    
    return logger

def get_logger(name: str = None):
    """Get a logger instance"""
    return logging.getLogger(name or __name__) 