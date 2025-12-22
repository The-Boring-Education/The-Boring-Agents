"""
Interview preparation API routes.

Routes define endpoints and delegate to controllers for business logic.
All operations are logged via middleware.
"""

import json
import logging
from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.api.controllers.interview_prep_controller import InterviewPrepController
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    GenerateInterviewSheetRequest,
    TopicGenerationRequest,
    BulkGenerationRequest,
    InterviewSheetResponse,
    SessionResponse,
    TopicTemplate,
    RoadmapSuggestion,
)
from src.core.env import get_env_manager

logger = logging.getLogger(__name__)
env_manager = get_env_manager()

router = APIRouter(prefix="/interview", tags=["interview"])

# Initialize controller
controller = InterviewPrepController()


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
        "timestamp": datetime.utcnow().isoformat() + "Z",
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


@router.post("/create-sheet-new", response_model=SessionResponse)
async def create_sheet_new(payload: CreateSheetRequest, background_tasks: BackgroundTasks, request: Request):
    """Create interview sheet with title and description using new workflow."""
    _log_action(
        request,
        "create_sheet_new",
        name=payload.name,
        agent_type=payload.agent_type.value,
        roadmap=payload.roadmap,
        technology=payload.technology
    )
    
    try:
        result = controller.create_sheet_new(payload, background_tasks)
        
        _log_action(
            request,
            "create_sheet_new",
            status="success",
            session_id=result.sessionId
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "create_sheet_new",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/create-sheet", response_model=InterviewSheetResponse)
def create_sheet(payload: GenerateInterviewSheetRequest, request: Request):
    """Legacy endpoint for MDX-based sheet creation (DEPRECATED)."""
    _log_action(
        request,
        "create_interview_sheet_deprecated",
        mdx_file=payload.mdx_file,
        agent_type=payload.agent_type.value,
        technology=payload.technology
    )
    
    try:
        result = controller.create_sheet(payload)
        return result
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "create_interview_sheet_deprecated",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/generate-topic", response_model=SessionResponse)
async def generate_topic(payload: TopicGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Generate questions for a single topic."""
    _log_action(
        request,
        "generate_topic",
        topic=payload.topic,
        agent_type=payload.agent_type.value,
        technology=payload.technology,
        question_count=payload.question_count,
        roadmap=payload.roadmap,
        difficulty=payload.difficulty,
        generate_answers=payload.generate_answers
    )
    
    try:
        result = controller.generate_topic(payload, background_tasks)
        return result
    except Exception as e:
        _log_action(
            request,
            "generate_topic",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/bulk-generate")
async def bulk_generate(payload: BulkGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Start bulk generation for multiple topics."""
    _log_action(
        request,
        "bulk_generate",
        topics_count=len(payload.topics),
        generate_answers=payload.generate_answers,
        auto_publish=payload.auto_publish
    )
    
    try:
        result = controller.bulk_generate(payload, background_tasks)
        return result
    except Exception as e:
        _log_action(
            request,
            "bulk_generate",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/sessions")
def list_sessions(status: Optional[str] = None, request: Request = Request):
    """List all active/recent sessions."""
    _log_action(request, "list_interview_sessions", status_filter=status)
    
    try:
        sessions = controller.list_sessions(status)
        
        _log_action(
            request,
            "list_interview_sessions",
            sessions_count=len(sessions)
        )
        
        return sessions
    except Exception as e:
        _log_action(
            request,
            "list_interview_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/session/{session_id}/progress")
def get_session_progress(session_id: str, request: Request):
    """Get progress for a specific session."""
    _log_action(request, "get_session_progress", session_id=session_id)
    
    try:
        result = controller.get_session_progress(session_id)
        
        _log_action(
            request,
            "get_session_progress",
            session_id=session_id,
            status=result.get("status"),
            progress=result.get("progress", {})
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "get_session_progress",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/session/{session_id}/output")
def get_session_output(session_id: str, request: Request):
    """Get final output JSON for a completed session."""
    _log_action(request, "get_session_output", session_id=session_id)
    
    try:
        import json
        import os
        
        status = controller.get_session_progress(session_id)
        output_file = status.get("output_file")
        
        if not output_file or not os.path.exists(output_file):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            sheet_data = json.load(f)
        
        _log_action(
            request,
            "get_session_output",
            session_id=session_id,
            status="success"
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "sheet_data": sheet_data
        }
    except HTTPException:
        raise
    except Exception as e:
        _log_action(
            request,
            "get_session_output",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/{session_id}/cancel")
def cancel_session(session_id: str, request: Request):
    """Cancel a running session."""
    _log_action(request, "cancel_session", session_id=session_id)
    
    try:
        result = controller.cancel_session(session_id)
        
        _log_action(
            request,
            "cancel_session",
            session_id=session_id,
            status="cancelled"
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "cancel_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/session/{session_id}/resume")
async def resume_session(session_id: str, background_tasks: BackgroundTasks, request: Request):
    """Resume a session from where it left off."""
    _log_action(request, "resume_session", session_id=session_id)
    
    try:
        result = controller.retry_session(session_id, background_tasks)
        
        _log_action(
            request,
            "resume_session",
            session_id=session_id,
            status="resumed"
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


@router.post("/session/{session_id}/retry")
async def retry_session(session_id: str, background_tasks: BackgroundTasks, request: Request):
    """Retry a failed session (alias for resume)."""
    _log_action(request, "retry_session", session_id=session_id)
    
    try:
        result = controller.retry_session(session_id, background_tasks)
        
        _log_action(
            request,
            "retry_session",
            old_session_id=session_id,
            new_session_id=result.sessionId
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "retry_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/topic-templates")
def get_topic_templates(request: Request):
    """Get available topic templates."""
    _log_action(request, "get_topic_templates")
    
    try:
        result = controller.get_topic_templates()
        return result
    except Exception as e:
        _log_action(
            request,
            "get_topic_templates",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/roadmap-suggestions")
def get_roadmap_suggestions(request: Request):
    """Get roadmap suggestions."""
    _log_action(request, "get_roadmap_suggestions")
    
    try:
        result = controller.get_roadmap_suggestions()
        return result
    except Exception as e:
        _log_action(
            request,
            "get_roadmap_suggestions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.delete("/session/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a session."""
    _log_action(request, "delete_interview_session", session_id=session_id)
    
    try:
        result = controller.delete_session(session_id)
        
        _log_action(
            request,
            "delete_interview_session",
            session_id=session_id,
            status="success"
        )
        
        return result
    except Exception as e:
        _log_action(
            request,
            "delete_interview_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise

