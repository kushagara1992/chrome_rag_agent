import sys
from typing import Optional
from loguru import logger
from smart_search.core.config import get_settings

def setup_logging(log_level: Optional[str] = None, log_file: Optional[str] = None) -> None:
    settings = get_settings()
    
    log_level = log_level or settings.log_level
    log_file = log_file or settings.log_file
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stdout,
        level=log_level,
        format="<level>{time:YYYY-MM-DD HH:mm:ss}</level> | <level>{level: <8}</level> | {name}:{function}:{line} - <level>{message}</level>",
        colorize=True,
    )
    
    # Add file handler if specified
    if log_file:
        logger.add(
            log_file,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="500 MB",
            retention="7 days",
        )
    
    logger.info(f"Logging configured - Level: {log_level}")
