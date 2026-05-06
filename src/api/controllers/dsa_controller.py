"""Controller for dedicated DSA question/study-guide generation."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, HTTPException

from src.agents.dsa.workflow import DSAWorkflowOrchestrator
from src.api.models.dsa_models import DSASessionResponse, DSATopicGenerationRequest
from src.core.config import config
from src.core.pipeline import PushToDB
from src.core.session import SessionStatus

logger = logging.getLogger(__name__)


class DSAController:
    """Business logic for DSA generation endpoints."""

    def __init__(self):
        self.orchestrator = DSAWorkflowOrchestrator()

    def _execute_workflow_background(self, session_id: str) -> None:
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as exc:
            logger.error("Error executing DSA workflow for session %s: %s", session_id, exc)

    def generate_topic(
        self,
        payload: DSATopicGenerationRequest,
        background_tasks: BackgroundTasks,
    ) -> DSASessionResponse:
        """Generate DSA package from topic-only input."""
        try:
            session_id = self.orchestrator.start_generation(
                topic=payload.topic,
                question_count=payload.question_count,
                include_real_world=payload.include_real_world,
                difficulty=payload.difficulty,
            )
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return DSASessionResponse(
                sessionId=session_id,
                message=(
                    f"Started DSA generation for topic: {payload.topic} "
                    f"(real-world: {payload.include_real_world})"
                ),
            )
        except Exception as exc:
            logger.error("Error creating DSA topic session: %s", exc)
            raise HTTPException(status_code=400, detail=str(exc))

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List DSA sessions with admin-friendly keys."""
        sessions = self.orchestrator.session_manager.list_sessions(status)
        formatted = []
        for session in sessions:
            formatted.append(
                {
                    "sessionId": session.get("session_id"),
                    "topic": session.get("topic"),
                    "questionCount": session.get("question_count", 20),
                    "includeRealWorld": session.get("include_real_world", True),
                    "difficulty": session.get("difficulty", "MEDIUM"),
                    "status": session.get("status"),
                    "progress": session.get("progress", {}),
                    "startedAt": session.get("created_at"),
                    "completedAt": session.get("updated_at")
                    if session.get("status") == "completed"
                    else None,
                    "outputFile": session.get("output_file"),
                    "error": session.get("error"),
                }
            )
        return formatted

    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status for one DSA session."""
        try:
            status = self.orchestrator.get_session_status(session_id)
            status["questionCount"] = status.get("question_count", 20)
            status["includeRealWorld"] = status.get("include_real_world", True)
            return status
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def get_session_output(self, session_id: str) -> Dict[str, Any]:
        """Get final output payload for completed DSA session."""
        status = self.get_session_progress(session_id)
        output_file = status.get("output_file")

        if output_file and os.path.exists(output_file):
            with open(output_file, encoding="utf-8") as file_obj:
                return {
                    "status": "success",
                    "session_id": session_id,
                    "output": json.load(file_obj),
                }

        # Fallback: return in-memory/session payload when file is missing.
        dsa_data = status.get("dsa_data")
        if dsa_data:
            return {"status": "success", "session_id": session_id, "output": dsa_data}

        raise HTTPException(status_code=404, detail="Output file not found")

    def cancel_session(self, session_id: str) -> Dict[str, str]:
        """Cancel an active DSA generation session."""
        try:
            session = self.orchestrator.get_session_status(session_id)
            if session.get("status") in {"pending", "in_progress", "questions_generating", "study_guide_generating"}:
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
        self,
        session_id: str,
        background_tasks: BackgroundTasks,
    ) -> DSASessionResponse:
        """Resume or retry an existing DSA session."""
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status.get("status") == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return DSASessionResponse(
                sessionId=session_id,
                message=f"Resuming DSA session: {session_id}",
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: str) -> Dict[str, str]:
        """Delete a DSA session."""
        try:
            self.orchestrator.session_manager.delete_session(session_id)
            return {"message": "Session deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")

    def push_session_to_db(
        self,
        session_id: str,
        *,
        environment: Optional[str] = None,
        push_questions: bool = True,
        push_study_guide: bool = True,
    ) -> Dict[str, Any]:
        """Push generated DSA session output to TBE-Web API endpoints."""
        if not push_questions and not push_study_guide:
            return {
                "ok": False,
                "message": "Nothing to push. Enable push_questions and/or push_study_guide.",
                "data": {},
            }

        session_data = self.orchestrator.session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        output_payload = session_data.get("dsa_data")
        if not output_payload:
            output_payload = self.get_session_output(session_id).get("output")

        if not output_payload:
            return {
                "ok": False,
                "message": "No generated output found for session.",
                "data": {},
            }

        base_v1_url = f"{config.get_api_base_url(environment).rstrip('/')}/api/v1"
        pusher = PushToDB(base_url=base_v1_url)

        questions = output_payload.get("questions", [])
        study_guide = output_payload.get("studyGuide")

        question_push_results = []
        question_failures = []

        if push_questions:
            for index, question in enumerate(questions):
                try:
                    push_result = pusher.push(
                        "/interview-prep/dsa-sheet/",
                        question,
                    )
                    question_push_results.append(
                        {
                            "index": index,
                            "title": question.get("title", ""),
                            "status_code": push_result.get("status_code"),
                        }
                    )
                except Exception as exc:
                    question_failures.append(
                        {
                            "index": index,
                            "title": question.get("title", ""),
                            "error": str(exc),
                        }
                    )

        study_guide_result = None
        study_guide_error = None
        if push_study_guide and study_guide:
            # TBE-Web currently exposes read-only study guide route for DSA.
            study_guide_error = (
                "Skipped: no dedicated study-guide write endpoint is available in TBE-Web yet."
            )

        ok = len(question_failures) == 0

        return {
            "ok": ok,
            "message": (
                "DSA session pushed successfully"
                if ok
                else "DSA session push completed with partial failures"
            ),
            "data": {
                "sessionId": session_id,
                "environment": environment or config.environment,
                "questionsAttempted": len(questions) if push_questions else 0,
                "questionsPushed": len(question_push_results),
                "questionsFailed": len(question_failures),
                "questionFailures": question_failures,
                "studyGuidePushed": bool(study_guide_result),
                "studyGuideError": study_guide_error,
            },
        }
