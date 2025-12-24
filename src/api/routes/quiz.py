"""
Quiz generation API routes.

Routes define endpoints and delegate to controllers for business logic.
All operations are logged via middleware.

Matches Interview Prep API pattern for consistency.

API Naming Conventions (REST-compliant):
- POST /quizzes           - Create a new quiz
- POST /topics            - Generate quiz for a single topic
- GET /sessions           - List all sessions
- GET /sessions/{id}      - Get session progress
- GET /sessions/{id}/output - Get session output
- POST /sessions/{id}/cancel - Cancel session
- POST /sessions/{id}/resume - Resume session
- POST /sessions/{id}/retry  - Retry session
- DELETE /sessions/{id}   - Delete session
- POST /validate          - Validate quiz data
- POST /upload            - Upload quiz to database
"""

import logging
from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from typing import Optional

from src.api.controllers.quiz_controller import QuizController
from src.api.models.quiz_models import (
    CreateQuizRequest,
    TopicGenerationRequest,
    UploadQuizRequest,
    ValidateQuizRequest,
    SessionResponse,
    SimpleStatus,
)
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["quiz"])

# Initialize controller
controller = QuizController()


# =============================================================================
# Quiz Creation
# =============================================================================

@router.post("/quizzes", response_model=SessionResponse)
async def create_quiz(
    payload: CreateQuizRequest,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Create a new quiz with topic and settings."""
    log_action(
        request,
        "create_quiz",
        topic=payload.topic,
        agent_type=payload.agent_type.value,
        question_count=payload.question_count,
        difficulty=payload.difficulty.value
    )
    
    try:
        result = controller.create_quiz(payload, background_tasks)
        
        log_action(
            request,
            "create_quiz",
            status="success",
            session_id=result.sessionId
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "create_quiz",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


# =============================================================================
# Topic Operations
# =============================================================================

@router.post("/topics", response_model=SessionResponse)
async def generate_topic(
    payload: TopicGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Generate quiz for a single topic."""
    log_action(
        request,
        "generate_quiz_topic",
        topic=payload.topic,
        agent_type=payload.agent_type.value,
        question_count=payload.question_count,
        difficulty=payload.difficulty.value
    )
    
    try:
        result = controller.generate_topic(payload, background_tasks)
        return result
    except Exception as e:
        log_action(
            request,
            "generate_quiz_topic",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


# =============================================================================
# Session Operations
# =============================================================================

@router.get("/sessions")
def list_sessions(status: Optional[str] = None, request: Request = None):
    """List all active/recent quiz sessions."""
    log_action(request, "list_quiz_sessions", status_filter=status)
    
    try:
        sessions = controller.list_sessions(status)
        
        log_action(
            request,
            "list_quiz_sessions",
            sessions_count=len(sessions)
        )
        
        return sessions
    except Exception as e:
        log_action(
            request,
            "list_quiz_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/sessions/{session_id}")
def get_session_progress(session_id: str, request: Request):
    """Get progress for a specific quiz session."""
    log_action(request, "get_quiz_session_progress", session_id=session_id)
    
    try:
        result = controller.get_session_progress(session_id)
        
        log_action(
            request,
            "get_quiz_session_progress",
            session_id=session_id,
            status=result.get("status"),
            progress=result.get("progress", {})
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "get_quiz_session_progress",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/sessions/{session_id}/output")
def get_session_output(session_id: str, request: Request):
    """Get final output for a completed quiz session."""
    log_action(request, "get_quiz_session_output", session_id=session_id)
    
    try:
        result = controller.get_session_output(session_id)
        
        log_action(
            request,
            "get_quiz_session_output",
            session_id=session_id,
            status="success"
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        log_action(
            request,
            "get_quiz_session_output",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/cancel")
def cancel_session(session_id: str, request: Request):
    """Cancel a running quiz session."""
    log_action(request, "cancel_quiz_session", session_id=session_id)
    
    try:
        result = controller.cancel_session(session_id)
        
        log_action(
            request,
            "cancel_quiz_session",
            session_id=session_id,
            status="cancelled"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "cancel_quiz_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/sessions/{session_id}/resume")
async def resume_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Resume a quiz session from where it left off."""
    log_action(request, "resume_quiz_session", session_id=session_id)
    
    try:
        result = controller.retry_session(session_id, background_tasks)
        
        log_action(
            request,
            "resume_quiz_session",
            session_id=session_id,
            status="resumed"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "resume_quiz_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/sessions/{session_id}/retry")
async def retry_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    request: Request
):
    """Retry a failed quiz session (alias for resume)."""
    log_action(request, "retry_quiz_session", session_id=session_id)
    
    try:
        result = controller.retry_session(session_id, background_tasks)
        
        log_action(
            request,
            "retry_quiz_session",
            old_session_id=session_id,
            new_session_id=result.sessionId
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "retry_quiz_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a quiz session."""
    log_action(request, "delete_quiz_session", session_id=session_id)
    
    try:
        result = controller.delete_session(session_id)
        
        log_action(
            request,
            "delete_quiz_session",
            session_id=session_id,
            status="success"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "delete_quiz_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


# =============================================================================
# Validation & Upload
# =============================================================================

@router.post("/validate", response_model=SimpleStatus)
def validate_quiz(payload: ValidateQuizRequest, request: Request):
    """Validate a quiz structure and content against DB schema."""
    log_action(request, "validate_quiz")
    
    try:
        result = controller.validate_quiz(payload)
        
        if result.ok:
            log_action(request, "validate_quiz", level="INFO", status="success")
        else:
            log_action(request, "validate_quiz", level="WARNING", status="failed")
        
        return result
    except Exception as e:
        log_action(
            request,
            "validate_quiz",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/upload", response_model=SimpleStatus)
def upload_quiz(payload: UploadQuizRequest, request: Request):
    """Upload a quiz to the database."""
    log_action(
        request,
        "upload_quiz",
        api_url=payload.api_url or "default"
    )
    
    try:
        result = controller.upload_quiz(payload)
        
        log_action(
            request,
            "upload_quiz",
            level="INFO",
            status="success" if result.ok else "failed"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "upload_quiz",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise