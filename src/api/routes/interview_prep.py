"""Interview preparation API routes.

REST-compliant naming:
- POST   /sheets                              - Create a new interview sheet
- POST   /topics                              - Generate questions for a single topic
- POST   /generate-topic                      - Alias (dashboard compatibility)
- GET    /sessions                            - List all sessions
- GET    /sessions/{id}                       - Get session progress
- GET    /sessions/{id}/output                - Get session output
- POST   /sessions/{id}/cancel                - Cancel session
- POST   /sessions/{id}/resume                - Resume session
- POST   /sessions/{id}/retry                 - Retry session
- DELETE /sessions/{id}                       - Delete session
- PUT    /sessions/{id}/questions/{qid}       - Update question
- GET    /sessions/{id}/questions/{qid}       - Get question
- DELETE /sessions/{id}/questions/{qid}       - Delete question
- POST   /sessions/{id}/questions             - Add question
"""

import json
import logging
import os
from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from src.api.controllers.interview_prep_controller import InterviewPrepController
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    TopicGenerationRequest,
    SessionResponse,
    TopicTemplate,
    RoadmapSuggestion,
    SimpleStatus,
    UploadSheetRequest,
    ValidateSheetRequest,
)
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interview", tags=["interview"])
controller = InterviewPrepController()


# ---------------------------------------------------------------------------
# Sheet operations
# ---------------------------------------------------------------------------

@router.post("/sheets", response_model=SessionResponse)
async def create_sheet(payload: CreateSheetRequest, background_tasks: BackgroundTasks, request: Request):
    """Create interview sheet with title and description."""
    logger.info("Creating sheet: %s", payload.name)
    log_action(request, "create_sheet", name=payload.name, agent_type=payload.agent_type.value, roadmap=payload.roadmap, technology=payload.technology)
    try:
        result = controller.create_sheet(payload, background_tasks)
        log_action(request, "create_sheet", status="success", session_id=result.sessionId)
        return result
    except Exception as e:
        log_action(request, "create_sheet", level="ERROR", error=str(e), error_type=type(e).__name__)
        raise


@router.post("/validate", response_model=SimpleStatus)
async def validate_sheet(payload: ValidateSheetRequest, request: Request):
    """Validate an interview sheet's structure before uploading."""
    log_action(request, "validate_sheet")
    try:
        return controller.validate_sheet(payload)
    except Exception as e:
        log_action(request, "validate_sheet", level="ERROR", error=str(e))
        raise

@router.post("/upload", response_model=SimpleStatus)
async def upload_sheet(payload: UploadSheetRequest, request: Request):
    """Upload a finalized interview sheet to the database."""
    log_action(request, "upload_sheet")
    try:
        return controller.upload_sheet(payload)
    except Exception as e:
        log_action(request, "upload_sheet", level="ERROR", error=str(e))
        raise

# ---------------------------------------------------------------------------
# Topic operations
# ---------------------------------------------------------------------------

