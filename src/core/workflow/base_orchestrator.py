"""Base workflow orchestrator shared across all agent workflows.

Subclasses only need to provide:
- A compiled LangGraph graph
- A session manager instance
- state_from_session() / determine_resume_status() callables
- A list of state fields to sync back to the session
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Optional

from src.core.session.base_session_manager import BaseSessionManager
from src.core.session.session_types import SessionStatus

logger = logging.getLogger(__name__)


class BaseWorkflowOrchestrator(ABC):
    """Generic orchestrator that drives a LangGraph workflow with session persistence."""

    def __init__(
        self,
        graph,
        session_manager: BaseSessionManager,
        state_from_session_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        determine_resume_status_fn: Callable[[Dict[str, Any]], str],
        sync_fields: Optional[List[str]] = None,
    ):
        self.graph = graph
        self.session_manager = session_manager
        self._state_from_session = state_from_session_fn
        self._determine_resume_status = determine_resume_status_fn
        self._sync_fields = sync_fields or ["questions", "status", "progress", "output_file"]

    def execute_workflow(self, session_id: str) -> Dict[str, Any]:
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")

        initial_state = self._state_from_session(session_data)

        if initial_state.get("status") == "completed":
            logger.info("Session %s already completed", session_id)
            return {
                "status": "completed",
                "session_id": session_id,
                "output_file": initial_state.get("output_file"),
            }

        initial_state["status"] = self._determine_resume_status(initial_state)

        try:
            final_state = self.graph.invoke(initial_state)
            if final_state:
                self._update_session_from_state(session_id, final_state)
                return {
                    "status": final_state.get("status", "completed"),
                    "session_id": session_id,
                    **{k: final_state.get(k) for k in self._sync_fields if k not in ("status", "progress")},
                }
            return {"status": "completed", "session_id": session_id}
        except Exception as e:
            logger.error("Error executing workflow for session %s: %s", session_id, e)
            self.session_manager.update_status(
                session_id,
                SessionStatus.FAILED,
                current_step=f"Workflow failed: {e}",
                error=str(e),
            )
            raise

    def _update_session_from_state(self, session_id: str, state_update: Dict[str, Any]) -> None:
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            return

        for field in self._sync_fields:
            if field in state_update:
                if field == "progress" and isinstance(session_data.get("progress"), dict):
                    session_data["progress"].update(state_update["progress"])
                else:
                    session_data[field] = state_update[field]

        self.session_manager.save_session(session_id, session_data)

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Return a status dict. Subclasses can extend to add extra fields."""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session_id,
            "status": session_data.get("status", "unknown"),
            "progress": session_data.get("progress", {}),
            "output_file": session_data.get("output_file"),
            "created_at": session_data.get("created_at"),
            "updated_at": session_data.get("updated_at"),
            "question_count": session_data.get("question_count", 20),
            "questions": session_data.get("questions", []),
            "agent_type": session_data.get("agent_type"),
        }

    def resume_session(self, session_id: str) -> Dict[str, Any]:
        return self.execute_workflow(session_id)
