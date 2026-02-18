import logging
from typing import Dict, Any, Optional

from src.agents.quiz.workflow.state import QuizWorkflowState
from src.agents.quiz.workflow.graph import create_workflow_graph
from src.agents.quiz.session.session_manager import QuizSessionManager
from src.agents.quiz.workflow.state_utils import (
    create_initial_state,
    state_from_session,
    determine_resume_status
)
from src.core.session import SessionStatus

logger = logging.getLogger(__name__)

class QuizWorkflowOrchestrator:
    """Orchestrator for quiz generation workflow."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.graph = create_workflow_graph()
        self.session_manager = QuizSessionManager()

    def start_generation(self, topic: str, description: str, agent_type: str, question_count: int = 20, target_audience: str = "developers", difficulty: str = "medium") -> str:
        """Start a new quiz generation workflow."""
        session_id = self.session_manager.create_session(
            topic=topic,
            description=description,
            agent_type=agent_type,
            question_count=question_count,
            target_audience=target_audience,
            difficulty=difficulty
        )
        logger.info(f"Started quiz generation workflow for session {session_id}")

        return session_id

    def execute_workflow(self, session_id: str) -> Dict[str, Any]:
        """Execute the workflow for a session."""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        # Build initial state from session
        initial_state: QuizWorkflowState = state_from_session(session_data)
        
        # Determine where to resume
        if initial_state["status"] == "completed":
            logger.info(f"Session {session_id} already completed")
            return {
                "status": "completed",
                "session_id": session_id,
                "output_file": initial_state["output_file"]
            }

        # Set initial status based on what's already done
        initial_state["status"] = determine_resume_status(initial_state)

        try:
            # Execute workflow - invoke runs the entire graph
            final_state = self.graph.invoke(initial_state)
            
            # Update session with final state
            if final_state:
                self._update_session_from_state(session_id, final_state)
                
                return {
                    "status": final_state.get("status", "completed"),
                    "session_id": session_id,
                    "output_file": final_state.get("output_file"),
                    "quiz_data": final_state.get("quiz_data")
                }
            
            return {
                "status": "completed",
                "session_id": session_id
            }
        except Exception as e:
            logger.error(f"Error executing workflow for session {session_id}: {e}")
            self.session_manager.update_status(
                session_id,
                SessionStatus.FAILED,
                current_step=f"Workflow failed: {str(e)}",
                error=str(e)
            )
            raise

    def _update_session_from_state(self, session_id: str, state_update: Dict[str, Any]) -> None:
        """Update session from workflow state update."""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            return

        # Update fields from state
        if "category_metadata" in state_update:
            session_data["category_metadata"] = state_update["category_metadata"]
        
        if "questions" in state_update:
            session_data["questions"] = state_update["questions"]
        
        if "status" in state_update:
            session_data["status"] = state_update["status"]
        
        if "progress" in state_update:
            session_data["progress"].update(state_update["progress"])
        
        if "output_file" in state_update:
            session_data["output_file"] = state_update["output_file"]
        
        self.session_manager.save_session(session_id, session_data)

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current session status with auto-fix for missing question_count."""
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")

        return {
            "session_id": session_id,
            "topic": session_data.get("topic"),
            "status": session_data.get("status", "unknown"),
            "progress": session_data.get("progress", {}),
            "output_file": session_data.get("output_file"),
            "created_at": session_data.get("created_at"),
            "updated_at": session_data.get("updated_at"),
            "question_count": session_data.get("question_count", 20),
            "questions": session_data.get("questions", []),
            "agent_type": session_data.get("agent_type"),
            "target_audience": session_data.get("target_audience"),
            "difficulty": session_data.get("difficulty")
        }