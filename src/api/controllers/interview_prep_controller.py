"""Interview preparation controller."""

import logging
from typing import Optional, List, Dict, Any

from fastapi import HTTPException, BackgroundTasks

from src.agents.interview.workflow.orchestrator import InterviewWorkflowOrchestrator
from src.core.session.session_types import SessionStatus
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    TopicGenerationRequest,
    SessionResponse,
    TopicTemplate,
)

logger = logging.getLogger(__name__)

# Hardcoded topic templates -- move to DB / config file when the list grows.
_TOPIC_TEMPLATES: List[Dict[str, Any]] = [
    {"name": "React.js", "description": "React.js interview questions covering hooks, components, state management, and best practices", "agentTypes": ["tech"], "suggestedQuestionCount": 25, "difficulty": "Medium", "roadmaps": ["Frontend", "Fullstack"], "category": "Frontend Framework", "tags": ["react", "javascript", "frontend"]},
    {"name": "Node.js", "description": "Node.js backend development questions including Express, APIs, and server-side concepts", "agentTypes": ["tech"], "suggestedQuestionCount": 30, "difficulty": "Medium", "roadmaps": ["Backend", "Fullstack"], "category": "Backend Runtime", "tags": ["nodejs", "javascript", "backend"]},
    {"name": "Data Structures & Algorithms", "description": "Core DSA concepts including arrays, trees, graphs, sorting, and algorithmic thinking", "agentTypes": ["dsa"], "suggestedQuestionCount": 40, "difficulty": "Hard", "roadmaps": ["DSA"], "category": "Computer Science", "tags": ["algorithms", "data-structures", "coding"]},
    {"name": "Python", "description": "Python programming questions covering syntax, libraries, OOP, and best practices", "agentTypes": ["tech"], "suggestedQuestionCount": 25, "difficulty": "Medium", "roadmaps": ["Backend", "Tech"], "category": "Programming Language", "tags": ["python", "programming", "backend"]},
    {"name": "System Design", "description": "System design interview questions covering scalability, architecture, and distributed systems", "agentTypes": ["system_design"], "suggestedQuestionCount": 15, "difficulty": "Hard", "roadmaps": ["Backend", "Fullstack"], "category": "Architecture", "tags": ["system-design", "architecture", "scalability"]},
    {"name": "JavaScript", "description": "Core JavaScript concepts including ES6+, async programming, and DOM manipulation", "agentTypes": ["tech"], "suggestedQuestionCount": 30, "difficulty": "Medium", "roadmaps": ["Frontend", "Fullstack"], "category": "Programming Language", "tags": ["javascript", "programming", "frontend"]},
    {"name": "Database Design", "description": "Database concepts including SQL, NoSQL, normalization, and query optimization", "agentTypes": ["tech"], "suggestedQuestionCount": 20, "difficulty": "Medium", "roadmaps": ["Backend", "Fullstack"], "category": "Database", "tags": ["database", "sql", "nosql"]},
]


