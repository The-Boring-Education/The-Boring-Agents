from typing import Dict, Any, Optional
from datetime import datetime, timezone

from src.core.session.base_session_manager import BaseSessionManager
from src.core.session.session_types import SessionStatus, ProgressInfo

class QuizSessionManager(BaseSessionManager):
    """Manages quiz generation sessions extending base session manager."""
    
    def __init__(self, sessions_dir: Optional[str] = None):
        """Initialize quiz session manager."""
        super().__init__(workflow_type="quiz", sessions_dir=sessions_dir)
    
    def _create_session_data(
        self,
        session_id: str,
        topic: str,
        description: str,
        agent_type: str,
        question_count: int = 20,
        target_audience: str = "developers",
        difficulty: str = "medium",
        **kwargs
    ) -> Dict[str, Any]:
        """Create initial quiz session data."""
        return {
            "session_id": session_id,
            "workflow_type": "quiz",
            "topic": topic,
            "description": description,
            "agent_type": agent_type,
            "question_count": question_count,
            "target_audience": target_audience,
            "difficulty": difficulty,
            "status": SessionStatus.PENDING.value,
            "questions": [],
            "category_metadata": None,
            "progress": ProgressInfo(
                current_step="Initializing...",
                completed=0,
                total=question_count
            ).to_dict(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "output_file": None,
            "quiz_data": None,
            **kwargs
        }
    
    def set_category_metadata(self, session_id: str, metadata: Dict[str, Any]) -> None:
        """Set category metadata for a session."""
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        session_data["category_metadata"] = metadata
        self.save_session(session_id, session_data)
    
    def add_question(self, session_id: str, question: Dict[str, Any]) -> None:
        """Add a question to a session."""
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        if "questions" not in session_data:
            session_data["questions"] = []
        
        session_data["questions"].append(question)
        self.save_session(session_id, session_data)
    
    def set_output_file(self, session_id: str, output_file: str, quiz_data: Optional[Dict[str, Any]] = None) -> None:
        """Set output file path for a completed session."""
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        session_data["output_file"] = output_file
        if quiz_data:
            session_data["quiz_data"] = quiz_data
        
        self.save_session(session_id, session_data)