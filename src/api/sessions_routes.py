from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
import os

from ..agents.quiz.quiz_orchestrator import QuizOrchestrator
from ..agents.interview.interview_sheet_manager import InterviewSheetManager
from ..utils.session_logger import read_logs, get_log_file_path
from ..utils.helpers import load_json_file
from ..core.config import config


router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/active")
def list_active_sessions():
    """Return active sessions from both interview and quiz workflows."""
    quiz = QuizOrchestrator()
    interview = InterviewSheetManager()
    quiz_sessions = quiz.list_active_sessions()
    interview_sessions = interview.list_active_sessions()

    return {
        "ok": True,
        "quiz": quiz_sessions.get("sessions", []),
        "interview": interview_sessions.get("sessions", []),
    }


@router.get("/logs/{session_id}")
def get_session_logs(session_id: str, limit: int = Query(default=200, ge=1, le=2000)):
    """Return recent JSONL logs for a given session id."""
    logs = read_logs(session_id=session_id, limit=limit)
    return {"ok": True, "session_id": session_id, "logs": logs}


@router.get("/detail/{session_id}")
def get_session_detail(session_id: str):
    """Fetch session progress JSON if present (quiz or interview)."""
    # Check quiz progress dir
    quiz_progress_dir = os.path.join(config.temp_dir, "quiz_progress")
    if os.path.isdir(quiz_progress_dir):
        for name in os.listdir(quiz_progress_dir):
            if session_id in name and name.endswith(".json"):
                return {"ok": True, "data": load_json_file(os.path.join(quiz_progress_dir, name))}

    # Check interview progress files
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


@router.post("/resume/{session_id}")
def resume_session(session_id: str):
    """Resume a paused session if possible (quiz or interview)."""
    # Try quiz first
    quiz = QuizOrchestrator()
    quiz_result = quiz.resume_quiz_generation(session_id)
    if quiz_result.get("status") != "error":
        return {"ok": True, "result": quiz_result}

    # Try interview by locating filepath
    interview = InterviewSheetManager()
    sessions = interview.list_active_sessions().get("sessions", [])
    match = next((s for s in sessions if s.get("session_id") == session_id), None)
    if match:
        result = interview.resume_session(match.get("filepath"))
        if result.get("status") != "error":
            return {"ok": True, "result": result}

    raise HTTPException(status_code=404, detail="Unable to resume session")


@router.delete("/{session_id}")
def delete_session(session_id: str):
    """Delete a session's progress artifacts and logs (quiz and interview).

    This removes:
    - Quiz progress file under temp/quiz_progress containing the session_id
    - Interview progress file(s) in temp/ matching the session_id in content
    - Session log file under logs/sessions/{session_id}.log
    """
    removed: Dict[str, Any] = {
        "progress_files": [],
        "logs_deleted": False,
    }

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
                    # best effort
                    pass

    # Delete interview progress files that match session_id in JSON content
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

