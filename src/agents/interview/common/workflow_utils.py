"""Workflow utility functions for node execution."""

from typing import Dict, Any, Callable, Optional
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def handle_node_errors(node_name: str, error_status: str = "failed"):
    """Decorator to handle errors in workflow nodes.
    
    Args:
        node_name: Name of the node
        error_status: Status to set on error
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: Dict[str, Any]) -> Dict[str, Any]:
            try:
                return func(state)
            except Exception as e:
                logger.error(f"Error in {node_name} node: {e}", exc_info=True)
                return {
                    "status": error_status,
                    "error": str(e),
                    "current_step": f"Failed: {str(e)}"
                }
        return wrapper
    return decorator


def check_skip_condition(
    state: Dict[str, Any],
    field: str,
    check_func: Optional[Callable] = None
) -> bool:
    """Check if a node should be skipped based on state.
    
    Args:
        state: Workflow state
        field: Field to check
        check_func: Optional function to check field value
        
    Returns:
        True if should skip, False otherwise
    """
    if field not in state:
        return False
    
    value = state[field]
    
    if check_func:
        return check_func(value)
    
    # Default: skip if field has a truthy value
    return bool(value)


def log_node_execution(
    node_name: str,
    session_id: str,
    message: Optional[str] = None
) -> None:
    """Log node execution.
    
    Args:
        node_name: Name of the node
        session_id: Session ID
        message: Optional additional message
    """
    if message:
        logger.info(f"[{node_name}] Session {session_id}: {message}")
    else:
        logger.info(f"[{node_name}] Session {session_id}: Executing")


def get_progress_update(
    completed: int,
    total: int,
    current_step: str
) -> Dict[str, Any]:
    """Get progress update dictionary.
    
    Args:
        completed: Number of completed items
        total: Total number of items
        current_step: Current step description
        
    Returns:
        Progress dictionary
    """
    return {
        "completed": completed,
        "total": total,
        "current_step": current_step
    }


def create_error_state(
    error_message: str,
    status: str = "failed"
) -> Dict[str, Any]:
    """Create an error state dictionary.
    
    Args:
        error_message: Error message
        status: Status to set
        
    Returns:
        Error state dictionary
    """
    return {
        "status": status,
        "error": error_message,
        "current_step": f"Failed: {error_message}"
    }