class InterviewPrepController:
    """Controller for interview preparation operations."""

    def __init__(self):
        self.orchestrator = InterviewWorkflowOrchestrator()
        try:
            self.orchestrator.session_manager.fix_all_sessions_question_count()
        except Exception as e:
            logger.warning("Failed to auto-fix sessions on init: %s", e, exc_info=True)

    # -- sheet / topic generation ---------------------------------------------

    def create_sheet(self, payload: CreateSheetRequest, background_tasks: BackgroundTasks) -> SessionResponse:
        try:
            session_id = self.orchestrator.start_generation(
                name=payload.name,
                description=payload.description,
                agent_type=payload.agent_type.value,
                roadmap=payload.roadmap,
                technology=payload.technology,
                question_count=payload.question_count,
            )
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return SessionResponse(sessionId=session_id, message=f"Started generating interview sheet: {payload.name}")
        except Exception as e:
            logger.error("Error creating sheet: %s", e)
            raise HTTPException(status_code=400, detail=str(e))

    def generate_topic(self, payload: TopicGenerationRequest, background_tasks: BackgroundTasks) -> SessionResponse:
        try:
            description = f"Interview questions for {payload.topic}. Difficulty: {payload.difficulty}. Roadmap: {payload.roadmap}."
            session_id = self.orchestrator.session_manager.create_session(
                name=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                roadmap=payload.roadmap,
                question_count=payload.question_count,
                technology=payload.technology,
                difficulty=payload.difficulty,
                generate_answers=payload.generate_answers,
            )
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return SessionResponse(sessionId=session_id, message=f"Started generating questions for topic: {payload.topic}")
        except Exception as e:
            logger.error("Error generating topic: %s", e)
            raise HTTPException(status_code=400, detail=str(e))

    # -- session queries ------------------------------------------------------

    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Session manager already auto-fixes question_count, so no fallback needed here."""
        sessions = self.orchestrator.session_manager.list_sessions(status)
        return [self._format_session(s) for s in sessions]

    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        try:
            result = self.orchestrator.get_session_status(session_id)
            qc = result.get("question_count", 20)
            result["questionCount"] = qc
            return result
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    # -- session actions ------------------------------------------------------

    def cancel_session(self, session_id: str) -> Dict[str, str]:
        try:
            session = self.orchestrator.get_session_status(session_id)
            if session["status"] in ("in_progress", "pending", "metadata_generating", "questions_generating", "answers_generating"):
                self.orchestrator.session_manager.update_status(
                    session_id, SessionStatus.FAILED,
                    current_step="Cancelled by user", error="Cancelled by user",
                )
            return {"message": "Session cancelled"}
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def retry_session(self, session_id: str, background_tasks: BackgroundTasks) -> SessionResponse:
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status["status"] == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            background_tasks.add_task(self._execute_workflow_background, session_id)
            return SessionResponse(sessionId=session_id, message=f"Resuming session: {session_id}")
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")

    def delete_session(self, session_id: str) -> Dict[str, str]:
        try:
            self.orchestrator.session_manager.delete_session(session_id)
            return {"message": "Session deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")

    # -- question CRUD --------------------------------------------------------

    def update_question(self, session_id: str, question_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.orchestrator.session_manager.update_question_in_session(session_id, question_id, updates)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error("Error updating question %s in session %s: %s", question_id, session_id, e)
            raise HTTPException(status_code=500, detail="Failed to update question")

    def get_question(self, session_id: str, question_id: str) -> Dict[str, Any]:
        try:
            question = self.orchestrator.session_manager.get_question(session_id, question_id)
            if not question:
                raise HTTPException(status_code=404, detail="Question not found")
            return question
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error getting question %s in session %s: %s", question_id, session_id, e)
            raise HTTPException(status_code=500, detail="Failed to get question")

    def delete_question(self, session_id: str, question_id: str) -> Dict[str, Any]:
        try:
            if not self.orchestrator.session_manager.delete_question(session_id, question_id):
                raise HTTPException(status_code=404, detail="Question not found")
            session = self.orchestrator.session_manager.get_session(session_id)
            return {"message": "Question deleted", "remaining_questions": len(session.get("questions", [])) if session else 0}
        except HTTPException:
            raise
        except Exception as e:
            logger.error("Error deleting question %s in session %s: %s", question_id, session_id, e)
            raise HTTPException(status_code=500, detail="Failed to delete question")

    def add_question(self, session_id: str, question: Dict[str, Any]) -> Dict[str, Any]:
        try:
            added = self.orchestrator.session_manager.add_question(session_id, question)
            session = self.orchestrator.session_manager.get_session(session_id)
            return {"question": added, "total_questions": len(session.get("questions", [])) if session else 0}
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            logger.error("Error adding question to session %s: %s", session_id, e)
            raise HTTPException(status_code=500, detail="Failed to add question")

    # -- templates ------------------------------------------------------------

    def get_topic_templates(self) -> List[TopicTemplate]:
        return [TopicTemplate(**t) for t in _TOPIC_TEMPLATES]

    # -- private helpers ------------------------------------------------------

    def _execute_workflow_background(self, session_id: str):
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as e:
            logger.error("Background workflow error for session %s: %s", session_id, e)

    @staticmethod
    def _format_session(session: Dict[str, Any]) -> Dict[str, Any]:
        qc = int(session.get("question_count", 20))
        return {
            "sessionId": session["session_id"],
            "topic": session.get("name", "Unknown"),
            "agentType": session.get("agent_type", "generic"),
            "roadmap": session.get("roadmap", "Tech"),
            "questionCount": qc,
            "question_count": qc,
            "status": session["status"],
            "progress": session.get("progress", {}),
            "startedAt": session.get("created_at"),
            "completedAt": session.get("updated_at") if session["status"] == "completed" else None,
            "outputFile": session.get("output_file"),
            "sheetData": session.get("sheet_data"),
            "error": session.get("error"),
        }
