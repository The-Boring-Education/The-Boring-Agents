"""Interview workflow orchestrator -- thin subclass of BaseWorkflowOrchestrator."""

import logging
from typing import Dict, Any, Optional

from src.core.workflow.base_orchestrator import BaseWorkflowOrchestrator
from src.agents.interview.workflow.graph import create_workflow_graph
from src.agents.interview.session.session_manager import InterviewSessionManager
from src.agents.interview.types import AnswerAgentType
from src.agents.interview.workflow.state import (
    create_initial_state,
    state_from_session,
    determine_resume_status,
)

logger = logging.getLogger(__name__)

_SYNC_FIELDS = ["meta", "questions", "status", "progress", "output_file"]


class InterviewWorkflowOrchestrator(BaseWorkflowOrchestrator):
    """Orchestrator for interview sheet generation workflow."""

    def __init__(self):
        super().__init__(
            graph=create_workflow_graph(),
            session_manager=InterviewSessionManager(),
            state_from_session_fn=state_from_session,
            determine_resume_status_fn=determine_resume_status,
            sync_fields=_SYNC_FIELDS,
        )

    def start_generation(
        self,
        name: str,
        description: str,
        agent_type: str,
        roadmap: str = "Tech",
        technology: Optional[str] = None,
        question_count: int = 20,
    ) -> str:
        try:
            AnswerAgentType(agent_type.lower())
        except ValueError:
            raise ValueError(f"Invalid agent type: {agent_type}")

        session_id = self.session_manager.create_session(
            name=name,
            description=description,
            agent_type=agent_type.lower(),
            roadmap=roadmap,
            question_count=question_count,
        )

        if technology:
            session_data = self.session_manager.get_session(session_id)
            if session_data:
                session_data["technology"] = technology
                self.session_manager.save_session(session_id, session_data)

        logger.info("Started generation workflow for session %s", session_id)
        return session_id

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Extend base with interview-specific fields."""
        base = super().get_session_status(session_id)
        session_data = self.session_manager.get_session(session_id)
        if session_data:
            base.update({
                "name": session_data.get("name"),
                "roadmap": session_data.get("roadmap"),
                "description": session_data.get("description"),
            })
        return base
