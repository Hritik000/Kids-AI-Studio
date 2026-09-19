import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import settings

def setup_logging():
    """Setup application logging."""
    logger = logging.getLogger()
    
    # Set log level based on environment
    if settings.ENVIRONMENT == "development":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # JSON formatter for structured logging
    json_formatter = jsonlogger.JsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(pathname)s %(lineno)d'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # File handler (in production, you might want to use a logging service)
    if settings.ENVIRONMENT == "production":
        file_handler = logging.FileHandler('/var/log/kidsai/app.log')
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    # Prevent duplicate logs
    logger.propagate = False
    
    return logger

# Create a default logger instance
logger = setup_logging()
