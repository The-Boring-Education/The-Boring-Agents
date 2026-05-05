"""Dedicated DSA API routes for admin topic-first generation."""

import logging

from fastapi import APIRouter, BackgroundTasks, Request

from src.api.controllers.dsa_controller import DSAController
from src.api.models.dsa_models import DSASessionResponse, DSATopicGenerationRequest
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dsa", tags=["dsa"])
controller = DSAController()


@router.post("/topics", response_model=DSASessionResponse)
async def generate_topic(
    payload: DSATopicGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Generate DSA questions + study guide by topic name."""
    log_action(
        request,
        "dsa_generate_topic",
        topic=payload.topic,
        question_count=payload.question_count,
        include_real_world=payload.include_real_world,
        difficulty=payload.difficulty,
    )
    return controller.generate_topic(payload, background_tasks)


@router.post("/generate-topic", response_model=DSASessionResponse)
async def generate_topic_alias(
    payload: DSATopicGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Alias endpoint for dashboard compatibility."""
    return await generate_topic(payload, background_tasks, request)


@router.get("/sessions")
def list_sessions(status: str = None, request: Request = None):
    """List DSA generation sessions."""
    log_action(request, "dsa_list_sessions", status_filter=status)
    return controller.list_sessions(status)


@router.get("/sessions/{session_id}")
def get_session_progress(session_id: str, request: Request):
    """Get DSA generation session progress."""
    log_action(request, "dsa_get_session_progress", session_id=session_id)
    return controller.get_session_progress(session_id)


@router.get("/sessions/{session_id}/output")
def get_session_output(session_id: str, request: Request):
    """Get output payload for a completed DSA session."""
    log_action(request, "dsa_get_session_output", session_id=session_id)
    return controller.get_session_output(session_id)


@router.post("/sessions/{session_id}/cancel")
def cancel_session(session_id: str, request: Request):
    """Cancel a DSA session."""
    log_action(request, "dsa_cancel_session", session_id=session_id)
    return controller.cancel_session(session_id)


@router.post("/sessions/{session_id}/resume", response_model=DSASessionResponse)
async def resume_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Resume a DSA session."""
    log_action(request, "dsa_resume_session", session_id=session_id)
    return controller.retry_session(session_id, background_tasks)


@router.post("/sessions/{session_id}/retry", response_model=DSASessionResponse)
async def retry_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Retry a DSA session."""
    log_action(request, "dsa_retry_session", session_id=session_id)
    return controller.retry_session(session_id, background_tasks)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a DSA session."""
    log_action(request, "dsa_delete_session", session_id=session_id)
    return controller.delete_session(session_id)
