"""
Session management API routes.

Routes define endpoints and delegate to controllers for business logic.
All operations are logged via middleware.
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, Query, Request

from ..controllers.session_controller import SessionController
from ...core.env import get_env_manager

logger = logging.getLogger(__name__)
env_manager = get_env_manager()

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Initialize controller
controller = SessionController()


def _get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


def _log_action(
    request: Optional[Request],
    action: str,
    level: str = "INFO",
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """Log an action with structured format."""
    log_data = {
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=0, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        )),
        "level": level,
        "action": action,
        "environment": env_manager.get("ENVIRONMENT", "dev"),
    }
    
    if request:
        log_data["request_id"] = _get_request_id(request)
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


@router.get("/active")
def list_active_sessions(request: Request):
    """Return active sessions from both interview and quiz workflows."""
    _log_action(request, "list_active_sessions")
    
    try:
        result = controller.list_active_sessions()
        quiz_count = len(result.get("quiz", []))
        interview_count = len(result.get("interview", []))
        
        _log_action(
            request,
            "list_active_sessions",
            quiz_sessions_count=quiz_count,
            interview_sessions_count=interview_count
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "list_active_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/logs/{session_id}")
def get_session_logs(session_id: str, limit: int = Query(default=200, ge=1, le=2000), request: Request = Request):
    """Return recent JSONL logs for a given session id."""
    _log_action(request, "get_session_logs", session_id=session_id, limit=limit)
    
    try:
        result = controller.get_session_logs(session_id, limit)
        
        _log_action(
            request,
            "get_session_logs",
            session_id=session_id,
            logs_count=len(result.get("logs", []))
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "get_session_logs",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/detail/{session_id}")
def get_session_detail(session_id: str, request: Request):
    """Fetch session progress JSON if present (quiz or interview)."""
    _log_action(request, "get_session_detail", session_id=session_id)
    
    try:
        result = controller.get_session_detail(session_id)
        
        _log_action(
            request,
            "get_session_detail",
            session_id=session_id,
            status="found"
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "get_session_detail",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/resume/{session_id}")
def resume_session(session_id: str, request: Request):
    """Resume a paused session if possible (quiz or interview)."""
    _log_action(request, "resume_session", session_id=session_id)
    
    try:
        result = controller.resume_session(session_id)
        
        _log_action(
            request,
            "resume_session",
            session_id=session_id,
            status="success"
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "resume_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.delete("/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a session's progress artifacts and logs (quiz and interview)."""
    _log_action(request, "delete_session", session_id=session_id)
    
    try:
        result = controller.delete_session(session_id)
        
        _log_action(
            request,
            "delete_session",
            session_id=session_id,
            status="success",
            progress_files_removed=len(result.get("removed", {}).get("progress_files", [])),
            logs_deleted=result.get("removed", {}).get("logs_deleted", False)
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "delete_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise

