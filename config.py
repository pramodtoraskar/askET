#!/usr/bin/env python3
"""
Configuration settings for Ask ET chatbot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
VECTOR_STORE_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Vector Store Configuration
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH", str(VECTOR_STORE_DIR / "faiss_index"))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(LOGS_DIR / "ask_et.log"))

# Application Configuration
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))

# Data Paths
BLOG_METADATA_PATH = os.getenv("BLOG_METADATA_PATH", str(DATA_DIR / "blog_metadata.json"))
PROJECT_METADATA_PATH = os.getenv("PROJECT_METADATA_PATH", str(DATA_DIR / "project_metadata.json"))

# Validation
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if not GOOGLE_API_KEY:
        errors.append("GOOGLE_API_KEY is required")
    
    if not Path(BLOG_METADATA_PATH).exists():
        errors.append(f"Blog metadata file not found: {BLOG_METADATA_PATH}")
    
    if not Path(PROJECT_METADATA_PATH).exists():
        errors.append(f"Project metadata file not found: {PROJECT_METADATA_PATH}")
    
    return errors

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": LOG_LEVEL,
            "propagate": False
        }
    }
} 