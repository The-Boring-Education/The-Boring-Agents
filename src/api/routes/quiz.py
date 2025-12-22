"""
Quiz generation API routes.

Routes define endpoints and delegate to controllers for business logic.
All operations are logged via middleware.
"""

import json
import logging
from fastapi import APIRouter, Request

from src.api.controllers.quiz_controller import QuizController
from src.api.models.quiz_models import (
    GenerateQuizRequest,
    GenerateQuizAPIResponse,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    QuizTopicsResponse,
)
from src.core.env import get_env_manager

logger = logging.getLogger(__name__)
env_manager = get_env_manager()

router = APIRouter(prefix="/quiz", tags=["quiz"])

# Initialize controller
controller = QuizController()


def _get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


def _log_action(
    request: Request,
    action: str,
    level: str = "INFO",
    **kwargs
) -> None:
    """Log an action with structured format."""
    log_data = {
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=0, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        )),
        "level": level,
        "request_id": _get_request_id(request),
        "action": action,
        "environment": env_manager.get("ENVIRONMENT", "dev"),
        **kwargs
    }
    
    log_message = json.dumps(log_data)
    
    if level == "ERROR":
        logger.error(log_message)
    elif level == "WARNING":
        logger.warning(log_message)
    else:
        logger.info(log_message)


@router.get("/topics", response_model=QuizTopicsResponse)
def get_available_topics(request: Request):
    """Return the list of available quiz topics supported by the orchestrator."""
    _log_action(request, "get_quiz_topics")
    result = controller.get_available_topics()
    _log_action(request, "get_quiz_topics", topics_count=len(result.topics))
    return result


@router.post("/generate", response_model=GenerateQuizAPIResponse)
def generate_quiz(payload: GenerateQuizRequest, request: Request):
    """Generate a complete quiz for a technology topic."""
    environment = payload.environment or env_manager.get("ENVIRONMENT", "dev")
    
    _log_action(
        request,
        "generate_quiz",
        topic=payload.topic,
        question_count=payload.question_count,
        target_audience=payload.target_audience,
        environment=environment
    )
    
    try:
        result = controller.generate_quiz(payload)
        
        _log_action(
            request,
            "generate_quiz",
            level="INFO",
            topic=payload.topic,
            session_id=result.session_id,
            status="success",
            questions_generated=len(result.quiz.get("questions", [])),
            environment=environment
        )
        
        return result
        
    except Exception as e:
        _log_action(
            request,
            "generate_quiz",
            level="ERROR",
            topic=payload.topic,
            error=str(e),
            error_type=type(e).__name__,
            environment=environment
        )
        raise


@router.post("/validate", response_model=SimpleStatus)
def validate_quiz(payload: ValidateQuizRequest, request: Request):
    """Validate a quiz structure and content."""
    _log_action(request, "validate_quiz")
    
    try:
        result = controller.validate_quiz(payload)
        
        if result.ok:
            _log_action(request, "validate_quiz", level="INFO", status="success")
        else:
            _log_action(request, "validate_quiz", level="WARNING", status="failed")
        
        return result
        
    except Exception as e:
        _log_action(
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
    environment = payload.environment or env_manager.get("ENVIRONMENT", "dev")
    
    _log_action(
        request,
        "upload_quiz",
        api_url=payload.api_url or "default",
        environment=environment
    )
    
    try:
        result = controller.upload_quiz(payload)
        
        _log_action(
            request,
            "upload_quiz",
            level="INFO",
            status="success",
            environment=environment
        )
        
        return result
        
    except Exception as e:
        _log_action(
            request,
            "upload_quiz",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__,
            environment=environment
        )
        raise


@router.get("/sessions")
def list_quiz_sessions(request: Request):
    """List all active quiz generation sessions."""
    _log_action(request, "list_quiz_sessions")
    
    try:
        result = controller.list_sessions()
        sessions = result.get("sessions", [])
        
        _log_action(
            request,
            "list_quiz_sessions",
            sessions_count=len(sessions)
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "list_quiz_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/progress/{session_id}")
def get_quiz_progress(session_id: str, request: Request):
    """Return progress details for a quiz generation session."""
    _log_action(request, "get_quiz_progress", session_id=session_id)
    
    try:
        result = controller.get_progress(session_id)
        
        _log_action(
            request,
            "get_quiz_progress",
            session_id=session_id,
            percent=result.get("percent", 0),
            status=result.get("status")
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "get_quiz_progress",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/logs/{session_id}")
def get_quiz_logs(session_id: str, limit: int = 200, request: Request = Request):
    """Proxy to session logs for convenience under quiz namespace."""
    _log_action(request, "get_quiz_logs", session_id=session_id, limit=limit)
    
    try:
        result = controller.get_logs(session_id, limit)
        
        _log_action(
            request,
            "get_quiz_logs",
            session_id=session_id,
            logs_count=len(result.get("logs", []))
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "get_quiz_logs",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/pending")
def list_pending_quizzes(request: Request):
    """List quiz JSON files in the output directory as pending items for upload."""
    _log_action(request, "list_pending_quizzes")
    
    try:
        result = controller.list_pending_quizzes()
        pending = result.get("pending", [])
        
        _log_action(
            request,
            "list_pending_quizzes",
            pending_count=len(pending)
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "list_pending_quizzes",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.delete("/pending/{filename}")
def delete_pending_quiz(filename: str, request: Request):
    """Delete a pending quiz file."""
    _log_action(request, "delete_pending_quiz", filename=filename)
    
    try:
        result = controller.delete_pending_quiz(filename)
        
        _log_action(
            request,
            "delete_pending_quiz",
            filename=filename,
            status="success"
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "delete_pending_quiz",
            level="ERROR",
            filename=filename,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/pending/{filename}/content")
def get_pending_quiz_content(filename: str, request: Request):
    """Get the content of a pending quiz file."""
    _log_action(request, "get_pending_quiz_content", filename=filename)
    
    try:
        result = controller.get_pending_quiz_content(filename)
        return result
    except Exception as e:
        _log_action(
            request,
            "get_pending_quiz_content",
            level="ERROR",
            filename=filename,
            error=str(e),
            error_type=type(e).__name__
        )
        raise

