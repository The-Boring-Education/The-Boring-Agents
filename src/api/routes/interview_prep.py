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


# Alias endpoint for dashboard compatibility
@router.post("/generate-topic", response_model=SessionResponse)
async def generate_topic_alias(payload: TopicGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Alias for /topics endpoint (dashboard calls this instead of /topics)."""
    return await generate_topic(payload, background_tasks, request)


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


# Dashboard-compatible aliases
@router.get("/session/{session_id}")
def get_session_progress_alias(session_id: str, request: Request):
    """Alias for /sessions/{id} endpoint (dashboard compatibility)."""
    return get_session_progress(session_id, request)


@router.get("/session/{session_id}/output")
def get_session_output_alias(session_id: str, request: Request):
    """Alias for /sessions/{id}/output endpoint (dashboard compatibility)."""
    return get_session_output(session_id, request)


@router.delete("/session/{session_id}")
def delete_session_alias(session_id: str, request: Request):
    """Delete a session (dashboard compatibility - singular 'session')."""
    log_action(request, "delete_session", session_id=session_id)
    
    try:
        session_manager = controller.session_manager
        session_manager.delete_session(session_id)
        
        log_action(
            request,
            "delete_session",
            session_id=session_id,
            status="deleted"
        )
        
        return {
            "status": "success",
            "message": f"Session {session_id} deleted successfully"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    except Exception as e:
        log_action(
            request,
            "delete_session",
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

@router.put("/session/{session_id}/questions/{question_id}")
async def update_question(
    session_id: str,
    question_id: str,
    updates: dict,
    request: Request
):
    """
    Update a generated question in a session.
    """
    log_action(
        request,
        "update_question",
        session_id=session_id,
        question_id=question_id,
        updates_keys=list(updates.keys())
    )
    
    try:
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
            
        result = controller.update_question(session_id, question_id, updates)
        
        log_action(
            request,
            "update_question",
            session_id=session_id,
            question_id=question_id,
            status="success"
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        log_action(
            request,
            "update_question",
            level="ERROR",
            session_id=session_id,
            question_id=question_id,
            error=str(e),
            error_type=type(e).__name__
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/questions/{question_id}")
async def get_question(
    session_id: str,
    question_id: str,
    request: Request
):
    """Get a single question from a session."""
    try:
        return controller.get_question(session_id, question_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}/questions/{question_id}")
async def delete_question(
    session_id: str,
    question_id: str,
    request: Request
):
    """Delete a question from a session."""
    try:
        return controller.delete_question(session_id, question_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/{session_id}/questions")
async def add_question(
    session_id: str,
    question: dict,
    request: Request
):
    """Add a new question to a session."""
    try:
        return controller.add_question(session_id, question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))