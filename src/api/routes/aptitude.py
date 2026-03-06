"""Aptitude API routes.

- POST /generate         - Generate answers for a single topic
- POST /generate-batch   - Generate answers for multiple topics
- GET  /topics           - List all registered topics
- POST /upload           - Upload generated data to TBE-Web API
"""

import logging
from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from src.api.controllers.aptitude_controller import AptitudeController
from src.api.models.aptitude_models import (
    AptitudeBatchRequest,
    AptitudeBatchResponse,
    AptitudeTopicRequest,
    AptitudeTopicResponse,
    AptitudeUploadRequest,
    SimpleStatus,
)
from src.utils.request_logging import log_action

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aptitude", tags=["aptitude"])
controller = AptitudeController()


@router.post("/generate", response_model=AptitudeTopicResponse)
async def generate_for_topic(
    payload: AptitudeTopicRequest,
    background_tasks: BackgroundTasks,
    request: Request,
):
    """Generate answers for a single aptitude topic."""
    log_action(request, "aptitude_generate", topic=payload.topic_name, questions=len(payload.questions))
    try:
        result = controller.generate_for_topic(
            topic_name=payload.topic_name,
            questions=payload.questions,
            category=payload.category,
            sub_category=payload.sub_category,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Generate failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-batch", response_model=AptitudeBatchResponse)
async def generate_batch(
    payload: AptitudeBatchRequest,
    request: Request,
):
    """Generate answers for multiple topics in batch."""
    log_action(request, "aptitude_batch", topics=len(payload.topics))
    try:
        topics_data = [
            {
                "name": t.topic_name,
                "questions": t.questions,
                "category": t.category,
                "subCategory": t.sub_category,
            }
            for t in payload.topics
        ]
        result = controller.generate_batch(topics_data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Batch generate failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/topics")
def list_topics(request: Request):
    """List all registered aptitude topics."""
    log_action(request, "aptitude_list_topics")
    return controller.get_topic_registry()


@router.post("/upload", response_model=SimpleStatus)
async def upload_to_api(payload: AptitudeUploadRequest, request: Request):
    """Upload generated aptitude data to TBE-Web database."""
    log_action(request, "aptitude_upload", file=payload.output_file)
    try:
        result = controller.upload_to_api(
            output_file=payload.output_file,
            api_url=payload.api_url,
            admin_secret=payload.admin_secret or "TBEAdmin",
        )
        return SimpleStatus(ok=result["ok"], message=result["message"])
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Upload failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
