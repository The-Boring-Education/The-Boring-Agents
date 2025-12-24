"""
Interview preparation controller.

Handles all business logic for interview preparation operations.
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, BackgroundTasks

from src.agents.interview.workflow.orchestrator import InterviewWorkflowOrchestrator
from src.core.session.session_types import SessionStatus
from src.core.env import get_env_manager
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    TopicGenerationRequest,
    SessionResponse,
    TopicTemplate,
    RoadmapSuggestion,
)

logger = logging.getLogger(__name__)
env_manager = get_env_manager()


class InterviewPrepController:
    """Controller for interview preparation operations."""
    
    def __init__(self):
        """Initialize the interview prep controller."""
        self.orchestrator = InterviewWorkflowOrchestrator()
        # Force auto-fix all existing sessions on first initialization
        try:
            # First, trigger list_sessions which auto-fixes all sessions
            _ = self.orchestrator.session_manager.list_sessions()
            # Then run explicit migration
            fixed = self.orchestrator.session_manager.fix_all_sessions_question_count()
            logger.info(f"✅ Auto-fixed question_count for sessions on startup (explicit fix: {fixed} sessions)")
        except Exception as e:
            logger.warning(f"⚠️ Failed to auto-fix sessions on initialization: {e}", exc_info=True)
    
    def create_sheet(
        self,
        payload: CreateSheetRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """
        Create interview sheet using workflow orchestrator.
        
        Args:
            payload: Create sheet request
            background_tasks: FastAPI background tasks
            
        Returns:
            Session response
        """
        try:
            session_id = self.orchestrator.start_generation(
                name=payload.name,
                description=payload.description,
                agent_type=payload.agent_type.value,
                roadmap=payload.roadmap,
                technology=payload.technology,
                question_count=payload.question_count
            )
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating interview sheet: {payload.name}"
            )
        except Exception as e:
            logger.error(f"Error creating sheet: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def _execute_workflow_background(self, session_id: str):
        """
        Execute workflow in background.
        
        Args:
            session_id: Session ID
        """
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as e:
            logger.error(f"Error executing workflow for session {session_id}: {e}")
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active/recent sessions."""
        # Get sessions from orchestrator (this already auto-fixes question_count)
        orchestrator_sessions = self.orchestrator.session_manager.list_sessions(status)
        
        # Convert to expected format
        formatted_sessions = []
        for session in orchestrator_sessions:
            progress = session.get("progress", {})
            questions = session.get("questions", [])
            
            # Get question_count - should already be fixed by list_sessions
            question_count = session.get("question_count")
            
            # Double-check: if still missing, calculate from available data
            if not question_count or question_count is None:
                # Fallback to progress.total or questions array length
                question_count = progress.get("total") or len(questions)
            if not question_count:
                question_count = 20  # Default fallback
                # Update session with calculated value
                session["question_count"] = question_count
                try:
                    self.orchestrator.session_manager.save_session(session["session_id"], session)
                except Exception as e:
                    logger.warning(f"Failed to save calculated question_count for session {session['session_id']}: {e}")
            
            # Ensure question_count is never None/undefined in response (GUARANTEED)
            final_question_count = int(question_count) if question_count else 20
            
            formatted_sessions.append({
                "sessionId": session["session_id"],
                "topic": session.get("name", "Unknown"),  # Map name to topic for compatibility
                "agentType": session.get("agent_type", "generic"),
                "roadmap": session.get("roadmap", "Tech"),
                "questionCount": final_question_count,  # camelCase for frontend (ALWAYS a number, NEVER None/undefined)
                "question_count": final_question_count,  # snake_case for compatibility with validation (ALWAYS a number, NEVER None/undefined)
                "status": session["status"],
                "progress": progress,
                "startedAt": session["created_at"],
                "completedAt": session.get("updated_at") if session["status"] == "completed" else None,
                "outputFile": session.get("output_file"),
                "sheetData": session.get("sheet_data"),
                "error": session.get("error")
            })
        
        return formatted_sessions
    
    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress for a specific session."""
        try:
            session_status = self.orchestrator.get_session_status(session_id)
            # Ensure both questionCount (camelCase) and question_count (snake_case) are present
            question_count = session_status.get("question_count")
            if question_count is not None:
                # Add camelCase version for frontend compatibility
                session_status["questionCount"] = question_count
            elif "questionCount" not in session_status:
                # Fallback: calculate from questions array
                questions = session_status.get("questions", [])
                progress = session_status.get("progress", {})
                question_count = progress.get("total") or len(questions) or 20
                session_status["question_count"] = question_count
                session_status["questionCount"] = question_count
            return session_status
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def cancel_session(self, session_id: str) -> Dict[str, str]:
        """Cancel a running session."""
        try:
            session = self.orchestrator.get_session_status(session_id)
            if session["status"] == "in_progress":
                self.orchestrator.session_manager.update_status(
                    session_id,
                    SessionStatus.FAILED,
                    current_step="Cancelled by user",
                    error="Cancelled by user"
                )
                from ...utils.session_logger import append_log
                append_log(session_id, "session_cancelled", {})
            return {"message": "Session cancelled"}
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def retry_session(
        self,
        session_id: str,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """Resume/retry a session."""
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status["status"] == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Resuming session: {session_id}"
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def delete_session(self, session_id: str) -> Dict[str, str]:
        """Delete a session."""
        try:
            self.orchestrator.session_manager.delete_session(session_id)
            return {"message": "Session deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def get_topic_templates(self) -> List[TopicTemplate]:
        """Get available topic templates."""
        templates = [
            {
                "name": "React.js",
                "description": "React.js interview questions covering hooks, components, state management, and best practices",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 25,
                "difficulty": "Medium",
                "roadmaps": ["Frontend", "Fullstack"],
                "category": "Frontend Framework",
                "tags": ["react", "javascript", "frontend"]
            },
            {
                "name": "Node.js",
                "description": "Node.js backend development questions including Express, APIs, and server-side concepts",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 30,
                "difficulty": "Medium",
                "roadmaps": ["Backend", "Fullstack"],
                "category": "Backend Runtime",
                "tags": ["nodejs", "javascript", "backend"]
            },
            {
                "name": "Data Structures & Algorithms",
                "description": "Core DSA concepts including arrays, trees, graphs, sorting, and algorithmic thinking",
                "agentTypes": ["dsa"],
                "suggestedQuestionCount": 40,
                "difficulty": "Hard",
                "roadmaps": ["DSA"],
                "category": "Computer Science",
                "tags": ["algorithms", "data-structures", "coding"]
            },
            {
                "name": "Python",
                "description": "Python programming questions covering syntax, libraries, OOP, and best practices",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 25,
                "difficulty": "Medium",
                "roadmaps": ["Backend", "Tech"],
                "category": "Programming Language",
                "tags": ["python", "programming", "backend"]
            },
            {
                "name": "System Design",
                "description": "System design interview questions covering scalability, architecture, and distributed systems",
                "agentTypes": ["system_design"],
                "suggestedQuestionCount": 15,
                "difficulty": "Hard",
                "roadmaps": ["Backend", "Fullstack"],
                "category": "Architecture",
                "tags": ["system-design", "architecture", "scalability"]
            },
            {
                "name": "JavaScript",
                "description": "Core JavaScript concepts including ES6+, async programming, and DOM manipulation",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 30,
                "difficulty": "Medium",
                "roadmaps": ["Frontend", "Fullstack"],
                "category": "Programming Language",
                "tags": ["javascript", "programming", "frontend"]
            },
            {
                "name": "Database Design",
                "description": "Database concepts including SQL, NoSQL, normalization, and query optimization",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "roadmaps": ["Backend", "Fullstack"],
                "category": "Database",
                "tags": ["database", "sql", "nosql"]
            }
        ]
        return [TopicTemplate(**t) for t in templates]
    
    def generate_topic(
        self,
        payload: TopicGenerationRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """
        Generate questions for a single topic.
        
        Args:
            payload: Topic generation request
            background_tasks: FastAPI background tasks
            
        Returns:
            Session response
        """
        try:
            # Create description from topic if not provided
            description = f"Interview questions for {payload.topic}. Difficulty: {payload.difficulty}. Roadmap: {payload.roadmap}."
            
            # Start generation workflow with question_count
            session_id = self.orchestrator.session_manager.create_session(
                name=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                roadmap=payload.roadmap,
                question_count=payload.question_count,
                technology=payload.technology,
                difficulty=payload.difficulty,
                generate_answers=payload.generate_answers
            )
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating questions for topic: {payload.topic}"
            )
        except Exception as e:
            logger.error(f"Error generating topic: {e}")
            raise HTTPException(status_code=400, detail=str(e))