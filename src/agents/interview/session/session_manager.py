"""Session manager for interview sheet generation extending base session manager."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ....core.session.base_session_manager import BaseSessionManager
from ....core.session.session_types import SessionStatus, ProgressInfo


class InterviewSessionManager(BaseSessionManager):
    """Manages interview sheet generation sessions extending base session manager."""
    
    def __init__(self, sessions_dir: Optional[str] = None):
        """Initialize interview session manager.
        
        Args:
            sessions_dir: Directory for storing session files (defaults to temp/interview_sessions)
        """
        super().__init__(workflow_type="interview", sessions_dir=sessions_dir)
    
    def _create_session_data(
        self,
        session_id: str,
        name: str,
        description: str,
        agent_type: str,
        roadmap: str = "Tech",
        question_count: int = 20,
        **kwargs
    ) -> Dict[str, Any]:
        """Create initial interview session data.
        
        Args:
            session_id: Session ID
            name: Sheet name
            description: Sheet description
            agent_type: Agent type (generic, dsa, tech, system_design)
            roadmap: Roadmap type (Frontend, Backend, Fullstack, Tech)
            question_count: Number of questions to generate
            **kwargs: Additional parameters
            
        Returns:
            Session data dictionary
        """
        return {
            "session_id": session_id,
            "workflow_type": "interview",
            "name": name,
            "description": description,
            "agent_type": agent_type,
            "roadmap": roadmap,
            "question_count": question_count,
            "status": SessionStatus.PENDING.value,
            "meta": None,
            "questions": [],
            "question_texts": [],
            "progress": ProgressInfo(
                current_step="Initializing...",
                completed=0,
                total=question_count
            ).to_dict(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "output_file": None,
            "sheet_data": None,
            **kwargs
        }
    
    def create_session(
        self,
        name: str,
        description: str,
        agent_type: str,
        roadmap: str = "Tech",
        question_count: int = 20,
        **kwargs
    ) -> str:
        """Create a new interview session.
        
        Args:
            name: Sheet name
            description: Sheet description
            agent_type: Agent type (generic, dsa, tech, system_design)
            roadmap: Roadmap type (Frontend, Backend, Fullstack, Tech)
            question_count: Number of questions to generate
            **kwargs: Additional parameters
            
        Returns:
            Session ID
        """
        return super().create_session(
            name=name,
            description=description,
            agent_type=agent_type,
            roadmap=roadmap,
            question_count=question_count,
            **kwargs
        )
    
    def set_meta(self, session_id: str, meta: str) -> None:
        """Set metadata for a session.
        
        Args:
            session_id: Session ID
            meta: Metadata string
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        session_data["meta"] = meta
        self.save_session(session_id, session_data)
    
    def add_question(self, session_id: str, question: Dict[str, Any]) -> None:
        """Add a question to a session.
        
        Args:
            session_id: Session ID
            question: Question data dictionary
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        if "questions" not in session_data:
            session_data["questions"] = []
        
        session_data["questions"].append(question)
        self.save_session(session_id, session_data)
    
    def update_questions(self, session_id: str, questions: list) -> None:
        """Update all questions for a session.
        
        Args:
            session_id: Session ID
            questions: List of question dictionaries
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        session_data["questions"] = questions
        self.save_session(session_id, session_data)
