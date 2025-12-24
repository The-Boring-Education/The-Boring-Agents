"""
Interview preparation API routes.

Routes define endpoints and delegate to controllers for business logic.
All operations are logged via middleware.

API Naming Conventions (REST-compliant):
- POST /sheets          - Create a new interview sheet
- POST /topics          - Generate questions for a single topic
- GET /sessions         - List all sessions
- GET /sessions/{id}    - Get session progress
- GET /sessions/{id}/output - Get session output
- POST /sessions/{id}/cancel - Cancel session
- POST /sessions/{id}/resume - Resume session
- POST /sessions/{id}/retry  - Retry session
- DELETE /sessions/{id} - Delete session
"""

import json
import logging
import os
from fastapi import APIRouter, BackgroundTasks, Request, HTTPException
from typing import Optional

from src.api.controllers.interview_prep_controller import InterviewPrepController
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    TopicGenerationRequest,
    BulkGenerationRequest,
    SessionResponse,
)
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview", tags=["interview"])

# Initialize controller
controller = InterviewPrepController()


# =============================================================================
# Sheet Operations
# =============================================================================

@router.post("/sheets", response_model=SessionResponse)
async def create_sheet(payload: CreateSheetRequest, background_tasks: BackgroundTasks, request: Request):
    """Create interview sheet with title and description."""
    print(f"Creating sheet: {payload}")
    log_action(
        request,
        "create_sheet",
        name=payload.name,
        agent_type=payload.agent_type.value,
        roadmap=payload.roadmap,
        technology=payload.technology
    )
    
    try:
        result = controller.create_sheet(payload, background_tasks)
        
        log_action(
            request,
            "create_sheet",
            status="success",
            session_id=result.sessionId
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "create_sheet",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


# =============================================================================
# Topic Operations
# =============================================================================

@router.post("/topics", response_model=SessionResponse)
async def generate_topic(payload: TopicGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Generate questions for a single topic."""
    log_action(
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
        log_action(
            request,
            "generate_topic",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/topics/bulk")
async def bulk_generate(payload: BulkGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Start bulk generation for multiple topics."""
    log_action(
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
        log_action(
            request,
            "bulk_generate",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


# =============================================================================
# Session Operations
# =============================================================================

@router.get("/sessions")
def list_sessions(status: Optional[str] = None, request: Request = Request):
    """List all active/recent sessions."""
    log_action(request, "list_sessions", status_filter=status)
    
    try:
        sessions = controller.list_sessions(status)
        
        log_action(
            request,
            "list_sessions",
            sessions_count=len(sessions)
        )
        
        return sessions
    except Exception as e:
        log_action(
            request,
            "list_sessions",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/sessions/{session_id}")
def get_session_progress(session_id: str, request: Request):
    """Get progress for a specific session."""
    log_action(request, "get_session_progress", session_id=session_id)
    
    try:
        result = controller.get_session_progress(session_id)
        
        log_action(
            request,
            "get_session_progress",
            session_id=session_id,
            status=result.get("status"),
            progress=result.get("progress", {})
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "get_session_progress",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/sessions/{session_id}/output")
def get_session_output(session_id: str, request: Request):
    """Get final output JSON for a completed session."""
    log_action(request, "get_session_output", session_id=session_id)
    
    try:
        status = controller.get_session_progress(session_id)
        output_file = status.get("output_file")
        
        if not output_file or not os.path.exists(output_file):
            raise HTTPException(status_code=404, detail="Output file not found")
        
        with open(output_file, 'r', encoding='utf-8') as f:
            sheet_data = json.load(f)
        
        log_action(
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
        log_action(
            request,
            "get_session_output",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/cancel")
def cancel_session(session_id: str, request: Request):
    """Cancel a running session."""
    log_action(request, "cancel_session", session_id=session_id)
    
    try:
        result = controller.cancel_session(session_id)
        
        log_action(
            request,
            "cancel_session",
            session_id=session_id,
            status="cancelled"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "cancel_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str, background_tasks: BackgroundTasks, request: Request):
    """Resume a session from where it left off."""
    log_action(request, "resume_session", session_id=session_id)
    
    try:
        result = controller.retry_session(session_id, background_tasks)
        
        log_action(
            request,
            "resume_session",
            session_id=session_id,
            status="resumed"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "resume_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.post("/sessions/{session_id}/retry")
async def retry_session(session_id: str, background_tasks: BackgroundTasks, request: Request):
    """Retry a failed session (alias for resume)."""
    log_action(request, "retry_session", session_id=session_id)
    
    try:
        result = controller.retry_session(session_id, background_tasks)
        
        log_action(
            request,
            "retry_session",
            old_session_id=session_id,
            new_session_id=result.sessionId
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "retry_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a session."""
    log_action(request, "delete_session", session_id=session_id)
    
    try:
        result = controller.delete_session(session_id)
        
        log_action(
            request,
            "delete_session",
            session_id=session_id,
            status="success"
        )
        
        return result
    except Exception as e:
        log_action(
            request,
            "delete_session",
            level="ERROR",
            session_id=session_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise


# =============================================================================
# Templates & Roadmaps
# =============================================================================

@router.get("/templates")
def get_topic_templates(request: Request):
    """Get available topic templates."""
    log_action(request, "get_templates")
    
    try:
        result = controller.get_topic_templates()
        return result
    except Exception as e:
        log_action(
            request,
            "get_templates",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise


@router.get("/roadmaps")
def get_roadmap_suggestions(request: Request):
    """Get roadmap suggestions."""
    log_action(request, "get_roadmaps")
    
    try:
        result = controller.get_roadmap_suggestions()
        return result
    except Exception as e:
        log_action(
            request,
            "get_roadmaps",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
