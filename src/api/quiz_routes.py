"""
Quiz generation API routes.

All operations are logged comprehensively for Admin UI monitoring.
"""

import json
import logging
import os
from fastapi import APIRouter, HTTPException, Request
from typing import Optional, List, Dict, Any

from ..agents.quiz.quiz_orchestrator import QuizOrchestrator
from ..agents.quiz.quiz_uploader import QuizUploader
from ..agents.quiz.types import QuizTopic
from ..utils.helpers import generate_filename, load_json_file
from ..utils.session_logger import read_logs
from ..core.config import config
from ..core.env import get_env_manager
from .models import (
    GenerateQuizRequest,
    GenerateQuizAPIResponse,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    QuizTopicsResponse,
)

logger = logging.getLogger(__name__)
env_manager = get_env_manager()

router = APIRouter(prefix="/quiz", tags=["quiz"])


def _get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")


def _log_action(
    request: Request,
    action: str,
    level: str = "INFO",
    **kwargs
) -> None:
    """
    Log an action with structured format.
    
    Args:
        request: FastAPI request object
        action: Action name
        level: Log level
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
    """Return the list of available quiz topics supported by the orchestrator.

    This keeps Admin UI dynamic and in sync with agents.
    """
    topics = [t.value for t in QuizTopic]
    _log_action(request, "get_quiz_topics", topics_count=len(topics))
    return QuizTopicsResponse(topics=topics)


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
        orchestrator = QuizOrchestrator()
        result = orchestrator.generate_complete_quiz(
            topic=payload.topic,
            question_count=payload.question_count,
            target_audience=payload.target_audience,
        )

        # Save if requested
        output_file: Optional[str] = None
        if payload.save and result:
            filename = generate_filename(prefix=f"quiz_{payload.topic.lower()}")
            orchestrator.save_content(result, filename)
            output_file = filename

        quiz_dict = result.get("quiz")
        if not quiz_dict:
            _log_action(
                request,
                "generate_quiz",
                level="ERROR",
                topic=payload.topic,
                error="Quiz generation failed - no quiz data returned",
                environment=environment
            )
            raise HTTPException(status_code=500, detail="Quiz generation failed")

        session_id = result.get("session_id", "unknown")
        _log_action(
            request,
            "generate_quiz",
            level="INFO",
            topic=payload.topic,
            session_id=session_id,
            status="success",
            questions_generated=len(quiz_dict.get("questions", [])),
            environment=environment
        )
        
        response = GenerateQuizAPIResponse(
            session_id=session_id,
            output_file=output_file or result.get("output_file"),
            quiz=quiz_dict,
        )
        return response
        
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
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")


@router.post("/validate", response_model=SimpleStatus)
def validate_quiz(payload: ValidateQuizRequest, request: Request):
    """Validate a quiz structure and content."""
    _log_action(request, "validate_quiz")
    
    try:
        uploader = QuizUploader()
        validation = uploader.validate_quiz(payload.quiz)
        status = validation.get("status")
        ok = status == "success"
        message = "Validation complete" if ok else "Validation failed"
        
        if ok:
            _log_action(
                request,
                "validate_quiz",
                level="INFO",
                status="success"
            )
        else:
            _log_action(
                request,
                "validate_quiz",
                level="WARNING",
                status="failed",
                error=validation.get("message", "Unknown error")
            )
        
        return SimpleStatus(ok=ok, message=message)
        
    except Exception as e:
        _log_action(
            request,
            "validate_quiz",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


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
        uploader = QuizUploader(api_url=payload.api_url, admin_secret=payload.admin_secret or "TBEAdmin")
        result = uploader.upload_quiz(payload.quiz)
        ok = result.get("status") == "success"
        message = result.get("message", "Upload complete")
        
        if ok:
            quiz_id = result.get("quiz_id", "unknown")
            _log_action(
                request,
                "upload_quiz",
                level="INFO",
                status="success",
                quiz_id=quiz_id,
                environment=environment
            )
        else:
            _log_action(
                request,
                "upload_quiz",
                level="ERROR",
                status="failed",
                error=message,
                environment=environment
            )
            raise HTTPException(status_code=400, detail=message)
        
        return SimpleStatus(ok=True, message=message)
        
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "upload_quiz",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__,
            environment=environment
        )
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/sessions")
def list_quiz_sessions(request: Request):
    """List all active quiz generation sessions."""
    _log_action(request, "list_quiz_sessions")
    
    try:
        orchestrator = QuizOrchestrator()
        result = orchestrator.list_active_sessions()
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
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/progress/{session_id}")
def get_quiz_progress(session_id: str, request: Request):
    """Return progress details for a quiz generation session."""
    _log_action(request, "get_quiz_progress", session_id=session_id)
    
    try:
        progress_dir = os.path.join(config.temp_dir, "quiz_progress")
        if not os.path.isdir(progress_dir):
            raise HTTPException(status_code=404, detail="Progress not found")

        progress_path: Optional[str] = None
        for name in os.listdir(progress_dir):
            if session_id in name and name.endswith(".json"):
                progress_path = os.path.join(progress_dir, name)
                break

        if not progress_path or not os.path.isfile(progress_path):
            raise HTTPException(status_code=404, detail="Progress not found")

        data = load_json_file(progress_path)

        # Derive counts
        total = int(data.get("question_count") or 0)
        generated = len(data.get("questions", []) or [])

        # Compute percent
        steps_completed: List[str] = data.get("steps_completed", []) or []
        current_step = data.get("current_step") or ""
        base_steps = {"research", "planning", "generation", "metadata"}
        completed_steps = len([s for s in steps_completed if s in base_steps])
        percent = completed_steps * 25.0
        
        if current_step == "generation" and total > 0:
            percent = 50.0 + min(25.0, (generated / total) * 25.0)
        if data.get("status") == "completed" or current_step == "completed":
            percent = 100.0

        _log_action(
            request,
            "get_quiz_progress",
            session_id=session_id,
            percent=percent,
            status=data.get("status")
        )

        return {
            "session_id": data.get("session_id"),
            "topic": data.get("topic"),
            "status": data.get("status"),
            "current_step": current_step,
            "steps_completed": steps_completed,
            "question_count": total,
            "questions_generated": generated,
            "percent": percent,
            "last_updated": data.get("last_updated"),
            "created_at": data.get("created_at"),
        }
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "get_quiz_progress",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.get("/logs/{session_id}")
def get_quiz_logs(session_id: str, limit: int = 200, request: Request = None):
    """Proxy to session logs for convenience under quiz namespace."""
    if request:
        _log_action(request, "get_quiz_logs", session_id=session_id, limit=limit)
    
    try:
        logs = read_logs(session_id=session_id, limit=max(1, min(limit, 2000)))
        
        if request:
            _log_action(
                request,
                "get_quiz_logs",
                session_id=session_id,
                logs_count=len(logs)
            )
        
        return {"session_id": session_id, "logs": logs}
    except Exception as e:
        if request:
            _log_action(
                request,
                "get_quiz_logs",
                level="ERROR",
                session_id=session_id,
                error=str(e),
                error_type=type(e).__name__
            )
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


@router.get("/pending")
def list_pending_quizzes(request: Request):
    """List quiz JSON files in the output directory as pending items for upload."""
    _log_action(request, "list_pending_quizzes")
    
    try:
        pending: List[Dict[str, Any]] = []
        out_dir = config.output_dir
        if not os.path.isdir(out_dir):
            return {"pending": pending}

        for name in os.listdir(out_dir):
            if not name.endswith(".json"):
                continue
            if not name.startswith("quiz_"):
                continue
            path = os.path.join(out_dir, name)
            try:
                content = load_json_file(path)
                quiz = content.get("quiz", {}) if isinstance(content, dict) else {}
                meta = content.get("metadata", {}) if isinstance(content, dict) else {}
                pending.append({
                    "filename": name,
                    "session_id": meta.get("session_id"),
                    "topic": meta.get("topic"),
                    "question_count": len((quiz.get("questions") or [])),
                    "categoryId": quiz.get("categoryId"),
                    "categoryName": quiz.get("categoryName"),
                })
            except Exception:
                continue

        pending.sort(key=lambda x: x.get("filename", ""), reverse=True)
        
        _log_action(
            request,
            "list_pending_quizzes",
            pending_count=len(pending)
        )
        
        return {"pending": pending}
    except Exception as e:
        _log_action(
            request,
            "list_pending_quizzes",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=f"Failed to list pending quizzes: {str(e)}")


@router.delete("/pending/{filename}")
def delete_pending_quiz(filename: str, request: Request):
    """Delete a pending quiz file."""
    _log_action(request, "delete_pending_quiz", filename=filename)
    
    try:
        out_path = os.path.join(config.output_dir, filename)
        if not os.path.isfile(out_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        os.remove(out_path)
        
        _log_action(
            request,
            "delete_pending_quiz",
            filename=filename,
            status="success"
        )
        
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "delete_pending_quiz",
            level="ERROR",
            filename=filename,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/{filename}/content")
def get_pending_quiz_content(filename: str, request: Request):
    """Get the content of a pending quiz file."""
    _log_action(request, "get_pending_quiz_content", filename=filename)
    
    try:
        out_path = os.path.join(config.output_dir, filename)
        if not os.path.isfile(out_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        content = load_json_file(out_path)
        return content
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "get_pending_quiz_content",
            level="ERROR",
            filename=filename,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))
