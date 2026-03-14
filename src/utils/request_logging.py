"""
Common request logging utilities.

Provides centralized functions for request ID extraction and structured action logging.
Used across all API routes for consistent logging patterns.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

from fastapi import Request

from src.core.env import get_env_manager

logger = logging.getLogger(__name__)
env_manager = get_env_manager()


def get_request_id(request: Request) -> str:
    """
    Extract request ID from request state.

    Args:
        request: FastAPI Request object

    Returns:
        Request ID string or 'unknown' if not set
    """
    return getattr(request.state, "request_id", "unknown")


def log_action(
    request: Optional[Request],
    action: str,
    level: str = "INFO",
    session_id: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """
    Log an action with structured JSON format.

    Provides consistent logging across all API routes with:
    - Timestamp in ISO format
    - Log level
    - Action name
    - Environment
    - Request ID (if request provided)
    - Session ID (if provided)
    - Additional context via kwargs

    Args:
        request: Optional FastAPI Request object
        action: Name of the action being performed
        level: Log level - "INFO", "WARNING", or "ERROR"
        session_id: Optional session identifier
        **kwargs: Additional context to include in log
    """
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": level,
        "action": action,
        "environment": env_manager.get("ENVIRONMENT", "dev"),
    }

    if request:
        log_data["request_id"] = get_request_id(request)
    if session_id:
        log_data["session_id"] = session_id

    log_data.update(kwargs)
    log_message = json.dumps(log_data)

    if level == "ERROR":
        logger.error(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)
