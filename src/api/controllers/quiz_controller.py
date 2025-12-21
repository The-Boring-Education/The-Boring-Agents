"""
Quiz generation controller.

Handles all business logic for quiz operations.
"""

import json
import logging
import os
from typing import Optional, List, Dict, Any
from fastapi import HTTPException

from ...agents.quiz.quiz_orchestrator import QuizOrchestrator
from ...agents.quiz.quiz_uploader import QuizUploader
from ...agents.quiz.types import QuizTopic
from ...utils.helpers import generate_filename, load_json_file
from ...utils.session_logger import read_logs
from ...core.config import config
from ...core.env import get_env_manager
from ..models.quiz_models import (
    GenerateQuizRequest,
    GenerateQuizAPIResponse,
    ValidateQuizRequest,
    UploadQuizRequest,
    SimpleStatus,
    QuizTopicsResponse,
)

logger = logging.getLogger(__name__)
env_manager = get_env_manager()


class QuizController:
    """Controller for quiz generation operations."""
    
    def __init__(self):
        """Initialize the quiz controller."""
        self.orchestrator = QuizOrchestrator()
        self.uploader = QuizUploader()
    
    def get_available_topics(self) -> QuizTopicsResponse:
        """Get list of available quiz topics."""
        topics = [t.value for t in QuizTopic]
        return QuizTopicsResponse(topics=topics)
    
    def generate_quiz(self, payload: GenerateQuizRequest) -> GenerateQuizAPIResponse:
        """Generate a complete quiz for a technology topic."""
        environment = payload.environment or env_manager.get("ENVIRONMENT", "dev")
        
        try:
            result = self.orchestrator.generate_complete_quiz(
                topic=payload.topic,
                question_count=payload.question_count,
                target_audience=payload.target_audience,
            )

            # Save if requested
            output_file: Optional[str] = None
            if payload.save and result:
                filename = generate_filename(prefix=f"quiz_{payload.topic.lower()}")
                self.orchestrator.save_content(result, filename)
                output_file = filename

            quiz_dict = result.get("quiz")
            if not quiz_dict:
                raise HTTPException(status_code=500, detail="Quiz generation failed - no quiz data returned")

            session_id = result.get("session_id", "unknown")
            
            return GenerateQuizAPIResponse(
                session_id=session_id,
                output_file=output_file or result.get("output_file"),
                quiz=quiz_dict,
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")
    
    def validate_quiz(self, payload: ValidateQuizRequest) -> SimpleStatus:
        """Validate a quiz structure and content."""
        try:
            validation = self.uploader.validate_quiz(payload.quiz)
            status = validation.get("status")
            ok = status == "success"
            message = "Validation complete" if ok else "Validation failed"
            
            return SimpleStatus(ok=ok, message=message)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
    
    def upload_quiz(self, payload: UploadQuizRequest) -> SimpleStatus:
        """Upload a quiz to the database."""
        environment = payload.environment or env_manager.get("ENVIRONMENT", "dev")
        
        try:
            uploader = QuizUploader(api_url=payload.api_url, admin_secret=payload.admin_secret or "TBEAdmin")
            result = uploader.upload_quiz(payload.quiz)
            ok = result.get("status") == "success"
            message = result.get("message", "Upload complete")
            
            if not ok:
                raise HTTPException(status_code=400, detail=message)
            
            return SimpleStatus(ok=True, message=message)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    def list_sessions(self) -> Dict[str, Any]:
        """List all active quiz generation sessions."""
        try:
            result = self.orchestrator.list_active_sessions()
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")
    
    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress details for a quiz generation session."""
        try:
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

            # Compute percent
            steps_completed: List[str] = data.get("steps_completed", []) or []
            current_step = data.get("current_step") or ""
            base_steps = {"research", "planning", "generation", "metadata"}
            completed_steps = len([s for s in steps_completed if s in base_steps])
            percent = completed_steps * 25.0
            
            if current_step == "generation" and total > 0:
                percent = 50.0 + min(25.0, (generated / total) * 25.0)
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")
    
    def get_logs(self, session_id: str, limit: int = 200) -> Dict[str, Any]:
        """Get session logs for a quiz."""
        try:
            logs = read_logs(session_id=session_id, limit=max(1, min(limit, 2000)))
            return {"session_id": session_id, "logs": logs}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")
    
    def list_pending_quizzes(self) -> Dict[str, Any]:
        """List quiz JSON files in the output directory as pending items for upload."""
        try:
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
                    continue

            pending.sort(key=lambda x: x.get("filename", ""), reverse=True)
            return {"pending": pending}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list pending quizzes: {str(e)}")
    
    def delete_pending_quiz(self, filename: str) -> Dict[str, bool]:
        """Delete a pending quiz file."""
        try:
            out_path = os.path.join(config.output_dir, filename)
            if not os.path.isfile(out_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            os.remove(out_path)
            return {"ok": True}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def get_pending_quiz_content(self, filename: str) -> Dict[str, Any]:
        """Get the content of a pending quiz file."""
        try:
            out_path = os.path.join(config.output_dir, filename)
            if not os.path.isfile(out_path):
                raise HTTPException(status_code=404, detail="File not found")
            
            content = load_json_file(out_path)
            return content
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

