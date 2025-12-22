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
    GenerateInterviewSheetRequest,
    TopicGenerationRequest,
    BulkTopicRequest,
    BulkGenerationRequest,
    InterviewSheetResponse,
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
    
    def create_sheet_new(
        self,
        payload: CreateSheetRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """Create interview sheet using new workflow orchestrator.
        
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
                technology=payload.technology
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
        """Execute workflow in background.
        
        Args:
            session_id: Session ID
        """
        try:
            self.orchestrator.execute_workflow(session_id)
        except Exception as e:
            logger.error(f"Error executing workflow for session {session_id}: {e}")
    
    def create_sheet(self, payload: GenerateInterviewSheetRequest) -> InterviewSheetResponse:
        """Create interview sheet from MDX file (DEPRECATED - use create_sheet_new instead)."""
        raise HTTPException(
            status_code=410,
            detail="This endpoint is deprecated. Please use /interview/create-sheet-new with name and description instead."
        )
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active/recent sessions."""
        # Get sessions from orchestrator
        orchestrator_sessions = self.orchestrator.session_manager.list_sessions(status)
        
        # Convert to expected format
        formatted_sessions = []
        for session in orchestrator_sessions:
            formatted_sessions.append({
                "sessionId": session["session_id"],
                "topic": session.get("name", "Unknown"),  # Map name to topic for compatibility
                "agentType": session.get("agent_type", "generic"),
                "roadmap": session.get("roadmap", "Tech"),
                "questionCount": session.get("question_count", session["progress"].get("total", 0)),
                "status": session["status"],
                "progress": session["progress"],
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
            return self.orchestrator.get_session_status(session_id)
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
    
    def get_roadmap_suggestions(self) -> List[RoadmapSuggestion]:
        """Get roadmap suggestions."""
        roadmaps = [
            {
                "name": "Frontend Developer",
                "description": "Complete frontend development roadmap covering modern frameworks and tools",
                "topics": ["HTML/CSS", "JavaScript", "React.js", "TypeScript", "State Management"],
                "technologies": ["React", "Vue", "Angular", "TypeScript", "Webpack", "Vite"],
                "difficulty": "Medium",
                "estimatedTime": "3-6 months"
            },
            {
                "name": "Backend Developer",
                "description": "Backend development roadmap focusing on server-side technologies and APIs",
                "topics": ["Node.js", "Python", "Database Design", "API Development", "System Design"],
                "technologies": ["Node.js", "Express", "Python", "Django", "Flask", "PostgreSQL", "MongoDB"],
                "difficulty": "Medium",
                "estimatedTime": "4-8 months"
            },
            {
                "name": "Full Stack Developer",
                "description": "Complete full stack development roadmap covering both frontend and backend",
                "topics": ["JavaScript", "React.js", "Node.js", "Database Design", "System Design", "DevOps"],
                "technologies": ["React", "Node.js", "TypeScript", "PostgreSQL", "Docker", "AWS"],
                "difficulty": "Hard",
                "estimatedTime": "6-12 months"
            },
            {
                "name": "Data Structures & Algorithms",
                "description": "Comprehensive DSA preparation for coding interviews",
                "topics": ["Arrays", "Linked Lists", "Trees", "Graphs", "Dynamic Programming", "Sorting"],
                "technologies": ["Python", "Java", "C++", "JavaScript"],
                "difficulty": "Hard",
                "estimatedTime": "4-6 months"
            }
        ]
        return [RoadmapSuggestion(**r) for r in roadmaps]

