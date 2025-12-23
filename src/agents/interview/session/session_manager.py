"""Session manager for interview sheet generation extending base session manager."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import os
import json

from src.core.session.base_session_manager import BaseSessionManager
from src.core.session.session_types import SessionStatus, ProgressInfo


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
    
    def set_output_file(self, session_id: str, output_file: str, sheet_data: Optional[Dict[str, Any]] = None) -> None:
        """Set output file path for a completed session.
        
        Args:
            session_id: Session ID
            output_file: Path to the output file
            sheet_data: Optional final sheet data to store
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        session_data["output_file"] = output_file
        if sheet_data:
            session_data["sheet_data"] = sheet_data
        
        self.save_session(session_id, session_data)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data with auto-fix for missing question_count.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data dictionary with question_count auto-fixed, or None if not found
        """
        session_data = super().get_session(session_id)
        
        if session_data:
            # Auto-fix: Ensure question_count is set using helper method
            old_count = session_data.get("question_count")
            new_count = self._fix_question_count(session_data)
            if old_count != new_count:
                # Save the fixed session immediately
                try:
                    self.save_session(session_id, session_data)
                except Exception as e:
                    # Log error but don't fail - at least return fixed data
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to save auto-fixed question_count for session {session_id}: {e}")
        
        return session_data
    
    def _fix_question_count(self, session_data: Dict[str, Any]) -> int:
        """Helper method to fix question_count in session data.
        
        Args:
            session_data: Session data dictionary
            
        Returns:
            Fixed question_count value
        """
        question_count_value = session_data.get("question_count")
        if question_count_value is None or question_count_value == 0:
            questions = session_data.get("questions", [])
            progress = session_data.get("progress", {})
            question_count = progress.get("total") or len(questions) or 20
            session_data["question_count"] = question_count
            return question_count
        return question_count_value
    
    def fix_all_sessions_question_count(self) -> int:
        """Fix question_count for all existing sessions (migration helper).
        
        Returns:
            Number of sessions fixed
        """
        import logging
        logger = logging.getLogger(__name__)
        
        fixed_count = 0
        if not os.path.exists(self.sessions_dir):
            logger.debug(f"Sessions directory does not exist: {self.sessions_dir}")
            return 0
        
        try:
            for filename in os.listdir(self.sessions_dir):
                if filename.endswith('.json'):
                    session_id = filename.replace('.json', '')
                    try:
                        session_data = super().get_session(session_id)
                        if session_data:
                            old_count = session_data.get("question_count")
                            new_count = self._fix_question_count(session_data)
                            if old_count != new_count or old_count is None:
                                self.save_session(session_id, session_data)
                                fixed_count += 1
                                logger.debug(f"Fixed session {session_id}: question_count={new_count}")
                    except Exception as e:
                        logger.warning(f"Failed to fix session {session_id}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error in fix_all_sessions_question_count: {e}", exc_info=True)
        
        return fixed_count
    
    def list_sessions(self, status: Optional[Any] = None) -> List[Dict[str, Any]]:
        """List all sessions with auto-fix for missing question_count.
        
        Args:
            status: Optional status filter (SessionStatus enum or string)
            
        Returns:
            List of session data dictionaries with question_count fixed
        """
        # Convert string status to SessionStatus enum if needed
        if isinstance(status, str):
            try:
                status = SessionStatus(status)
            except ValueError:
                status = None
        
        sessions = super().list_sessions(status)
        
        # Auto-fix: Ensure question_count is set for all sessions
        for session in sessions:
            old_count = session.get("question_count")
            # Fix question_count - this modifies session dict in place
            new_count = self._fix_question_count(session)
            # Always save if count changed or was missing/None
            if old_count != new_count or old_count is None:
                # Save the fixed session immediately
                try:
                    self.save_session(session["session_id"], session)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.debug(f"Auto-fixed and saved question_count for session {session['session_id']}: {old_count} -> {new_count}")
                except Exception as e:
                    # Log error but don't fail - at least return fixed data
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to save auto-fixed question_count for session {session['session_id']}: {e}")
        
        return sessions