from typing import Dict, Any, Callable, Optional
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
                logger.error(f"Error in {node_name} node: {e}", exc_info=True)
                return {
                    "status": error_status,
                    "error": str(e),
                    "current_step": f"Failed: {str(e)}"
                }
        return wrapper
    return decorator

def check_skip_condition(state: Dict[str, Any], field: str, check_func: Optional[Callable] = None) -> bool:
    """Check if a node should be skipped based on state."""
    if field not in state:
        return False

    value = state[field]

    if check_func:
        return check_func(value)
    
    return bool(value)
    
def log_node_execution(node_name: str, session_id: str, message: Optional[str] = None):
    """Log node execution."""
    logger.info(f"[{session_id}] {node_name}: {message or 'Executing...'}")

def get_progress_update(completed: int, total: int, current_step: str) -> Dict[str, Any]:
    """Get progress update."""
    return {
        "current_step": current_step,
        "completed": completed,
        "total": total
    }
    