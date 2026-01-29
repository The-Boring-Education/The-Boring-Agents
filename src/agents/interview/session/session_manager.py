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
    
    
    def add_question(self, session_id: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Add a question to a session.
        
        Args:
            session_id: Session ID
            question: Question data dictionary
            
        Returns:
            Added question with ID
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        # Ensure question has an ID
        if "id" not in question and "_id" not in question:
            # Generate a temporary ID if one doesn't exist
            # Use timestamp or index-based ID? 
            # Frontend uses question_INDEX if missing, but for new questions we should probably generate one.
            # But let's stick to simple ID generation for now.
            import uuid
            question["id"] = str(uuid.uuid4())
            question["created_at"] = datetime.now(timezone.utc).isoformat()
            question["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # 1. Add to 'questions' list
        if "questions" not in session_data:
            session_data["questions"] = []
        
        session_data["questions"].append(question)
        
        # 2. Add to 'sheet_data' if exists
        if "sheet_data" in session_data and session_data["sheet_data"]:
            if "questions" not in session_data["sheet_data"]:
                session_data["sheet_data"]["questions"] = []
            session_data["sheet_data"]["questions"].append(question)
            
            # Sync to output file
            output_file = session_data.get("output_file")
            if output_file and os.path.exists(output_file):
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(session_data["sheet_data"], f, indent=2, ensure_ascii=False)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to update output file {output_file}: {e}")

        # Update question count
        session_data["question_count"] = max(
            session_data.get("question_count", 0), 
            len(session_data["questions"])
        )
        
        self.save_session(session_id, session_data)
        return question

    def get_question(self, session_id: str, question_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific question from a session.
        
        Args:
            session_id: Session ID
            question_id: Question ID
            
        Returns:
            Question dictionary or None
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return None
            
        # Try finding in questions list
        questions = session_data.get("questions", [])
        for i, q in enumerate(questions):
            q_id = q.get("id") or q.get("_id")
            
            # Match by ID or Index
            is_match = False
            if str(q_id) == str(question_id):
                is_match = True
            elif question_id.startswith("question_"):
                try:
                    idx = int(question_id.split("_")[1])
                    if i == idx:
                        is_match = True
                except (ValueError, IndexError):
                    pass
            
            if is_match:
                return q
                
        return None

    def delete_question(self, session_id: str, question_id: str) -> bool:
        """Delete a question from a session.
        
        Args:
            session_id: Session ID
            question_id: Question ID
            
        Returns:
            True if deleted, False if not found
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
            
        deleted = False
        
        # 1. Delete from questions matching ID logic
        if "questions" in session_data:
            questions = session_data["questions"]
            target_idx = -1
            
            for i, q in enumerate(questions):
                q_id = q.get("id") or q.get("_id")
                
                is_match = False
                if str(q_id) == str(question_id):
                    is_match = True
                elif question_id.startswith("question_"):
                    try:
                        idx = int(question_id.split("_")[1])
                        if i == idx:
                            is_match = True
                    except (ValueError, IndexError):
                        pass
                
                if is_match:
                    target_idx = i
                    break
            
            if target_idx != -1:
                questions.pop(target_idx)
                session_data["questions"] = questions
                deleted = True
        
        # 2. Delete from sheet_data if exists
        if "sheet_data" in session_data and session_data["sheet_data"]:
            sheet_questions = session_data["sheet_data"].get("questions", [])
            target_idx = -1
            
            for i, q in enumerate(sheet_questions):
                q_id = q.get("id") or q.get("_id")
                
                is_match = False
                if str(q_id) == str(question_id):
                    is_match = True
                elif question_id.startswith("question_"):
                    try:
                        idx = int(question_id.split("_")[1])
                        if i == idx:
                            is_match = True
                    except (ValueError, IndexError):
                        pass
                
                if is_match:
                    target_idx = i
                    break
            
            if target_idx != -1:
                sheet_questions.pop(target_idx)
                session_data["sheet_data"]["questions"] = sheet_questions
                deleted = True
                
                # Sync to output file
                output_file = session_data.get("output_file")
                if output_file and os.path.exists(output_file):
                    try:
                        with open(output_file, 'w', encoding='utf-8') as f:
                            json.dump(session_data["sheet_data"], f, indent=2, ensure_ascii=False)
                    except Exception as e:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.error(f"Failed to update output file {output_file}: {e}")

        if deleted:
            # Update count
            session_data["question_count"] = len(session_data.get("questions", []))
            self.save_session(session_id, session_data)
            
        return deleted
    
    def update_questions(self, session_id: str, questions: list) -> None:
        """Update all questions for a session.
        
        Args:
            session_id: Session ID
            questions: List of question dictionaries
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
    
    def update_question_in_session(self, session_id: str, question_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a specific question in a session (including final sheet data).
        
        Args:
            session_id: Session ID
            question_id: Question ID to update
            updates: Dictionary of fields to update
            
        Returns:
            Updated question dictionary
            
        Raises:
            ValueError: If session or question not found
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
            
        updated_question = None
        question_found = False
        
        # 1. Update in 'questions' list (in-progress or completed)
        if "questions" in session_data:
            for i, q in enumerate(session_data["questions"]):
                # Check different ID fields (id, _id)
                q_id = q.get("id") or q.get("_id")
                
                # Match by explicit ID OR by index if ID is like "question_X"
                is_match = False
                if str(q_id) == str(question_id):
                    is_match = True
                elif question_id.startswith("question_"):
                    try:
                        idx = int(question_id.split("_")[1])
                        if i == idx:
                            is_match = True
                    except (ValueError, IndexError):
                        pass

                if is_match:
                    # Update fields
                    session_data["questions"][i].update(updates)
                    # Ensure updated_at is set
                    session_data["questions"][i]["updated_at"] = datetime.now(timezone.utc).isoformat()
                    updated_question = session_data["questions"][i]
                    question_found = True
                    break
                    
        # 2. Update in 'sheet_data' if it exists (completed session final output)
        if "sheet_data" in session_data and session_data["sheet_data"]:
            sheet_questions = session_data["sheet_data"].get("questions", [])
            for i, q in enumerate(sheet_questions):
                q_id = q.get("id") or q.get("_id")
                
                is_match = False
                if str(q_id) == str(question_id):
                    is_match = True
                elif question_id.startswith("question_"):
                    try:
                        idx = int(question_id.split("_")[1])
                        if i == idx:
                            is_match = True
                    except (ValueError, IndexError):
                        pass

                if is_match:
                    # Update fields
                    sheet_questions[i].update(updates)
                    sheet_questions[i]["updated_at"] = datetime.now(timezone.utc).isoformat()
                    # If we didn't find it in main list (unlikely), take from here
                    if not updated_question:
                        updated_question = sheet_questions[i]
                    question_found = True
                    break
            session_data["sheet_data"]["questions"] = sheet_questions
            
            # Sync to output file if it exists
            output_file = session_data.get("output_file")
            if output_file and os.path.exists(output_file) and session_data["sheet_data"]:
                try:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(session_data["sheet_data"], f, indent=2, ensure_ascii=False)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to update output file {output_file}: {e}")
            
        if not question_found:
            raise ValueError(f"Question {question_id} not found in session {session_id}")
            
        self.save_session(session_id, session_data)
        return updated_question


    
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