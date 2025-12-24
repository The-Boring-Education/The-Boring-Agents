"""
Quiz generation controller.

Handles all business logic for quiz operations.
Matches the Interview Prep controller pattern for consistency.

NOTE: This controller references QuizWorkflowOrchestrator which you need to implement
in src/agents/quiz/workflow/orchestrator.py using LangGraph.
"""

import logging
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, BackgroundTasks

# TODO: Implement QuizWorkflowOrchestrator in src/agents/quiz/workflow/orchestrator.py
# Uncomment the import below once implemented:
# from src.agents.quiz.workflow.orchestrator import QuizWorkflowOrchestrator

from src.core.session.session_types import SessionStatus
from src.core.env import get_env_manager
from src.api.models.quiz_models import (
    CreateQuizRequest,
    TopicGenerationRequest,
    BulkTopicRequest,
    BulkGenerationRequest,
    UploadQuizRequest,
    ValidateQuizRequest,
    SessionResponse,
    SimpleStatus,
    QuizTopicTemplate,
    QuizCategorySuggestion,
)

logger = logging.getLogger(__name__)
env_manager = get_env_manager()


class QuizController:
    """Controller for quiz generation operations.
    
    Pattern matches InterviewPrepController for consistency.
    """
    
    def __init__(self):
        """Initialize the quiz controller."""
        # TODO: Uncomment once you implement QuizWorkflowOrchestrator
        # self.orchestrator = QuizWorkflowOrchestrator()
        
        # Placeholder until orchestrator is implemented
        self.orchestrator = None
        
        # Auto-fix sessions on startup (like Interview Prep)
        if self.orchestrator:
            try:
                _ = self.orchestrator.session_manager.list_sessions()
                logger.info("✅ Quiz controller initialized with orchestrator")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize quiz sessions: {e}")
        else:
            logger.warning("⚠️ QuizWorkflowOrchestrator not implemented yet. Quiz generation will not work.")
    
    def _check_orchestrator(self):
        """Check if orchestrator is available."""
        if not self.orchestrator:
            raise HTTPException(
                status_code=501,
                detail="QuizWorkflowOrchestrator not implemented yet. Implement it in src/agents/quiz/workflow/orchestrator.py"
            )
    
    # =========================================================================
    # Quiz Creation
    # =========================================================================
    
    def create_quiz(
        self,
        payload: CreateQuizRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """
        Create quiz using workflow orchestrator.
        
        Args:
            payload: Create quiz request
            background_tasks: FastAPI background tasks
            
        Returns:
            Session response
        """
        self._check_orchestrator()
        
        try:
            # Create description if not provided
            description = payload.description or f"Quiz for {payload.topic}. Difficulty: {payload.difficulty.value}."
            
            session_id = self.orchestrator.start_generation(
                topic=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                question_count=payload.question_count,
                target_audience=payload.target_audience,
                difficulty=payload.difficulty.value
            )
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating quiz: {payload.topic}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating quiz: {e}")
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
            logger.error(f"Error executing quiz workflow for session {session_id}: {e}")
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active/recent quiz sessions."""
        self._check_orchestrator()
        
        # Get sessions from orchestrator
        orchestrator_sessions = self.orchestrator.session_manager.list_sessions(status)
        
        # Convert to expected format (matching Interview Prep pattern)
        formatted_sessions = []
        for session in orchestrator_sessions:
            progress = session.get("progress", {})
            questions = session.get("questions", [])
            
            # Get question_count with fallbacks
            question_count = session.get("question_count")
            if not question_count or question_count is None:
                question_count = progress.get("total") or len(questions) or 20
                session["question_count"] = question_count
                try:
                    self.orchestrator.session_manager.save_session(session["session_id"], session)
                except Exception as e:
                    logger.warning(f"Failed to save question_count for session {session['session_id']}: {e}")
            
            final_question_count = int(question_count) if question_count else 20
            
            formatted_sessions.append({
                "sessionId": session["session_id"],
                "topic": session.get("topic", session.get("name", "Unknown")),
                "agentType": session.get("agent_type", "generic"),
                "targetAudience": session.get("target_audience", "developers"),
                "questionCount": final_question_count,
                "question_count": final_question_count,  # snake_case for compatibility
                "status": session["status"],
                "progress": progress,
                "startedAt": session["created_at"],
                "completedAt": session.get("updated_at") if session["status"] == "completed" else None,
                "outputFile": session.get("output_file"),
                "quizData": session.get("quiz_data"),
                "error": session.get("error")
            })
        
        return formatted_sessions
    
    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress for a specific quiz session."""
        self._check_orchestrator()
        
        try:
            session_status = self.orchestrator.get_session_status(session_id)
            
            # Ensure both camelCase and snake_case versions are present
            question_count = session_status.get("question_count")
            if question_count is not None:
                session_status["questionCount"] = question_count
            elif "questionCount" not in session_status:
                questions = session_status.get("questions", [])
                progress = session_status.get("progress", {})
                question_count = progress.get("total") or len(questions) or 20
                session_status["question_count"] = question_count
                session_status["questionCount"] = question_count
            
            return session_status
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def cancel_session(self, session_id: str) -> Dict[str, str]:
        """Cancel a running quiz session."""
        self._check_orchestrator()
        
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
        """Resume/retry a quiz session."""
        self._check_orchestrator()
        
        try:
            status = self.orchestrator.get_session_status(session_id)
            if status["status"] == "completed":
                raise HTTPException(status_code=400, detail="Session already completed")
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Resuming quiz session: {session_id}"
            )
        except ValueError:
            raise HTTPException(status_code=404, detail="Session not found")
    
    def delete_session(self, session_id: str) -> Dict[str, str]:
        """Delete a quiz session."""
        self._check_orchestrator()
        
        try:
            self.orchestrator.session_manager.delete_session(session_id)
            return {"message": "Session deleted"}
        except Exception:
            raise HTTPException(status_code=404, detail="Session not found")
    
    # =========================================================================
    # Topic Generation
    # =========================================================================
    
    def generate_topic(
        self,
        payload: TopicGenerationRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """
        Generate quiz for a single topic.
        
        Args:
            payload: Topic generation request
            background_tasks: FastAPI background tasks
            
        Returns:
            Session response
        """
        self._check_orchestrator()
        
        try:
            description = f"Quiz for {payload.topic}. Difficulty: {payload.difficulty.value}."
            
            session_id = self.orchestrator.session_manager.create_session(
                topic=payload.topic,
                description=description,
                agent_type=payload.agent_type.value,
                question_count=payload.question_count,
                target_audience=payload.target_audience,
                difficulty=payload.difficulty.value
            )
            
            # Execute workflow in background
            background_tasks.add_task(self._execute_workflow_background, session_id)
            
            return SessionResponse(
                sessionId=session_id,
                message=f"Started generating quiz for topic: {payload.topic}"
            )
        except Exception as e:
            logger.error(f"Error generating quiz topic: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    def bulk_generate(
        self,
        payload: BulkGenerationRequest,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """
        Start bulk quiz generation for multiple topics.
        
        Args:
            payload: Bulk generation request
            background_tasks: FastAPI background tasks
            
        Returns:
            Dictionary with session IDs and status
        """
        self._check_orchestrator()
        
        try:
            session_ids = []
            errors = []
            
            for topic_request in payload.topics:
                try:
                    description = f"Quiz for {topic_request.topic}. Difficulty: {topic_request.difficulty.value}."
                    
                    session_id = self.orchestrator.start_generation(
                        topic=topic_request.topic,
                        description=description,
                        agent_type=topic_request.agent_type.value,
                        question_count=topic_request.question_count,
                        target_audience=topic_request.target_audience,
                        difficulty=topic_request.difficulty.value
                    )
                    
                    # Store additional metadata
                    session_data = self.orchestrator.session_manager.get_session(session_id)
                    if session_data:
                        session_data["auto_upload"] = payload.auto_upload
                        self.orchestrator.session_manager.save_session(session_id, session_data)
                    
                    # Execute workflow in background
                    background_tasks.add_task(self._execute_workflow_background, session_id)
                    
                    session_ids.append({
                        "sessionId": session_id,
                        "topic": topic_request.topic,
                        "status": "started"
                    })
                except Exception as e:
                    logger.error(f"Error generating quiz for topic {topic_request.topic}: {e}")
                    errors.append({
                        "topic": topic_request.topic,
                        "error": str(e)
                    })
            
            return {
                "sessions": session_ids,
                "errors": errors,
                "total": len(payload.topics),
                "started": len(session_ids),
                "failed": len(errors)
            }
        except Exception as e:
            logger.error(f"Error in bulk generate: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    # =========================================================================
    # Output & Upload
    # =========================================================================
    
    def get_session_output(self, session_id: str) -> Dict[str, Any]:
        """Get final output for a completed quiz session."""
        self._check_orchestrator()
        
        import os
        import json
        
        try:
            status = self.orchestrator.get_session_status(session_id)
            output_file = status.get("output_file")
            
            if not output_file or not os.path.exists(output_file):
                raise HTTPException(status_code=404, detail="Output file not found")
            
            with open(output_file, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)
            
            return {
                "status": "success",
                "session_id": session_id,
                "quiz_data": quiz_data
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    def validate_quiz(self, payload: ValidateQuizRequest) -> SimpleStatus:
        """Validate quiz structure and content."""
        try:
            quiz_data = payload.quiz
            errors = []
            
            # Basic structure validation
            required_fields = ["categoryName", "categoryDescription", "questions"]
            for field in required_fields:
                if field not in quiz_data:
                    errors.append(f"Missing required field: {field}")
            
            # Validate questions
            questions = quiz_data.get("questions", [])
            if not questions:
                errors.append("Quiz must have at least one question")
            else:
                for i, question in enumerate(questions):
                    q_errors = self._validate_question(question, i)
                    errors.extend(q_errors)
            
            if errors:
                return SimpleStatus(ok=False, message=f"Validation failed: {'; '.join(errors[:5])}")
            
            return SimpleStatus(ok=True, message="Validation successful")
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
    
    def _validate_question(self, question: Dict[str, Any], index: int) -> List[str]:
        """Validate a single quiz question."""
        errors = []
        prefix = f"Question {index + 1}"
        
        required = ["question", "options", "correctAnswer", "explanation", "difficulty"]
        for field in required:
            if field not in question:
                errors.append(f"{prefix}: Missing field '{field}'")
        
        options = question.get("options", [])
        if len(options) != 4:
            errors.append(f"{prefix}: Must have exactly 4 options (found {len(options)})")
        
        correct_answer = question.get("correctAnswer")
        if correct_answer is not None and (not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3):
            errors.append(f"{prefix}: correctAnswer must be 0-3")
        
        difficulty = question.get("difficulty", "").lower()
        if difficulty not in ["easy", "medium", "hard"]:
            errors.append(f"{prefix}: Invalid difficulty '{difficulty}'")
        
        return errors
    
    def upload_quiz(self, payload: UploadQuizRequest) -> SimpleStatus:
        """Upload quiz to database via API."""
        import requests
        
        try:
            # Validate first
            validation = self.validate_quiz(ValidateQuizRequest(quiz=payload.quiz))
            if not validation.ok:
                return SimpleStatus(ok=False, message=f"Validation failed: {validation.message}")
            
            # Get API URL from config or payload
            from src.core.config import config
            api_url = (payload.api_url or config.api_base_url).rstrip('/')
            
            # Prepare request
            url = f"{api_url}/api/v1/quiz"
            headers = {
                'x-admin-secret': payload.admin_secret or 'TBEAdmin',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, json=payload.quiz, headers=headers, timeout=30)
            
            if response.status_code in [200, 201]:
                return SimpleStatus(ok=True, message="Quiz uploaded successfully")
            else:
                return SimpleStatus(ok=False, message=f"Upload failed: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            return SimpleStatus(ok=False, message="Upload timeout - API server may be slow")
        except requests.exceptions.ConnectionError:
            return SimpleStatus(ok=False, message="Connection error - check if API server is running")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # =========================================================================
    # Templates & Suggestions
    # =========================================================================
    
    def get_topic_templates(self) -> List[QuizTopicTemplate]:
        """Get available quiz topic templates."""
        templates = [
            {
                "name": "React.js",
                "description": "React.js quiz covering hooks, components, state management, and best practices",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "frontend engineers"],
                "category": "Frontend Framework",
                "tags": ["react", "javascript", "frontend"]
            },
            {
                "name": "Node.js",
                "description": "Node.js backend quiz including Express, APIs, and server-side concepts",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "backend engineers"],
                "category": "Backend Runtime",
                "tags": ["nodejs", "javascript", "backend"]
            },
            {
                "name": "JavaScript",
                "description": "Core JavaScript concepts including ES6+, async programming, and fundamentals",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 25,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "beginners"],
                "category": "Programming Language",
                "tags": ["javascript", "programming", "web"]
            },
            {
                "name": "Python",
                "description": "Python programming quiz covering syntax, libraries, OOP, and best practices",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "data scientists"],
                "category": "Programming Language",
                "tags": ["python", "programming", "backend"]
            },
            {
                "name": "Data Structures & Algorithms",
                "description": "DSA concepts including arrays, trees, graphs, sorting, and algorithms",
                "agentTypes": ["dsa"],
                "suggestedQuestionCount": 30,
                "difficulty": "Hard",
                "targetAudiences": ["developers", "interview prep"],
                "category": "Computer Science",
                "tags": ["algorithms", "data-structures", "coding"]
            },
            {
                "name": "MongoDB",
                "description": "MongoDB quiz covering CRUD operations, aggregations, and schema design",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "backend engineers"],
                "category": "Database",
                "tags": ["mongodb", "nosql", "database"]
            },
            {
                "name": "SQL",
                "description": "SQL quiz covering queries, joins, normalization, and optimization",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "data analysts"],
                "category": "Database",
                "tags": ["sql", "database", "queries"]
            },
            {
                "name": "DevOps",
                "description": "DevOps concepts including CI/CD, Docker, Kubernetes, and cloud services",
                "agentTypes": ["tech"],
                "suggestedQuestionCount": 20,
                "difficulty": "Medium",
                "targetAudiences": ["developers", "DevOps engineers"],
                "category": "Infrastructure",
                "tags": ["devops", "docker", "kubernetes", "cloud"]
            }
        ]
        return [QuizTopicTemplate(**t) for t in templates]
    
    def get_category_suggestions(self) -> List[QuizCategorySuggestion]:
        """Get quiz category suggestions."""
        categories = [
            {
                "name": "Frontend Development",
                "description": "Complete frontend development quiz collection",
                "topics": ["HTML/CSS", "JavaScript", "React.js", "TypeScript", "Vue.js"],
                "difficulty": "Medium",
                "estimatedTime": "30-45 minutes"
            },
            {
                "name": "Backend Development",
                "description": "Backend development quiz collection",
                "topics": ["Node.js", "Python", "Database Design", "API Development", "Authentication"],
                "difficulty": "Medium",
                "estimatedTime": "30-45 minutes"
            },
            {
                "name": "Full Stack",
                "description": "Comprehensive full stack development quiz",
                "topics": ["JavaScript", "React.js", "Node.js", "MongoDB", "REST APIs"],
                "difficulty": "Hard",
                "estimatedTime": "45-60 minutes"
            },
            {
                "name": "Data Structures & Algorithms",
                "description": "DSA preparation quiz for coding interviews",
                "topics": ["Arrays", "Linked Lists", "Trees", "Graphs", "Dynamic Programming"],
                "difficulty": "Hard",
                "estimatedTime": "60-90 minutes"
            }
        ]
        return [QuizCategorySuggestion(**c) for c in categories]
