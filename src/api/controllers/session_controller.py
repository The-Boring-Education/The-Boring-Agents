"""
Session management controller.

Handles all business logic for session operations.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, Query

from src.agents.quiz.quiz_orchestrator import QuizOrchestrator
from src.agents.interview.session.session_manager import InterviewSessionManager
from src.utils.session_logger import read_logs, get_log_file_path
from src.utils.helpers import load_json_file
from src.core.config import config


class SessionController:
    """Controller for session management operations."""
    
    def __init__(self):
        """Initialize the session controller."""
        self.quiz_orchestrator = QuizOrchestrator()
        self.interview_session_manager = InterviewSessionManager()
    
    def list_active_sessions(self) -> Dict[str, Any]:
        """Return active sessions from both interview and quiz workflows."""
        try:
            quiz_sessions = self.quiz_orchestrator.list_active_sessions()
            interview_sessions = self.interview_session_manager.list_sessions()
            
            # Format interview sessions to match expected structure
            formatted_interview_sessions = []
            for session in interview_sessions:
                formatted_interview_sessions.append({
                    "session_id": session["session_id"],
                    "name": session["name"],
                    "status": session["status"],
                    "progress": session["progress"],
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"]
                })
            
            return {
                "ok": True,
                "quiz": quiz_sessions.get("sessions", []),
                "interview": formatted_interview_sessions,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list active sessions: {str(e)}")
    
    def get_session_logs(self, session_id: str, limit: int = 200) -> Dict[str, Any]:
        """Return recent JSONL logs for a given session id."""
        try:
            logs = read_logs(session_id=session_id, limit=limit)
            return {"ok": True, "session_id": session_id, "logs": logs}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get session logs: {str(e)}")
    
    def get_session_detail(self, session_id: str) -> Dict[str, Any]:
        """Fetch session progress JSON if present (quiz or interview)."""
        try:
            # Check quiz progress dir
            quiz_progress_dir = os.path.join(config.temp_dir, "quiz_progress")
            if os.path.isdir(quiz_progress_dir):
                for name in os.listdir(quiz_progress_dir):
                    if session_id in name and name.endswith(".json"):
                        data = load_json_file(os.path.join(quiz_progress_dir, name))
                        return {"ok": True, "data": data}

            # Check interview sessions using new session manager
            interview_session = self.interview_session_manager.get_session(session_id)
            if interview_session:
                return {"ok": True, "data": interview_session}

            # Fallback: Check old interview progress files (for backward compatibility)
            if os.path.isdir(config.temp_dir):
                for name in os.listdir(config.temp_dir):
                    if name.startswith("progress_") and name.endswith(".json"):
                        path = os.path.join(config.temp_dir, name)
                        try:
                            data = load_json_file(path)
                            if data.get("session_id") == session_id:
                                return {"ok": True, "data": data}
                        except Exception:
                            continue

            raise HTTPException(status_code=404, detail="Session not found")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get session detail: {str(e)}")
    
    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused session if possible (quiz or interview)."""
        try:
            # Try quiz first
            quiz_result = self.quiz_orchestrator.resume_quiz_generation(session_id)
            if quiz_result.get("status") != "error":
                return {"ok": True, "result": quiz_result}

            # Try interview using new session manager
            session = self.interview_session_manager.get_session(session_id)
            if session:
                # Use the workflow orchestrator to resume
                from ...agents.interview.workflow.orchestrator import InterviewWorkflowOrchestrator
                orchestrator = InterviewWorkflowOrchestrator()
                result = orchestrator.resume_session(session_id)
                if result.get("status") != "failed":
                    return {"ok": True, "result": result}

            raise HTTPException(status_code=404, detail="Unable to resume session")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to resume session: {str(e)}")
    
    def delete_session(self, session_id: str) -> Dict[str, Any]:
        """Delete a session's progress artifacts and logs (quiz and interview)."""
        removed: Dict[str, Any] = {
            "progress_files": [],
            "logs_deleted": False,
        }

        try:
            # Delete quiz progress files
            quiz_progress_dir = os.path.join(config.temp_dir, "quiz_progress")
            if os.path.isdir(quiz_progress_dir):
                for name in os.listdir(quiz_progress_dir):
                    if session_id in name and name.endswith(".json"):
                        path = os.path.join(quiz_progress_dir, name)
                        try:
                            os.remove(path)
                            removed["progress_files"].append(path)
                        except Exception:
                            pass

            # Delete interview session using new session manager
            try:
                self.interview_session_manager.delete_session(session_id)
                removed["progress_files"].append(f"interview_session_{session_id}.json")
            except Exception:
                pass

            # Also check old interview progress files (for backward compatibility)
            if os.path.isdir(config.temp_dir):
                for name in os.listdir(config.temp_dir):
                    if name.startswith("progress_") and name.endswith(".json"):
                        path = os.path.join(config.temp_dir, name)
                        try:
                            data = load_json_file(path)
                            if data.get("session_id") == session_id:
                                try:
                                    os.remove(path)
                                    removed["progress_files"].append(path)
                                except Exception:
                                    pass
                        except Exception:
                            continue

            # Delete logs file
            log_path = get_log_file_path(session_id)
            if os.path.exists(log_path):
                try:
                    os.remove(log_path)
                    removed["logs_deleted"] = True
                except Exception:
                    pass

            return {"ok": True, "removed": removed}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

