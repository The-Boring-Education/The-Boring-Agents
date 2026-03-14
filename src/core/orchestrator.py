"""Core workflow orchestration and node utilities.

Provides:
- BaseWorkflowOrchestrator: ABC that drives a LangGraph workflow with session persistence.
- Workflow helper functions: handle_node_errors, check_skip_condition, etc.
"""

import logging
from abc import ABC
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.core.session import BaseSessionManager, SessionStatus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Workflow node helpers (agent-agnostic)
# ---------------------------------------------------------------------------


def handle_node_errors(node_name: str, error_status: str = "failed"):
    """Decorator to catch exceptions in workflow nodes and return error state."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                return func(state)
            except Exception as e:
                logger.error("Error in %s node: %s", node_name, e, exc_info=True)
                return create_error_state(str(e), error_status)

        return wrapper

    return decorator


def check_skip_condition(
    state: Dict[str, Any],
    field: str,
    check_func: Optional[Callable] = None,
) -> bool:
    """Return True if the node should be skipped (field already populated)."""
    if field not in state:
        return False
    value = state[field]
    return check_func(value) if check_func else bool(value)


def log_node_execution(
    node_name: str, session_id: str, message: Optional[str] = None
) -> None:
    if message:
        logger.info("[%s] Session %s: %s", node_name, session_id, message)
    else:
        logger.info("[%s] Session %s: Executing", node_name, session_id)


def get_progress_update(
    completed: int, total: int, current_step: str
) -> Dict[str, Any]:
    return {"completed": completed, "total": total, "current_step": current_step}


def create_error_state(error_message: str, status: str = "failed") -> Dict[str, Any]:
    return {
        "status": status,
        "error": error_message,
        "current_step": f"Failed: {error_message}",
    }


def update_state_safely(
    state: Dict[str, Any], updates: Dict[str, Any]
) -> Dict[str, Any]:
    new_state = state.copy()
    new_state.update(updates)
    return new_state


def validate_state_fields(
    state: Dict[str, Any], required_fields: List[str]
) -> Tuple[bool, List[str]]:
    missing = [f for f in required_fields if f not in state or state[f] is None]
    return (len(missing) == 0, missing)


# ---------------------------------------------------------------------------
# Base orchestrator
# ---------------------------------------------------------------------------


class BaseWorkflowOrchestrator(ABC):
    """Drives a LangGraph workflow with session persistence.

    Subclasses provide: graph, session_manager, state conversion fns, sync_fields.
    """

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
        self._sync_fields = sync_fields or [
            "questions",
            "status",
            "progress",
            "output_file",
        ]

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
                    **{
                        k: final_state.get(k)
                        for k in self._sync_fields
                        if k not in ("status", "progress")
                    },
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

    def _update_session_from_state(
        self, session_id: str, state_update: Dict[str, Any]
    ) -> None:
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            return
        for field in self._sync_fields:
            if field in state_update:
                if field == "progress" and isinstance(
                    session_data.get("progress"), dict
                ):
                    session_data["progress"].update(state_update["progress"])
                else:
                    session_data[field] = state_update[field]
        self.session_manager.save_session(session_id, session_data)

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
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
