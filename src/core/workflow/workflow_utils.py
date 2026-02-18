"""Generic workflow utility functions for LangGraph node execution.

These utilities are agent-agnostic and can be used by any workflow.
"""

from typing import Dict, Any, Callable, Optional, Tuple, List
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def handle_node_errors(node_name: str, error_status: str = "failed"):
    """Decorator to handle errors in workflow nodes."""
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
    """Check if a node should be skipped based on existing state data."""
    if field not in state:
        return False
    value = state[field]
    return check_func(value) if check_func else bool(value)


def log_node_execution(
    node_name: str,
    session_id: str,
    message: Optional[str] = None,
) -> None:
    if message:
        logger.info("[%s] Session %s: %s", node_name, session_id, message)
    else:
        logger.info("[%s] Session %s: Executing", node_name, session_id)


def get_progress_update(completed: int, total: int, current_step: str) -> Dict[str, Any]:
    return {"completed": completed, "total": total, "current_step": current_step}


def create_error_state(error_message: str, status: str = "failed") -> Dict[str, Any]:
    return {"status": status, "error": error_message, "current_step": f"Failed: {error_message}"}


def update_state_safely(state: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Return a new state dict with updates applied (does not mutate original)."""
    new_state = state.copy()
    new_state.update(updates)
    return new_state


def validate_state_fields(
    state: Dict[str, Any],
    required_fields: List[str],
) -> Tuple[bool, List[str]]:
    missing = [f for f in required_fields if f not in state or state[f] is None]
    return (len(missing) == 0, missing)
