"""
Quiz generation controller.

Handles all business logic for quiz operations.
Matches the Interview Prep controller pattern for consistency.

NOTE: This controller references QuizWorkflowOrchestrator which you need to implement
in src/agents/quiz/workflow/orchestrator.py using LangGraph.
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, BackgroundTasks

# TODO: Implement QuizWorkflowOrchestrator in src/agents/quiz/workflow/orchestrator.py
# Uncomment the import below once implemented:
from src.agents.quiz.workflow.orchestrator import QuizWorkflowOrchestrator

from src.core.session.session_types import SessionStatus
from src.core.env import get_env_manager
from src.api.models.quiz_models import (
    CreateQuizRequest,
    TopicGenerationRequest,
    UploadQuizRequest,
    ValidateQuizRequest,
    SessionResponse,
    SimpleStatus,
)

logger = logging.getLogger(__name__)
env_manager = get_env_manager()


class QuizController:
    """Controller for quiz generation operations.
    
    Pattern matches InterviewPrepController for consistency.
    """
    
    def __init__(self):
        """Initialize the quiz controller."""
        self.orchestrator = QuizWorkflowOrchestrator()
    
    def _check_orchestrator(self):
        """Check if orchestrator is available."""
        if not self.orchestrator:
            raise HTTPException(
                status_code=501,
                detail="QuizWorkflowOrchestrator not implemented yet. Implement it in src/agents/quiz/workflow/orchestrator.py"
            )
    
    # =========================================================================
    # Quiz Creation
    # =========================================================================
    
    def create_quiz(
        self,
        payload: CreateQuizRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """
        Create quiz using workflow orchestrator.
        
        Args:
            payload: Create quiz request
            background_tasks: FastAPI background tasks
            
        Returns:
            Session response
        """
        self._check_orchestrator()
        
        try:
            # Create description if not provided
            description = payload.description or f"Quiz for {payload.topic}. Difficulty: {payload.difficulty.value}."
            
            session_id = self.orchestrator.start_generation(
                topic=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                question_count=payload.question_count,
                target_audience=payload.target_audience,
                difficulty=payload.difficulty.value
            )
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating quiz: {payload.topic}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating quiz: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def _execute_workflow_background(self, session_id: str):
        """
        Execute workflow in background.
        
        Args:
            session_id: Session ID
        """
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as e:
            logger.error(f"Error executing quiz workflow for session {session_id}: {e}")
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active/recent quiz sessions."""
        self._check_orchestrator()
        
        # Get sessions from orchestrator
        orchestrator_sessions = self.orchestrator.session_manager.list_sessions(status)
        
        # Convert to expected format (matching Interview Prep pattern)
        formatted_sessions = []
        for session in orchestrator_sessions:
            progress = session.get("progress", {})
            questions = session.get("questions", [])
            
            # Get question_count with fallbacks
            question_count = session.get("question_count")
            if not question_count or question_count is None:
                question_count = progress.get("total") or len(questions) or 20
                session["question_count"] = question_count
                try:
                    self.orchestrator.session_manager.save_session(session["session_id"], session)
                except Exception as e:
                    logger.warning(f"Failed to save question_count for session {session['session_id']}: {e}")
            
            final_question_count = int(question_count) if question_count else 20
            
            formatted_sessions.append({
                "sessionId": session["session_id"],
                "topic": session.get("topic", session.get("name", "Unknown")),
                "agentType": session.get("agent_type", "generic"),
                "targetAudience": session.get("target_audience", "developers"),
                "questionCount": final_question_count,
                "question_count": final_question_count,  # snake_case for compatibility
                "status": session["status"],
                "progress": progress,
                "startedAt": session["created_at"],
                "completedAt": session.get("updated_at") if session["status"] == "completed" else None,
                "outputFile": session.get("output_file"),
                "quizData": session.get("quiz_data"),
                "error": session.get("error")
            })
        
        return formatted_sessions
    
    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress for a specific quiz session."""
        self._check_orchestrator()
        
        try:
            session_status = self.orchestrator.get_session_status(session_id)
            
            # Ensure both camelCase and snake_case versions are present
            question_count = session_status.get("question_count")
            if question_count is not None:
                session_status["questionCount"] = question_count
            elif "questionCount" not in session_status:
                questions = session_status.get("questions", [])
                progress = session_status.get("progress", {})
                question_count = progress.get("total") or len(questions) or 20
                session_status["question_count"] = question_count
                session_status["questionCount"] = question_count
            
            return session_status
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def cancel_session(self, session_id: str) -> Dict[str, str]:
        """Cancel a running quiz session."""
        self._check_orchestrator()
        
        try:
            session = self.orchestrator.get_session_status(session_id)
            if session["status"] == "in_progress":
                self.orchestrator.session_manager.update_status(
                    session_id,
                    SessionStatus.FAILED,
                    current_step="Cancelled by user",
                    error="Cancelled by user"
                )
                from ...utils.session_logger import append_log
                append_log(session_id, "session_cancelled", {})
            return {"message": "Session cancelled"}
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def retry_session(
        self,
        session_id: str,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """Resume/retry a quiz session."""
        self._check_orchestrator()
        
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status["status"] == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Resuming quiz session: {session_id}"
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def delete_session(self, session_id: str) -> Dict[str, str]:
        """Delete a quiz session."""
        self._check_orchestrator()
        
        try:
            self.orchestrator.session_manager.delete_session(session_id)
            return {"message": "Session deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # =========================================================================
    # Topic Generation
    # =========================================================================
    
    def generate_topic(
        self,
        payload: TopicGenerationRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """
        Generate quiz for a single topic.
        
        Args:
            payload: Topic generation request
            background_tasks: FastAPI background tasks
            
        Returns:
            Session response
        """
        self._check_orchestrator()
        
        try:
            description = f"Quiz for {payload.topic}. Difficulty: {payload.difficulty.value}."
            
            session_id = self.orchestrator.session_manager.create_session(
                topic=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                question_count=payload.question_count,
                target_audience=payload.target_audience,
                difficulty=payload.difficulty.value
            )
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating quiz for topic: {payload.topic}"
            )
        except Exception as e:
            logger.error(f"Error generating quiz topic: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # =========================================================================
    # Output & Upload
    # =========================================================================
    
    def get_session_output(self, session_id: str) -> Dict[str, Any]:
        """Get final output for a completed quiz session."""
        self._check_orchestrator()
        
        import os
        import json
        
        try:
            status = self.orchestrator.get_session_status(session_id)
            output_file = status.get("output_file")
            
            if not output_file or not os.path.exists(output_file):
                raise HTTPException(status_code=404, detail="Output file not found")
            
            with open(output_file, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
            
            return {
                "status": "success",
                "session_id": session_id,
                "quiz_data": quiz_data
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def validate_quiz(self, payload: ValidateQuizRequest) -> SimpleStatus:
        """Validate quiz structure and content against DB schema."""
        try:
            quiz_data = payload.quiz
            errors = []
            
            # Required fields matching Quiz.ts schema
            required_fields = ["categoryName", "categoryDescription", "categoryIcon", "questions"]
            for field in required_fields:
                if field not in quiz_data:
                    errors.append(f"Missing required field: {field}")
            
            # Validate questions
            questions = quiz_data.get("questions", [])
            if not questions:
                errors.append("Quiz must have at least one question")
            else:
                for i, question in enumerate(questions):
                    q_errors = self._validate_question(question, i)
                    errors.extend(q_errors)
            
            if errors:
                return SimpleStatus(ok=False, message=f"Validation failed: {'; '.join(errors[:5])}")
            
            return SimpleStatus(ok=True, message="Validation successful")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
    
    def _validate_question(self, question: Dict[str, Any], index: int) -> List[str]:
        """Validate a single quiz question against QuizQuestionModel schema."""
        errors = []
        prefix = f"Question {index + 1}"
        
        # Required fields matching QuizQuestionModel in Quiz.ts
        required = ["question", "options", "correctAnswer", "explanation", "detailedExplanation", "difficulty"]
        for field in required:
            if field not in question:
                errors.append(f"{prefix}: Missing field '{field}'")
        
        # Validate options (min 2 required per schema)
        options = question.get("options", [])
        if len(options) < 2:
            errors.append(f"{prefix}: At least 2 options required (found {len(options)})")
        
        # Validate correct answer
        correct_answer = question.get("correctAnswer")
        if correct_answer is not None:
            if not isinstance(correct_answer, int):
                errors.append(f"{prefix}: correctAnswer must be an integer")
            elif correct_answer < 0 or correct_answer >= len(options):
                errors.append(f"{prefix}: correctAnswer index out of range")
        
        # Validate difficulty
        difficulty = question.get("difficulty", "").lower()
        if difficulty not in ["easy", "medium", "hard"]:
            errors.append(f"{prefix}: Invalid difficulty '{difficulty}' (must be easy/medium/hard)")
        
        return errors
    
    def upload_quiz(self, payload: UploadQuizRequest) -> SimpleStatus:
        """Upload quiz to database via API."""
        import requests
        
        try:
            # Convert Pydantic model to dict for validation
            quiz_dict = payload.quiz.model_dump() if hasattr(payload.quiz, 'model_dump') else payload.quiz
            
            # Validate first
            validation = self.validate_quiz(ValidateQuizRequest(quiz=quiz_dict))
            if not validation.ok:
                return SimpleStatus(ok=False, message=f"Validation failed: {validation.message}")
            
            # Get API URL from config or payload
            from src.core.config import config
            api_url = (payload.api_url or config.api_base_url).rstrip('/')
            
            # Prepare request
            url = f"{api_url}/api/v1/quiz"
            headers = {
                'x-admin-secret': payload.admin_secret or 'TBEAdmin',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=quiz_dict, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return SimpleStatus(ok=True, message="Quiz uploaded successfully")
            else:
                return SimpleStatus(ok=False, message=f"Upload failed: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            return SimpleStatus(ok=False, message="Upload timeout - API server may be slow")
        except requests.exceptions.ConnectionError:
            return SimpleStatus(ok=False, message="Connection error - check if API server is running")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")