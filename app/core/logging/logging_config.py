import logging
import logging.config
import json
from datetime import datetime
from pathlib import Path
import os
from typing import Any, Dict

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

class CustomJsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add extra fields if they exist
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)

class RequestIdFilter(logging.Filter):
    """Filter to add request ID to log records"""
    def filter(self, record):
        record.request_id = getattr(record, "request_id", "no_request_id")
        return True

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "json": {
            "()": CustomJsonFormatter
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d %(message)s"
        }
    },
    "filters": {
        "request_id": {
            "()": RequestIdFilter
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "filters": ["request_id"]
        },
        "file": {
            "level": "INFO",
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "filters": ["request_id"]
        },
        "error_file": {
            "level": "ERROR",
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/error.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "filters": ["request_id"]
        }
    },
    "loggers": {
        "": {  # Root logger
            "handlers": ["console", "file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": True
        },
        "app": {  # Application logger
            "handlers": ["console", "file", "error_file"],
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "propagate": False
        },
        "uvicorn": {  # Uvicorn logger
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# Initialize logging configuration
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("app")

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(name)

def log_request(request_id: str, **kwargs: Any) -> None:
    """Log request details"""
    logger.info(
        "Request received",
        extra={
            "request_id": request_id,
            **kwargs
        }
    )

def log_response(request_id: str, status_code: int, **kwargs: Any) -> None:
    """Log response details"""
    logger.info(
        "Response sent",
        extra={
            "request_id": request_id,
            "status_code": status_code,
            **kwargs
        }
    )

def log_error(request_id: str, error: Exception, **kwargs: Any) -> None:
    """Log error details"""
    logger.error(
        f"Error occurred: {str(error)}",
        exc_info=True,
        extra={
            "request_id": request_id,
            **kwargs
        }
    )