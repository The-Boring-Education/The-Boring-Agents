"""Workflow orchestrator for interview sheet generation."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.agents.interview.workflow.state import InterviewWorkflowState
from src.agents.interview.workflow.graph import create_workflow_graph
from src.agents.interview.session.session_manager import InterviewSessionManager
from src.agents.interview.types import AnswerAgentType
from src.core.session.session_types import SessionStatus
from src.agents.interview.common.state_utils import (
    create_initial_state,
    state_from_session,
    determine_resume_status
)

logger = logging.getLogger(__name__)


class InterviewWorkflowOrchestrator:
    """Orchestrator for interview sheet generation workflow."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.graph = create_workflow_graph()
        self.session_manager = InterviewSessionManager()
    
    def start_generation(
        self,
        name: str,
        description: str,
        agent_type: str,
        roadmap: str = "Tech",
        technology: Optional[str] = None
    ) -> str:
        """Start a new sheet generation workflow.
        
        Args:
            name: Sheet name
            description: Sheet description
            agent_type: Agent type (generic, dsa, tech, system_design)
            roadmap: Roadmap type (Frontend, Backend, Fullstack, Tech)
            technology: Optional technology name for tech agent
            
        Returns:
            Session ID
        """
        # Validate agent type
        try:
            AnswerAgentType(agent_type.lower())
        except ValueError:
            raise ValueError(f"Invalid agent type: {agent_type}")
        
        # Create session
        session_id = self.session_manager.create_session(
            name=name,
            description=description,
            agent_type=agent_type.lower(),
            roadmap=roadmap
        )
        
        # Initialize workflow state using utility
        initial_state: InterviewWorkflowState = create_initial_state(
            session_id=session_id,
            name=name,
            description=description,
            agent_type=agent_type.lower(),
            roadmap=roadmap
        )
        
        # Store technology in session if provided
        if technology:
            session_data = self.session_manager.get_session(session_id)
            if session_data:
                session_data["technology"] = technology
                self.session_manager.save_session(session_id, session_data)
        
        logger.info(f"Started generation workflow for session {session_id}")
        
        return session_id
    
    def execute_workflow(self, session_id: str) -> Dict[str, Any]:
        """Execute the workflow for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Final state dictionary
        """
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        # Build initial state from session using utility
        initial_state: InterviewWorkflowState = state_from_session(session_data)
        
        # Determine where to resume
        if initial_state["status"] == "completed":
            logger.info(f"Session {session_id} already completed")
            return {
                "status": "completed",
                "session_id": session_id,
                "output_file": initial_state["output_file"]
            }
        
        # Set initial status based on what's already done using utility
        initial_state["status"] = determine_resume_status(initial_state)
        
        try:
            # Execute workflow - invoke runs the entire graph
            # Nodes are idempotent, so they'll skip if work is already done
            final_state = self.graph.invoke(initial_state)
            
            # Update session with final state
            if final_state:
                self._update_session_from_state(session_id, final_state)
                
                return {
                    "status": final_state.get("status", "completed"),
                    "session_id": session_id,
                    "output_file": final_state.get("output_file"),
                    "sheet_data": final_state.get("sheet_data")
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
        """Update session from workflow state update.
        
        Args:
            session_id: Session ID
            state_update: State update from workflow node
        """
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            return
        
        # Update fields from state
        if "meta" in state_update:
            session_data["meta"] = state_update["meta"]
        
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
        """Get current session status.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session status dictionary
        """
        session_data = self.session_manager.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "name": session_data.get("name"),
            "status": session_data.get("status", "unknown"),
            "progress": session_data.get("progress", {}),
            "output_file": session_data.get("output_file"),
            "created_at": session_data.get("created_at"),
            "updated_at": session_data.get("updated_at")
        }
    
    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a session from where it left off.
        
        Args:
            session_id: Session ID
            
        Returns:
            Final state dictionary
        """
        return self.execute_workflow(session_id)

