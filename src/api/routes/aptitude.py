"""Aptitude API routes.

- POST /generate         - Generate answers for a single topic
- POST /generate-batch   - Generate answers for multiple topics
- GET  /topics           - List all registered topics
- POST /upload           - Upload generated data to TBE-Web API
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from src.api.controllers.aptitude_controller import AptitudeController
from src.api.models.aptitude_models import (
    AptitudeBatchRequest,
    AptitudeBatchResponse,
    AptitudeGenerateRequest,
    AptitudeGenerateResponse,
    AptitudeUploadRequest,
    SimpleStatus,
)
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aptitude", tags=["aptitude"])
controller = AptitudeController()


@router.post("/generate", response_model=AptitudeGenerateResponse)
async def generate_for_topic(payload: AptitudeGenerateRequest, request: Request):
    """Generate answers for a single aptitude topic.

    Accepts:
    - topic (slug or name) — required
    - questions (list of strings) — optional, provide your own questions
    - numQuestions (int) — optional, how many to auto-generate (min 10)
    - If neither questions nor numQuestions: generates 10 questions
    """
    log_action(request, "aptitude_generate", topic=payload.topic)
    try:
        result = controller.generate_for_topic(
            topic=payload.topic,
            questions=payload.questions,
            num_questions=payload.num_questions,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Generate failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch", response_model=AptitudeBatchResponse)
async def generate_batch(payload: AptitudeBatchRequest, request: Request):
    """Generate answers for multiple topics in batch.

    Accepts a list of topic slugs/names. Each topic gets numQuestions (default 10).
    """
    log_action(request, "aptitude_batch", topics=len(payload.topics))
    try:
        result = controller.generate_batch(
            topics=payload.topics,
            num_questions=payload.num_questions,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Batch generate failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics")
def list_topics(request: Request):
    """List all registered aptitude topics with slugs."""
    log_action(request, "aptitude_list_topics")
    return controller.get_topic_registry()


@router.post("/upload", response_model=SimpleStatus)
async def upload_to_api(payload: AptitudeUploadRequest, request: Request):
    """Upload generated aptitude data to TBE-Web database via bulk upload API."""
    log_action(request, "aptitude_upload", file=payload.output_file)
    try:
        result = controller.upload_to_api(
            output_file=payload.output_file,
            api_url=payload.api_url,
            admin_secret=payload.admin_secret,
        )
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Upload failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
