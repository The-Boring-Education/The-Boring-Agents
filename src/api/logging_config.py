"""
Centralized logging configuration for The Boring Agents API.

Provides structured JSON logging with file rotation and
environment-aware configuration.
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from src.core.env import get_env_manager


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Formats log records as JSON for easy parsing and analysis.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format a log record as JSON.

        Args:
            record: The log record to format

        Returns:
            JSON string representation of the log record
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "environment"):
            log_data["environment"] = record.environment
        if hasattr(record, "action"):
            log_data["action"] = record.action
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_data[key] = value

        return json.dumps(log_data)


def setup_api_logging() -> None:
    """
    Set up logging configuration for the API.

    Configures:
    - Console handler with JSON formatting
    - File handler with rotation
    - Environment-based log levels
    - Log directory creation
    """
    env_manager = get_env_manager()

    # Get log level from environment
    log_level_str = env_manager.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Get log directory
    log_dir = Path(env_manager.get("LOG_DIR", "./logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create API log file path
    api_log_file = log_dir / "api.log"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create JSON formatter
    json_formatter = JSONFormatter()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(json_formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation (10MB per file, keep 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        api_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(json_formatter)
    root_logger.addHandler(file_handler)

    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info(
        json.dumps(
            {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": "INFO",
                "message": "API logging configured",
                "log_level": log_level_str,
                "log_file": str(api_log_file),
                "environment": env_manager.get("ENVIRONMENT", "dev"),
            }
        )
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with API context.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
