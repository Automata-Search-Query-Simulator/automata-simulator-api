"""Logging configuration for automata simulator API."""
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logger(name: str = "automata_simulator", log_level: str = "INFO") -> logging.Logger:
    """
    Set up and configure logger for the application.
    
    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Don't add handlers if they already exist (avoid duplicates)
    if logger.handlers:
        return logger
    
    # Set log level
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler only (Vercel environment is read-only)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Only add file handler if not in serverless environment
    # Check for writable filesystem (local development)
    try:
        log_dir = Path(__file__).parent / "logs"
        if log_dir.exists() or os.access(Path(__file__).parent, os.W_OK):
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / "automata_simulator.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding="utf-8"
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # Silently skip file logging in read-only environments (like Vercel)
        pass
    
    return logger


def get_logger(name: str = "automata_simulator") -> logging.Logger:
    """
    Get logger instance, creating it if it doesn't exist.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Determine log level from environment or default to INFO
        log_level = os.environ.get("LOG_LEVEL", "INFO")
        # Use DEBUG level if Flask debug mode is enabled
        if os.environ.get("FLASK_DEBUG", "").lower() in ("true", "1", "yes"):
            log_level = "DEBUG"
        setup_logger(name, log_level)
    return logger

