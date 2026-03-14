"""
Session management API routes.

Routes define endpoints and delegate to controllers for business logic.
All operations are logged via middleware.
"""

import logging

from fastapi import APIRouter, Query, Request

from src.api.controllers.session_controller import SessionController
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# Initialize controller
controller = SessionController()


@router.get("/active")
def list_active_sessions(request: Request):
    """Return active sessions from both interview and quiz workflows."""
    log_action(request, "list_active_sessions")

    try:
        result = controller.list_active_sessions()
        quiz_count = len(result.get("quiz", []))
        interview_count = len(result.get("interview", []))

        log_action(
            request,
            "list_active_sessions",
            quiz_sessions_count=quiz_count,
            interview_sessions_count=interview_count,
        )

        return result
    except Exception as e:
        log_action(
            request,
            "list_active_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


@router.get("/logs/{session_id}")
def get_session_logs(
    session_id: str,
    limit: int = Query(default=200, ge=1, le=2000),
    request: Request = Request,
):
    """Return recent JSONL logs for a given session id."""
    log_action(request, "get_session_logs", session_id=session_id, limit=limit)

    try:
        result = controller.get_session_logs(session_id, limit)

        log_action(
            request,
            "get_session_logs",
            session_id=session_id,
            logs_count=len(result.get("logs", [])),
        )

        return result
    except Exception as e:
        log_action(
            request,
            "get_session_logs",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


@router.get("/detail/{session_id}")
def get_session_detail(session_id: str, request: Request):
    """Fetch session progress JSON if present (quiz or interview)."""
    log_action(request, "get_session_detail", session_id=session_id)

    try:
        result = controller.get_session_detail(session_id)

        log_action(request, "get_session_detail", session_id=session_id, status="found")

        return result
    except Exception as e:
        log_action(
            request,
            "get_session_detail",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


@router.post("/resume/{session_id}")
def resume_session(session_id: str, request: Request):
    """Resume a paused session if possible (quiz or interview)."""
    log_action(request, "resume_session", session_id=session_id)

    try:
        result = controller.resume_session(session_id)

        log_action(request, "resume_session", session_id=session_id, status="success")

        return result
    except Exception as e:
        log_action(
            request,
            "resume_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise


@router.delete("/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a session's progress artifacts and logs (quiz and interview)."""
    log_action(request, "delete_session", session_id=session_id)

    try:
        result = controller.delete_session(session_id)

        log_action(
            request,
            "delete_session",
            session_id=session_id,
            status="success",
            progress_files_removed=len(
                result.get("removed", {}).get("progress_files", [])
            ),
            logs_deleted=result.get("removed", {}).get("logs_deleted", False),
        )

        return result
    except Exception as e:
        log_action(
            request,
            "delete_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise
