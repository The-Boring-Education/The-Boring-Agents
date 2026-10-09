"""Controller for Shiksha course bundle generation."""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import BackgroundTasks, HTTPException

from src.agents.shiksha.workflow import ShikshaWorkflowOrchestrator
from src.api.models.shiksha_models import (
    ShikshaSessionResponse,
    ShikshaTopicGenerationRequest,
)
from src.core.config import config
from src.core.pipeline import PushToDB
from src.core.session import SessionStatus

logger = logging.getLogger(__name__)


class ShikshaController:
    """Business logic for Shiksha generation endpoints."""

    def __init__(self):
        self.orchestrator = ShikshaWorkflowOrchestrator()

    def _execute_workflow_background(self, session_id: str) -> None:
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as exc:
            logger.error(
                "Error executing Shiksha workflow for session %s: %s",
                session_id,
                exc,
            )

    def generate_topic(
        self,
        payload: ShikshaTopicGenerationRequest,
        background_tasks: BackgroundTasks,
    ) -> ShikshaSessionResponse:
        """Generate a course bundle from topic-only input."""
        try:
            session_id = self.orchestrator.start_generation(
                topic=payload.topic,
                chapter_count=payload.chapter_count,
                difficulty=payload.difficulty,
            )
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return ShikshaSessionResponse(
                sessionId=session_id,
                message=f"Started Shiksha generation for topic: {payload.topic}",
            )
        except Exception as exc:
            logger.error("Error creating Shiksha topic session: %s", exc)
            raise HTTPException(status_code=400, detail=str(exc))

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List Shiksha sessions with admin-friendly keys."""
        sessions = self.orchestrator.session_manager.list_sessions(status)
        return [
            {
                "sessionId": s.get("session_id"),
                "topic": s.get("topic"),
                "chapterCount": s.get("chapter_count", 5),
                "difficulty": s.get("difficulty", "MEDIUM"),
                "status": s.get("status"),
                "progress": s.get("progress", {}),
                "startedAt": s.get("created_at"),
                "completedAt": s.get("updated_at")
                if s.get("status") == "completed"
                else None,
                "outputFile": s.get("output_file"),
                "error": s.get("error"),
            }
            for s in sessions
        ]

    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get detailed status for one Shiksha session."""
        try:
            status = self.orchestrator.get_session_status(session_id)
            status["chapterCount"] = status.get("chapter_count", 5)
            return status
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def get_session_output(self, session_id: str) -> Dict[str, Any]:
        """Get final Bundle payload for a completed Shiksha session."""
        status = self.get_session_progress(session_id)
        output_file = status.get("output_file")

        if output_file and os.path.exists(output_file):
            with open(output_file, encoding="utf-8") as file_obj:
                return {
                    "status": "success",
                    "session_id": session_id,
                    "output": json.load(file_obj),
                }

        # ponytail: fall back to in-memory bundle when file is missing
        bundle = status.get("bundle")
        if bundle:
            return {"status": "success", "session_id": session_id, "output": bundle}

        raise HTTPException(status_code=404, detail="Output file not found")

    def cancel_session(self, session_id: str) -> Dict[str, str]:
        """Cancel an active Shiksha generation session."""
        try:
            session = self.orchestrator.get_session_status(session_id)
            if session.get("status") in {
                "pending",
                "in_progress",
                "outline_generating",
                "chapters_generating",
            }:
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
    ) -> ShikshaSessionResponse:
        """Resume or retry an existing Shiksha session."""
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status.get("status") == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return ShikshaSessionResponse(
                sessionId=session_id,
                message=f"Resuming Shiksha session: {session_id}",
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: str) -> Dict[str, str]:
        """Delete a Shiksha session."""
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
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Push a generated Bundle to the TBE-Web import endpoint."""
        session_data = self.orchestrator.session_manager.get_session(session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        bundle = session_data.get("bundle")
        if not bundle:
            bundle = self.get_session_output(session_id).get("output")

        if not bundle:
            return {
                "ok": False,
                "message": "No generated output found for session.",
                "data": {},
            }

        base_v1_url = f"{config.get_api_base_url(environment).rstrip('/')}/api/v1"
        pusher = PushToDB(base_url=base_v1_url)

        try:
            result = pusher.push(
                "/shiksha/import",
                {"bundle": bundle, "dryRun": dry_run},
            )
        except Exception as exc:
            return {
                "ok": False,
                "message": f"Push failed: {exc}",
                "data": {"sessionId": session_id},
            }

        return {
            "ok": True,
            "message": "Shiksha bundle pushed (import as Draft)",
            "data": {
                "sessionId": session_id,
                "environment": environment or config.environment,
                "dryRun": dry_run,
                "statusCode": result.get("status_code"),
                "response": result.get("response"),
            },
        }
