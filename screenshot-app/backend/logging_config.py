"""
Logging Configuration for Screenshot Tool
Provides structured logging with file rotation and console output
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os


def setup_logging(name: str = __name__) -> logging.Logger:
    """
    Configure structured logging for the application.
    
    Features:
    - Console output with colored formatting (development)
    - Rotating file handler (10MB max, 5 backups)
    - Configurable log level via environment variable
    - Emoji-based log messages for easy scanning
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Get log level from environment (default: INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # Console handler (stdout for better compatibility)
            logging.StreamHandler(sys.stdout),
            
            # File handler (rotating, max 10MB, keep 5 backups)
            RotatingFileHandler(
                'logs/screenshot_tool.log',
                maxBytes=10_485_760,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ],
        force=True  # Override any existing configuration
    )
    
    # Set levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Get logger for this module
    logger = logging.getLogger(name)
    
    return logger


# Create default logger
logger = setup_logging()


# Convenience functions for common log patterns
def log_capture_start(url: str, mode: str, stealth: bool = False):
    """Log screenshot capture start"""
    stealth_indicator = "🥷" if stealth else "📸"
    logger.info(f"{stealth_indicator} Starting {mode} capture: {url}")


def log_capture_success(url: str, path: str, duration: float = None):
    """Log successful screenshot capture"""
    duration_str = f" ({duration:.2f}s)" if duration else ""
    logger.info(f"✅ Captured: {url} → {path}{duration_str}")


def log_capture_error(url: str, error: str):
    """Log screenshot capture error"""
    logger.error(f"❌ Failed to capture {url}: {error}")


def log_auth_state(cookie_count: int, ls_count: int):
    """Log authentication state loading"""
    logger.info(f"🔐 Auth state loaded: {cookie_count} cookies, {ls_count} localStorage items")


def log_quality_check(url: str, score: float, passed: bool):
    """Log quality check result"""
    status = "✅ PASS" if passed else "⚠️  FAIL"
    logger.info(f"{status} Quality check for {url}: {score:.1f}/100")


def log_browser_launch(headless: bool, stealth: bool):
    """Log browser launch"""
    mode = "headless" if headless else "visible"
    stealth_str = " with stealth" if stealth else ""
    logger.info(f"🌐 Launching {mode} browser{stealth_str}")


def log_request_start(request_id: str, url_count: int):
    """Log API request start"""
    logger.info(f"🚀 Request {request_id[:8]}: Processing {url_count} URL(s)")


def log_request_complete(request_id: str, success_count: int, total_count: int, duration: float):
    """Log API request completion"""
    logger.info(
        f"🏁 Request {request_id[:8]} complete: "
        f"{success_count}/{total_count} successful ({duration:.2f}s)"
    )


def log_cancellation(request_id: str, completed: int, total: int):
    """Log request cancellation"""
    logger.warning(
        f"🛑 Request {request_id[:8]} cancelled: "
        f"{completed}/{total} completed before cancellation"
    )

