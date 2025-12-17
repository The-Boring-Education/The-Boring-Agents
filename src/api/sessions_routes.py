"""
Session management API routes.

All operations are logged comprehensively for Admin UI monitoring.
"""

import json
import logging
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional, List, Dict, Any
import os

from ..agents.quiz.quiz_orchestrator import QuizOrchestrator
from ..agents.interview.interview_sheet_manager import InterviewSheetManager
from ..utils.session_logger import read_logs, get_log_file_path
from ..utils.helpers import load_json_file
from ..core.config import config
from ..core.env import get_env_manager

logger = logging.getLogger(__name__)
env_manager = get_env_manager()

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


def _log_action(
    request: Request,
    action: str,
    level: str = "INFO",
    session_id: Optional[str] = None,
    **kwargs
) -> None:
    """
    Log an action with structured format.
    
    Args:
        request: FastAPI request object
        action: Action name
        level: Log level
        session_id: Session ID if available
        **kwargs: Additional log fields
    """
    log_data = {
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=0, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        )),
        "level": level,
        "request_id": _get_request_id(request),
        "action": action,
        "environment": env_manager.get("ENVIRONMENT", "dev"),
    }
    
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
        quiz = QuizOrchestrator()
        interview = InterviewSheetManager()
        quiz_sessions = quiz.list_active_sessions()
        interview_sessions = interview.list_active_sessions()
        
        quiz_count = len(quiz_sessions.get("sessions", []))
        interview_count = len(interview_sessions.get("sessions", []))
        
        _log_action(
            request,
            "list_active_sessions",
            quiz_sessions_count=quiz_count,
            interview_sessions_count=interview_count
        )
        
        return {
            "ok": True,
            "quiz": quiz_sessions.get("sessions", []),
            "interview": interview_sessions.get("sessions", []),
        }
    except Exception as e:
        _log_action(
            request,
            "list_active_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to list active sessions: {str(e)}")


@router.get("/logs/{session_id}")
def get_session_logs(session_id: str, limit: int = Query(default=200, ge=1, le=2000), request: Request = None):
    """Return recent JSONL logs for a given session id."""
    if request:
        _log_action(request, "get_session_logs", session_id=session_id, limit=limit)
    
    try:
        logs = read_logs(session_id=session_id, limit=limit)
        
        if request:
            _log_action(
                request,
                "get_session_logs",
                session_id=session_id,
                logs_count=len(logs)
            )
        
        return {"ok": True, "session_id": session_id, "logs": logs}
    except Exception as e:
        if request:
            _log_action(
                request,
                "get_session_logs",
                level="ERROR",
                session_id=session_id,
                error=str(e),
                error_type=type(e).__name__
            )
        raise HTTPException(status_code=500, detail=f"Failed to get session logs: {str(e)}")


@router.get("/detail/{session_id}")
def get_session_detail(session_id: str, request: Request):
    """Fetch session progress JSON if present (quiz or interview)."""
    _log_action(request, "get_session_detail", session_id=session_id)
    
    try:
        # Check quiz progress dir
        quiz_progress_dir = os.path.join(config.temp_dir, "quiz_progress")
        if os.path.isdir(quiz_progress_dir):
            for name in os.listdir(quiz_progress_dir):
                if session_id in name and name.endswith(".json"):
                    data = load_json_file(os.path.join(quiz_progress_dir, name))
                    _log_action(
                        request,
                        "get_session_detail",
                        session_id=session_id,
                        type="quiz",
                        status="found"
                    )
                    return {"ok": True, "data": data}

        # Check interview progress files
        if os.path.isdir(config.temp_dir):
            for name in os.listdir(config.temp_dir):
                if name.startswith("progress_") and name.endswith(".json"):
                    path = os.path.join(config.temp_dir, name)
                    try:
                        data = load_json_file(path)
                        if data.get("session_id") == session_id:
                            _log_action(
                                request,
                                "get_session_detail",
                                session_id=session_id,
                                type="interview",
                                status="found"
                            )
                            return {"ok": True, "data": data}
                    except Exception:
                        continue

        _log_action(
            request,
            "get_session_detail",
            level="ERROR",
            session_id=session_id,
            error="Session not found"
        )
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "get_session_detail",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to get session detail: {str(e)}")


@router.post("/resume/{session_id}")
def resume_session(session_id: str, request: Request):
    """Resume a paused session if possible (quiz or interview)."""
    _log_action(request, "resume_session", session_id=session_id)
    
    try:
        # Try quiz first
        quiz = QuizOrchestrator()
        quiz_result = quiz.resume_quiz_generation(session_id)
        if quiz_result.get("status") != "error":
            _log_action(
                request,
                "resume_session",
                session_id=session_id,
                type="quiz",
                status="success"
            )
            return {"ok": True, "result": quiz_result}

        # Try interview by locating filepath
        interview = InterviewSheetManager()
        sessions = interview.list_active_sessions().get("sessions", [])
        match = next((s for s in sessions if s.get("session_id") == session_id), None)
        if match:
            result = interview.resume_session(match.get("filepath"))
            if result.get("status") != "error":
                _log_action(
                    request,
                    "resume_session",
                    session_id=session_id,
                    type="interview",
                    status="success"
                )
                return {"ok": True, "result": result}

        _log_action(
            request,
            "resume_session",
            level="ERROR",
            session_id=session_id,
            error="Unable to resume session"
        )
        raise HTTPException(status_code=404, detail="Unable to resume session")
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "resume_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to resume session: {str(e)}")


@router.delete("/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a session's progress artifacts and logs (quiz and interview).

    This removes:
    - Quiz progress file under temp/quiz_progress containing the session_id
    - Interview progress file(s) in temp/ matching the session_id in content
    - Session log file under logs/sessions/{session_id}.log
    """
    _log_action(request, "delete_session", session_id=session_id)
    
    removed: Dict[str, Any] = {
        "progress_files": [],
        "logs_deleted": False,
    }

    try:
        # Delete quiz progress files
        quiz_progress_dir = os.path.join(config.temp_dir, "quiz_progress")
        if os.path.isdir(quiz_progress_dir):
            for name in os.listdir(quiz_progress_dir):
                if session_id in name and name.endswith(".json"):
                    path = os.path.join(quiz_progress_dir, name)
                    try:
                        os.remove(path)
                        removed["progress_files"].append(path)
                    except Exception:
                        pass

        # Delete interview progress files that match session_id in JSON content
        if os.path.isdir(config.temp_dir):
            for name in os.listdir(config.temp_dir):
                if name.startswith("progress_") and name.endswith(".json"):
                    path = os.path.join(config.temp_dir, name)
                    try:
                        data = load_json_file(path)
                        if data.get("session_id") == session_id:
                            try:
                                os.remove(path)
                                removed["progress_files"].append(path)
                            except Exception:
                                pass
                    except Exception:
                        continue

        # Delete logs file
        log_path = get_log_file_path(session_id)
        if os.path.exists(log_path):
            try:
                os.remove(log_path)
                removed["logs_deleted"] = True
            except Exception:
                pass

        _log_action(
            request,
            "delete_session",
            session_id=session_id,
            status="success",
            progress_files_removed=len(removed["progress_files"]),
            logs_deleted=removed["logs_deleted"]
        )

        return {"ok": True, "removed": removed}
    except Exception as e:
        _log_action(
            request,
            "delete_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")
