"""
Logging configuration for the password manager.
Provides centralized logging for debugging and audit trail.
"""

import logging
import os
from constants import LOG_FILE, LOG_FORMAT, LOG_LEVEL


def setup_logger(name="PasswordManager"):
    """
    Set up and configure logger.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Console handler (only warnings and errors)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        console_formatter = logging.Formatter("%(levelname)s: %(message)s")
        console_handler.setFormatter(console_formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


# Create default logger
logger = setup_logger()
