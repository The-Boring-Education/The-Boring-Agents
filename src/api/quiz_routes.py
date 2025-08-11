from fastapi import APIRouter, HTTPException
from typing import Optional
import logging

from ..agents.quiz.quiz_orchestrator import QuizOrchestrator
from ..agents.quiz.quiz_uploader import QuizUploader
from ..agents.quiz.types import QuizTopic
from ..utils.helpers import generate_filename
from .models import (
    GenerateQuizRequest,
    GenerateQuizAPIResponse,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    QuizTopicsResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/topics", response_model=QuizTopicsResponse)
def get_available_topics():
    """Return the list of available quiz topics supported by the orchestrator.

    This keeps Admin UI dynamic and in sync with agents.
    """
    topics = [t.value for t in QuizTopic]
    return QuizTopicsResponse(topics=topics)


@router.post("/generate", response_model=GenerateQuizAPIResponse)
def generate_quiz(payload: GenerateQuizRequest):
    # Log environment information for tracking
    env_info = f"env:{payload.environment or 'unknown'}"
    logger.info(f"Generating quiz for topic '{payload.topic}' with {payload.question_count} questions, target: {payload.target_audience}, {env_info}")
    
    orchestrator = QuizOrchestrator()
    result = orchestrator.generate_complete_quiz(
        topic=payload.topic,
        question_count=payload.question_count,
        target_audience=payload.target_audience,
    )

    # Save if requested (orchestrator already saves via its own flow; keep a stable filename)
    output_file: Optional[str] = None
    if payload.save and result:
        filename = generate_filename(prefix=f"quiz_{payload.topic.lower()}")
        orchestrator.save_content(result, filename)
        output_file = filename

    quiz_dict = result.get("quiz")
    if not quiz_dict:
        logger.error(f"Quiz generation failed for topic '{payload.topic}', {env_info}")
        raise HTTPException(status_code=500, detail="Quiz generation failed")

    logger.info(f"Successfully generated quiz for topic '{payload.topic}', session: {result.get('session_id', 'unknown')}, {env_info}")
    
    response = GenerateQuizAPIResponse(
        session_id=result.get("session_id", ""),
        output_file=output_file or result.get("output_file"),
        quiz=quiz_dict,
    )
    return response


@router.post("/validate", response_model=SimpleStatus)
def validate_quiz(payload: ValidateQuizRequest):
    logger.info("Validating quiz structure and content")
    uploader = QuizUploader()
    validation = uploader.validate_quiz(payload.quiz)
    status = validation.get("status")
    ok = status == "success"
    message = "Validation complete" if ok else "Validation failed"
    
    if ok:
        logger.info("Quiz validation successful")
    else:
        logger.warning(f"Quiz validation failed: {validation.get('message', 'Unknown error')}")
    
    return SimpleStatus(ok=ok, message=message)


@router.post("/upload", response_model=SimpleStatus)
def upload_quiz(payload: UploadQuizRequest):
    # Log environment information for tracking
    env_info = f"env:{payload.environment or 'unknown'}"
    logger.info(f"Uploading quiz to platform, {env_info}")
    
    uploader = QuizUploader(api_url=payload.api_url, admin_secret=payload.admin_secret or "TBEAdmin")
    result = uploader.upload_quiz(payload.quiz)
    ok = result.get("status") == "success"
    message = result.get("message", "Upload complete")
    
    if ok:
        logger.info(f"Quiz upload successful, {env_info}")
    else:
        logger.error(f"Quiz upload failed: {message}, {env_info}")
        raise HTTPException(status_code=400, detail=message)
    
    return SimpleStatus(ok=True, message=message)