@router.post("/topics", response_model=SessionResponse)
async def generate_topic(payload: TopicGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Generate questions for a single topic."""
    log_action(request, "generate_topic", topic=payload.topic, agent_type=payload.agent_type.value, question_count=payload.question_count)
    try:
        return controller.generate_topic(payload, background_tasks)
    except Exception as e:
        log_action(request, "generate_topic", level="ERROR", error=str(e), error_type=type(e).__name__)
        raise


@router.post("/generate-topic", response_model=SessionResponse)
async def generate_topic_alias(payload: TopicGenerationRequest, background_tasks: BackgroundTasks, request: Request):
    """Alias for /topics (dashboard compatibility)."""
    return await generate_topic(payload, background_tasks, request)


# ---------------------------------------------------------------------------
# Session operations
# ---------------------------------------------------------------------------

@router.get("/sessions")
def list_sessions(status: Optional[str] = None, request: Request = None):
    """List all active/recent sessions."""
    log_action(request, "list_sessions", status_filter=status)
    try:
        sessions = controller.list_sessions(status)
        log_action(request, "list_sessions", sessions_count=len(sessions))
        return sessions
    except Exception as e:
        log_action(request, "list_sessions", level="ERROR", error=str(e), error_type=type(e).__name__)
        raise


@router.get("/sessions/{session_id}")
def get_session_progress(session_id: str, request: Request):
    """Get progress for a specific session."""
    log_action(request, "get_session_progress", session_id=session_id)
    try:
        result = controller.get_session_progress(session_id)
        log_action(request, "get_session_progress", session_id=session_id, status=result.get("status"))
        return result
    except Exception as e:
        log_action(request, "get_session_progress", level="ERROR", session_id=session_id, error=str(e))
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
        with open(output_file, "r", encoding="utf-8") as f:
            sheet_data = json.load(f)
        return {"status": "success", "session_id": session_id, "sheet_data": sheet_data}
    except HTTPException:
        raise
    except Exception as e:
        log_action(request, "get_session_output", level="ERROR", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/cancel")
def cancel_session(session_id: str, request: Request):
    """Cancel a running session."""
    log_action(request, "cancel_session", session_id=session_id)
    try:
        return controller.cancel_session(session_id)
    except Exception as e:
        log_action(request, "cancel_session", level="ERROR", session_id=session_id, error=str(e))
        raise


@router.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str, background_tasks: BackgroundTasks, request: Request):
    """Resume a session from where it left off."""
    log_action(request, "resume_session", session_id=session_id)
    try:
        return controller.retry_session(session_id, background_tasks)
    except Exception as e:
        log_action(request, "resume_session", level="ERROR", session_id=session_id, error=str(e))
        raise


@router.post("/sessions/{session_id}/retry")
async def retry_session(session_id: str, background_tasks: BackgroundTasks, request: Request):
    """Retry a failed session."""
    log_action(request, "retry_session", session_id=session_id)
    try:
        return controller.retry_session(session_id, background_tasks)
    except Exception as e:
        log_action(request, "retry_session", level="ERROR", session_id=session_id, error=str(e))
        raise


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, request: Request):
    """Delete a session."""
    log_action(request, "delete_session", session_id=session_id)
    try:
        return controller.delete_session(session_id)
    except Exception as e:
        log_action(request, "delete_session", level="ERROR", session_id=session_id, error=str(e))
        raise

@router.put("/sessions/{session_id}/sheet")
async def update_session_sheet(session_id: str, payload: dict, request: Request):
    """Update the entire sheet data for a session."""
    log_action(request, "update_session_sheet", session_id=session_id)
    try:
        sheet_data = payload.get("sheetData")
        if not sheet_data:
            raise HTTPException(status_code=400, detail="No sheetData provided")
        return controller.update_session_sheet(session_id, sheet_data)
    except HTTPException:
        raise
    except Exception as e:
        log_action(request, "update_session_sheet", level="ERROR", session_id=session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Question CRUD (under /sessions/ for consistency)
# ---------------------------------------------------------------------------

@router.put("/sessions/{session_id}/questions/{question_id}")
async def update_question(session_id: str, question_id: str, updates: dict, request: Request):
    """Update a generated question in a session."""
    log_action(request, "update_question", session_id=session_id, question_id=question_id)
    try:
        if not updates:
            raise HTTPException(status_code=400, detail="No updates provided")
        return controller.update_question(session_id, question_id, updates)
    except HTTPException:
        raise
    except Exception as e:
        log_action(request, "update_question", level="ERROR", session_id=session_id, question_id=question_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update question")


@router.get("/sessions/{session_id}/questions/{question_id}")
async def get_question(session_id: str, question_id: str, request: Request):
    """Get a single question from a session."""
    try:
        return controller.get_question(session_id, question_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}/questions/{question_id}")
async def delete_question(session_id: str, question_id: str, request: Request):
    """Delete a question from a session."""
    try:
        return controller.delete_question(session_id, question_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/questions")
async def add_question(session_id: str, question: dict, request: Request):
    """Add a new question to a session."""
    try:
        return controller.add_question(session_id, question)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Dashboard backward-compatibility aliases (singular /session/)
# These redirect to the canonical /sessions/ endpoints.
# ---------------------------------------------------------------------------

@router.get("/session/{session_id}")
def get_session_progress_alias(session_id: str, request: Request):
    return get_session_progress(session_id, request)


@router.get("/session/{session_id}/output")
def get_session_output_alias(session_id: str, request: Request):
    return get_session_output(session_id, request)


@router.delete("/session/{session_id}")
def delete_session_alias(session_id: str, request: Request):
    return delete_session(session_id, request)


@router.put("/session/{session_id}/questions/{question_id}")
async def update_question_alias(session_id: str, question_id: str, updates: dict, request: Request):
    return await update_question(session_id, question_id, updates, request)


@router.get("/session/{session_id}/questions/{question_id}")
async def get_question_alias(session_id: str, question_id: str, request: Request):
    return await get_question(session_id, question_id, request)


@router.delete("/session/{session_id}/questions/{question_id}")
async def delete_question_alias(session_id: str, question_id: str, request: Request):
    return await delete_question(session_id, question_id, request)


@router.post("/session/{session_id}/questions")
async def add_question_alias(session_id: str, question: dict, request: Request):
    return await add_question(session_id, question, request)

@router.put("/session/{session_id}/sheet")
async def update_session_sheet_alias(session_id: str, payload: dict, request: Request):
    return await update_session_sheet(session_id, payload, request)


@router.get("/session/{session_id}/session")
def get_session_alias_alt(session_id: str, request: Request):
    """Extra alias for dashboard /session/{id}/session requests."""
    return get_session_progress(session_id, request)

# ---------------------------------------------------------------------------
# Template operations
# ---------------------------------------------------------------------------

@router.get("/topic-templates", response_model=List[TopicTemplate])
def get_topic_templates(request: Request):
    """Get available topic templates."""
    log_action(request, "get_topic_templates")
    return controller.get_topic_templates()


@router.get("/roadmap-suggestions", response_model=List[RoadmapSuggestion])
def get_roadmap_suggestions(request: Request):
    """Get roadmap suggestions."""
    log_action(request, "get_roadmap_suggestions")
    return controller.get_roadmap_suggestions()


# ---------------------------------------------------------------------------
# DSA Content Generation
# ---------------------------------------------------------------------------

from src.api.controllers.dsa_content_controller import DSAContentController
from src.api.models.dsa_content_models import (
    DSAContentBulkEnrichRequest,
    DSAContentBulkEnrichResponse,
    DSAContentEnrichRequest,
    DSAContentGenerateRequest,
    DSAContentGenerateResponse,
)

dsa_content_controller = DSAContentController()


@router.post("/dsa-content/generate", response_model=DSAContentGenerateResponse)
async def generate_dsa_content(payload: DSAContentGenerateRequest, request: Request):
    """Generate structured DSA content sections for a question.

    Produces a JSON object with 8 educational sections:
    first_principles, constraints, examples, ways_to_solve,
    how_to_approach, pseudo_code, working_code, common_mistakes.
    """
    log_action(
        request,
        "generate_dsa_content",
        question=payload.question[:60],
        topic=payload.topic,
        difficulty=payload.difficulty,
    )
    try:
        result = dsa_content_controller.generate_content(payload)
        log_action(
            request,
            "generate_dsa_content",
            status="success" if result.status == "success" else "error",
            question=payload.question[:60],
        )
        return result
    except Exception as e:
        log_action(
            request,
            "generate_dsa_content",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/dsa-content/enrich/{question_id}", response_model=DSAContentGenerateResponse
)
async def enrich_dsa_content(
    question_id: str, payload: DSAContentEnrichRequest, request: Request
):
    """Auto-enrich a DSA question by fetching its metadata from TBE-Web,
    generating interactive content sections, and pushing them back.
    """
    log_action(request, "enrich_dsa_content", question_id=question_id)
    try:
        result = dsa_content_controller.enrich_content(question_id, payload)
        log_action(
            request,
            "enrich_dsa_content",
            status="success" if result.status == "success" else "error",
            question_id=question_id,
        )
        return result
    except Exception as e:
        log_action(
            request,
            "enrich_dsa_content",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/dsa-content/bulk-enrich", response_model=DSAContentBulkEnrichResponse
)
async def bulk_enrich_dsa_content(
    payload: DSAContentBulkEnrichRequest, request: Request
):
    """Bulk enrich DSA questions that are missing interactive content sections.
    Includes rate limiting to avoid API exhaustion.
    """
    log_action(
        request,
        "bulk_enrich_dsa_content",
        limit=payload.limit,
        delay=payload.delay,
        force=payload.force,
    )
    try:
        result = dsa_content_controller.bulk_enrich_content(payload)
        log_action(
            request,
            "bulk_enrich_dsa_content",
            status=result.status,
            enriched=result.enriched_count,
            failed=result.failed_count,
        )
        return result
    except Exception as e:
        log_action(
            request,
            "bulk_enrich_dsa_content",
            level="ERROR",
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(status_code=500, detail=str(e))
