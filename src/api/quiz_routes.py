from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
import os
import logging

from ..agents.quiz.quiz_orchestrator import QuizOrchestrator
from ..agents.quiz.quiz_uploader import QuizUploader
from ..agents.quiz.types import QuizTopic
from ..utils.helpers import generate_filename
from ..utils.helpers import load_json_file
from ..utils.session_logger import read_logs
from ..core.config import config
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
    action_type = "generate_quiz"
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
        logger.error(f"Quiz generation failed for topic '{payload.topic}', action: {action_type}, {env_info}")
        raise HTTPException(status_code=500, detail="Quiz generation failed")

    logger.info(f"Successfully generated quiz for topic '{payload.topic}', session: {result.get('session_id', 'unknown')}, action: {action_type}, {env_info}")
    
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


# Additional Quiz endpoints used by Admin UI

@router.get("/sessions")
def list_quiz_sessions():
    orchestrator = QuizOrchestrator()
    return orchestrator.list_active_sessions()


@router.get("/progress/{session_id}")
def get_quiz_progress(session_id: str):
    """Return progress details for a quiz generation session.

    Computes a percent based on steps completed and question generation progress.
    """
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

    # Compute percent: 4 steps (research, planning, generation, metadata)
    steps_completed: List[str] = data.get("steps_completed", []) or []
    current_step = data.get("current_step") or ""
    base_steps = {"research", "planning", "generation", "metadata"}
    completed_steps = len([s for s in steps_completed if s in base_steps])
    percent = completed_steps * 25.0
    # If currently generating, add partial progress within the generation step (worth 25%)
    if current_step == "generation" and total > 0:
        percent = 50.0 + min(25.0, (generated / total) * 25.0)
    # Clamp and finalize for completed
    if data.get("status") == "completed" or current_step == "completed":
        percent = 100.0

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


@router.get("/logs/{session_id}")
def get_quiz_logs(session_id: str, limit: int = 200):
    """Proxy to session logs for convenience under quiz namespace."""
    logs = read_logs(session_id=session_id, limit=max(1, min(limit, 2000)))
    return {"session_id": session_id, "logs": logs}


@router.get("/pending")
def list_pending_quizzes():
    """List quiz JSON files in the output directory as pending items for upload."""
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
            # Skip unreadable files
            continue

    # Sort newest first if metadata has created timestamp embedded in filename order is enough
    pending.sort(key=lambda x: x.get("filename", ""), reverse=True)
    return {"pending": pending}


@router.delete("/pending/{filename}")
def delete_pending_quiz(filename: str):
    out_path = os.path.join(config.output_dir, filename)
    if not os.path.isfile(out_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        os.remove(out_path)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending/{filename}/content")
def get_pending_quiz_content(filename: str):
    out_path = os.path.join(config.output_dir, filename)
    if not os.path.isfile(out_path):
        raise HTTPException(status_code=404, detail="File not found")
    try:
        return load_json_file(out_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

