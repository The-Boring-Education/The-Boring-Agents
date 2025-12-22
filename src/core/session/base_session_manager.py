"""Base session manager for all agent workflows.

This provides a common interface for session management that can be extended
by specific workflows (Interview, Quiz, Shiksha, etc.).
"""

import json
import os
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from src.core.config import config
from src.core.session.session_types import SessionStatus, ProgressInfo, BaseSessionData


class BaseSessionManager(ABC):
    """Base class for session management across all agent workflows.
    
    Provides common functionality for:
    - Creating and managing sessions
    - Tracking progress
    - Persisting state
    - Listing and querying sessions
    
    Subclasses should implement workflow-specific logic.
    """
    
    def __init__(self, workflow_type: str, sessions_dir: Optional[str] = None):
        """Initialize the session manager.
        
        Args:
            workflow_type: Type of workflow (e.g., "interview", "quiz", "shiksha")
            sessions_dir: Directory for storing session files (defaults to temp/{workflow_type}_sessions)
        """
        self.workflow_type = workflow_type
        self.sessions_dir = sessions_dir or os.path.join(
            config.temp_dir, 
            f"{workflow_type}_sessions"
        )
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def _get_session_file(self, session_id: str) -> str:
        """Get the file path for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            File path
        """
        return os.path.join(self.sessions_dir, f"{session_id}.json")
    
    def create_session(self, **kwargs) -> str:
        """Create a new session.
        
        Args:
            **kwargs: Workflow-specific session data
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session_data = self._create_session_data(session_id, **kwargs)
        self.save_session(session_id, session_data)
        return session_id
    
    @abstractmethod
    def _create_session_data(self, session_id: str, **kwargs) -> Dict[str, Any]:
        """Create initial session data structure.
        
        Subclasses should implement this to create workflow-specific session data.
        
        Args:
            session_id: Session ID
            **kwargs: Workflow-specific parameters
            
        Returns:
            Session data dictionary
        """
        pass
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        session_file = self._get_session_file(session_id)
        if not os.path.exists(session_file):
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Save session data.
        
        Args:
            session_id: Session ID
            session_data: Session data to save
        """
        session_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        session_file = self._get_session_file(session_id)
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving session {session_id}: {e}")
            raise
    
    def update_status(
        self,
        session_id: str,
        status: SessionStatus,
        current_step: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """Update session status.
        
        Args:
            session_id: Session ID
            status: New status
            current_step: Optional current step description
            error: Optional error message
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        session_data["status"] = status.value
        if current_step:
            if "progress" not in session_data:
                session_data["progress"] = {}
            session_data["progress"]["current_step"] = current_step
        if error:
            session_data["error"] = error
        
        self.save_session(session_id, session_data)
    
    def update_progress(
        self,
        session_id: str,
        completed: Optional[int] = None,
        total: Optional[int] = None,
        current_step: Optional[str] = None,
        **kwargs
    ) -> None:
        """Update session progress.
        
        Args:
            session_id: Session ID
            completed: Number of completed items
            total: Total number of items
            current_step: Current step description
            **kwargs: Additional progress fields
        """
        session_data = self.get_session(session_id)
        if not session_data:
            raise ValueError(f"Session {session_id} not found")
        
        if "progress" not in session_data:
            session_data["progress"] = {}
        
        if completed is not None:
            session_data["progress"]["completed"] = completed
        if total is not None:
            session_data["progress"]["total"] = total
        if current_step:
            session_data["progress"]["current_step"] = current_step
        
        # Calculate percent
        if "completed" in session_data["progress"] and "total" in session_data["progress"]:
            completed_val = session_data["progress"]["completed"]
            total_val = session_data["progress"]["total"]
            if total_val > 0:
                session_data["progress"]["percent"] = round((completed_val / total_val) * 100, 2)
        
        # Add any additional progress fields
        for key, value in kwargs.items():
            session_data["progress"][key] = value
        
        self.save_session(session_id, session_data)
    
    def list_sessions(self, status: Optional[SessionStatus] = None) -> List[Dict[str, Any]]:
        """List all sessions, optionally filtered by status.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of session data dictionaries
        """
        sessions = []
        
        if not os.path.exists(self.sessions_dir):
            return sessions
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                session_id = filename.replace('.json', '')
                session_data = self.get_session(session_id)
                
                if session_data:
                    # Filter by status if provided
                    if status is None or session_data.get("status") == status.value:
                        sessions.append(session_data)
        
        # Sort by updated_at (newest first)
        sessions.sort(
            key=lambda x: x.get("updated_at", x.get("created_at", "")),
            reverse=True
        )
        
        return sessions
    
    def delete_session(self, session_id: str) -> None:
        """Delete a session.
        
        Args:
            session_id: Session ID
        """
        session_file = self._get_session_file(session_id)
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except Exception as e:
                print(f"Error deleting session {session_id}: {e}")
                raise
    
    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get progress information for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            Progress dictionary or None if session not found
        """
        session_data = self.get_session(session_id)
        if not session_data:
            return None
        
        return {
            "session_id": session_id,
            "status": session_data.get("status"),
            "progress": session_data.get("progress", {}),
            "error": session_data.get("error"),
            "updated_at": session_data.get("updated_at")
        }

