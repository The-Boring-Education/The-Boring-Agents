"""Shiksha API routes for admin topic-first course generation."""

import logging

from fastapi import APIRouter, BackgroundTasks, Request

from src.api.controllers.shiksha_controller import ShikshaController
from src.api.models.shiksha_models import (
    ShikshaPushRequest,
    ShikshaPushResponse,
    ShikshaSessionResponse,
    ShikshaTopicGenerationRequest,
)
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/shiksha", tags=["shiksha"])
controller = ShikshaController()


@router.post("/topics", response_model=ShikshaSessionResponse)
async def generate_topic(
    payload: ShikshaTopicGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Generate a Shiksha course bundle by topic name."""
    log_action(
        request,
        "shiksha_generate_topic",
        topic=payload.topic,
        chapter_count=payload.chapter_count,
        difficulty=payload.difficulty,
    )
    return controller.generate_topic(payload, background_tasks)


@router.post("/generate-topic", response_model=ShikshaSessionResponse)
async def generate_topic_alias(
    payload: ShikshaTopicGenerationRequest,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Alias endpoint for dashboard compatibility."""
    return await generate_topic(payload, background_tasks, request)


@router.get("/sessions")
def list_sessions(status: str = None, request: Request = None):
    """List Shiksha generation sessions."""
    log_action(request, "shiksha_list_sessions", status_filter=status)
    return controller.list_sessions(status)


@router.get("/sessions/{session_id}")
def get_session_progress(session_id: str, request: Request):
    """Get Shiksha generation session progress."""
    log_action(request, "shiksha_get_session_progress", session_id=session_id)
    return controller.get_session_progress(session_id)


@router.get("/sessions/{session_id}/output")
def get_session_output(session_id: str, request: Request):
    """Get output Bundle for a completed Shiksha session."""
    log_action(request, "shiksha_get_session_output", session_id=session_id)
    return controller.get_session_output(session_id)


@router.post("/sessions/{session_id}/cancel")
def cancel_session(session_id: str, request: Request):
    """Cancel a Shiksha session."""
    log_action(request, "shiksha_cancel_session", session_id=session_id)
    return controller.cancel_session(session_id)


@router.post("/sessions/{session_id}/resume", response_model=ShikshaSessionResponse)
async def resume_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Resume a Shiksha session."""
    log_action(request, "shiksha_resume_session", session_id=session_id)
    return controller.retry_session(session_id, background_tasks)


@router.post("/sessions/{session_id}/retry", response_model=ShikshaSessionResponse)
async def retry_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Retry a Shiksha session."""
    log_action(request, "shiksha_retry_session", session_id=session_id)
    return controller.retry_session(session_id, background_tasks)


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a Shiksha session."""
    log_action(request, "shiksha_delete_session", session_id=session_id)
    return controller.delete_session(session_id)


@router.post("/sessions/{session_id}/push", response_model=ShikshaPushResponse)
def push_session_to_db(
    session_id: str,
    payload: ShikshaPushRequest,
    request: Request,
):
    """Push a generated Bundle to TBE-Web import (lands as Draft)."""
    log_action(
        request,
        "shiksha_push_session",
        session_id=session_id,
        environment=payload.environment,
        dry_run=payload.dry_run,
    )
    return controller.push_session_to_db(
        session_id,
        environment=payload.environment,
        dry_run=payload.dry_run,
    )
