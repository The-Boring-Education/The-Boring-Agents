"""Interview preparation controller."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, HTTPException

from src.agents.interview.workflow import InterviewWorkflowOrchestrator
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    RoadmapSuggestion,
    SessionResponse,
    SimpleStatus,
    TopicGenerationRequest,
    TopicTemplate,
    UploadSheetRequest,
    ValidateSheetRequest,
)
from src.core.constants import INTERVIEW_TEMPLATES, ROADMAP_SUGGESTIONS
from src.core.session import SessionStatus

logger = logging.getLogger(__name__)


class InterviewPrepController:
    """Controller for interview preparation operations."""

    def __init__(self):
        self.orchestrator = InterviewWorkflowOrchestrator()
        try:
            self.orchestrator.session_manager.fix_all_sessions_question_count()
        except Exception as e:
            logger.warning("Failed to auto-fix sessions on init: %s", e, exc_info=True)

    # -- sheet / topic generation ---------------------------------------------

    def create_sheet(
        self, payload: CreateSheetRequest, background_tasks: BackgroundTasks
    ) -> SessionResponse:
        try:
            session_id = self.orchestrator.start_generation(
                name=payload.name,
                description=payload.description,
                agent_type=payload.agent_type.value,
                roadmap=payload.roadmap,
                technology=payload.technology,
                question_count=payload.question_count,
            )
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating interview sheet: {payload.name}",
            )
        except Exception as e:
            logger.error("Error creating sheet: %s", e)
            raise HTTPException(status_code=400, detail=str(e))

    def generate_topic(
        self, payload: TopicGenerationRequest, background_tasks: BackgroundTasks
    ) -> SessionResponse:
        try:
            description = f"Interview questions for {payload.topic}. Difficulty: {payload.difficulty}. Roadmap: {payload.roadmap}."
            session_id = self.orchestrator.session_manager.create_session(
                name=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                roadmap=payload.roadmap,
                question_count=payload.question_count,
                technology=payload.technology,
                difficulty=payload.difficulty,
                generate_answers=payload.generate_answers,
            )
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating questions for topic: {payload.topic}",
            )
        except Exception as e:
            logger.error("Error generating topic: %s", e)
            raise HTTPException(status_code=400, detail=str(e))

    # -- session queries ------------------------------------------------------

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Session manager already auto-fixes question_count, so no fallback needed here."""
        sessions = self.orchestrator.session_manager.list_sessions(status)
        return [self._format_session(s) for s in sessions]

    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        try:
            result = self.orchestrator.get_session_status(session_id)
            qc = result.get("question_count", 20)
            result["questionCount"] = qc
            return result
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    # -- session actions ------------------------------------------------------

    def cancel_session(self, session_id: str) -> Dict[str, str]:
        try:
            session = self.orchestrator.get_session_status(session_id)
            if session["status"] in (
                "in_progress",
                "pending",
                "metadata_generating",
                "questions_generating",
                "answers_generating",
            ):
                self.orchestrator.session_manager.update_status(
                    session_id,
                    SessionStatus.FAILED,
                    current_step="Cancelled by user",
                    error="Cancelled by user",
                )
            return {"message": "Session cancelled"}
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def retry_session(
        self, session_id: str, background_tasks: BackgroundTasks
    ) -> SessionResponse:
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status["status"] == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return SessionResponse(
                sessionId=session_id, message=f"Resuming session: {session_id}"
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: str) -> Dict[str, str]:
        try:
            self.orchestrator.session_manager.delete_session(session_id)
            return {"message": "Session deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")

    # -- question CRUD --------------------------------------------------------

    def update_question(
        self, session_id: str, question_id: str, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            return self.orchestrator.session_manager.update_question_in_session(
                session_id, question_id, updates
            )
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error(
                "Error updating question %s in session %s: %s",
                question_id,
                session_id,
                e,
            )
            raise HTTPException(status_code=500, detail="Failed to update question")

    def update_session_sheet(
        self, session_id: str, sheet_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Update the entire sheet data for a session."""
        try:
            self.orchestrator.session_manager.update_sheet_data(session_id, sheet_data)
            return {"message": "Session sheet updated successfully"}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error("Error updating sheet data for session %s: %s", session_id, e)
            raise HTTPException(
                status_code=500, detail="Failed to update session sheet"
            )

    def get_question(self, session_id: str, question_id: str) -> Dict[str, Any]:
        try:
            question = self.orchestrator.session_manager.get_question(
                session_id, question_id
            )
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            return question
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Error getting question %s in session %s: %s",
                question_id,
                session_id,
                e,
            )
            raise HTTPException(status_code=500, detail="Failed to get question")

    def delete_question(self, session_id: str, question_id: str) -> Dict[str, Any]:
        try:
            if not self.orchestrator.session_manager.delete_question(
                session_id, question_id
            ):
                raise HTTPException(status_code=404, detail="Question not found")
            session = self.orchestrator.session_manager.get_session(session_id)
            return {
                "message": "Question deleted",
                "remaining_questions": len(session.get("questions", []))
                if session
                else 0,
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                "Error deleting question %s in session %s: %s",
                question_id,
                session_id,
                e,
            )
            raise HTTPException(status_code=500, detail="Failed to delete question")

    def add_question(self, session_id: str, question: Dict[str, Any]) -> Dict[str, Any]:
        try:
            added = self.orchestrator.session_manager.add_question(session_id, question)
            session = self.orchestrator.session_manager.get_session(session_id)
            return {
                "question": added,
                "total_questions": len(session.get("questions", [])) if session else 0,
            }
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error("Error adding question to session %s: %s", session_id, e)
            raise HTTPException(status_code=500, detail="Failed to add question")

    # -- validation & upload --------------------------------------------------

    def validate_sheet(self, payload: ValidateSheetRequest) -> SimpleStatus:
        """Validate an interview sheet structure."""
        try:
            sheet_data = payload.sheetData
            errors = []

            # Required core fields
            required_fields = ["name", "slug", "description", "questions"]
            for field in required_fields:
                if field not in sheet_data:
                    errors.append(f"Missing required field: {field}")

            # Validate questions
            questions = sheet_data.get("questions", [])
            if not questions:
                errors.append("Interview sheet must have at least one question")
            else:
                for i, q in enumerate(questions):
                    prefix = f"Question {i + 1}"
                    for q_field in ["title", "question", "answer", "frequency"]:
                        if q_field not in q:
                            errors.append(f"{prefix}: Missing field '{q_field}'")

            if errors:
                return SimpleStatus(
                    ok=False, message=f"Validation failed: {'; '.join(errors[:5])}"
                )

            return SimpleStatus(ok=True, message="Validation successful")
        except Exception as e:
            logger.error("Validation error: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def upload_sheet(self, payload: UploadSheetRequest) -> SimpleStatus:
        """Upload interview sheet to the database via API."""
        import requests

        from src.core.config import config

        try:
            sheet_dict = (
                payload.sheetData.model_dump()
                if hasattr(payload.sheetData, "model_dump")
                else payload.sheetData
            )

            validation = self.validate_sheet(ValidateSheetRequest(sheetData=sheet_dict))
            if not validation.ok:
                return validation

            api_url = self._resolve_upload_url(payload.environment)
            url = f"{api_url}/api/v1/interview-prep/upload"

            headers = {"x-admin-secret": config.admin_secret, "Content-Type": "application/json"}

            upload_body = {
                "sessionId": "direct-upload",
                "metadata": payload.metadata,
                "sheetData": sheet_dict,
            }

            response = requests.post(url, json=upload_body, headers=headers, timeout=30)

            if response.status_code in [200, 201]:
                return SimpleStatus(
                    ok=True, message="Interview sheet uploaded successfully"
                )
            else:
                return SimpleStatus(
                    ok=False,
                    message=f"Upload failed: HTTP {response.status_code} - {response.text}",
                )

        except requests.exceptions.Timeout:
            return SimpleStatus(
                ok=False, message="Upload timeout - API server may be slow"
            )
        except requests.exceptions.ConnectionError:
            return SimpleStatus(
                ok=False, message="Connection error - check if API server is running"
            )
        except Exception as e:
            logger.error("Upload handler error: %s", e)
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    @staticmethod
    def _resolve_upload_url(environment: Optional[str] = None) -> str:
        """Resolve the target API base URL from environment name or config default."""
        from src.core.config import config

        return config.get_api_base_url(environment).rstrip("/")

    # -- templates ------------------------------------------------------------

    def get_topic_templates(self) -> List[TopicTemplate]:
        return [TopicTemplate(**t) for t in INTERVIEW_TEMPLATES]

    def get_roadmap_suggestions(self) -> List[RoadmapSuggestion]:
        return [RoadmapSuggestion(**s) for s in ROADMAP_SUGGESTIONS]

    # -- private helpers ------------------------------------------------------

    def _execute_workflow_background(self, session_id: str):
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as e:
            logger.error("Background workflow error for session %s: %s", session_id, e)

    @staticmethod
    def _format_session(session: Dict[str, Any]) -> Dict[str, Any]:
        qc = int(session.get("question_count", 20))
        return {
            "sessionId": session["session_id"],
            "topic": session.get("name", "Unknown"),
            "agentType": session.get("agent_type", "generic"),
            "roadmap": session.get("roadmap", "Tech"),
            "questionCount": qc,
            "question_count": qc,
            "status": session["status"],
            "progress": session.get("progress", {}),
            "startedAt": session.get("created_at"),
            "completedAt": session.get("updated_at")
            if session["status"] == "completed"
            else None,
            "outputFile": session.get("output_file"),
            "sheetData": session.get("sheet_data"),
            "error": session.get("error"),
        }
