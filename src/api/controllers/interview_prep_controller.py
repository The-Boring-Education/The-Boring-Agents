"""
Interview preparation controller.

Handles all business logic for interview preparation operations.
"""

import json
import logging
import os
import uuid
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from fastapi import HTTPException, BackgroundTasks

from ...agents.interview.interview_sheet_manager import InterviewSheetManager
from ...agents.interview.types import AnswerAgentType
from ...core.config import config
from ...core.env import get_env_manager
from ...utils.session_logger import append_log
from ..models.interview_prep_models import (
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

# Session management (in-memory for now)
active_sessions: Dict[str, Dict[str, Any]] = {}


class InterviewPrepController:
    """Controller for interview preparation operations."""
    
    def __init__(self):
        """Initialize the interview prep controller."""
        pass
    
    def _create_session(self, topic: str, agent_type: str, **kwargs) -> str:
        """Create a new interview generation session."""
        session_id = str(uuid.uuid4())
        session_data = {
            "sessionId": session_id,
            "topic": topic,
            "agentType": agent_type,
            "technology": kwargs.get("technology"),
            "roadmap": kwargs.get("roadmap", "Tech"),
            "questionCount": kwargs.get("question_count", 20),
            "status": "pending",
            "progress": {
                "percent": 0,
                "current_step": "Initializing...",
                "completed_questions": 0,
                "total_questions": kwargs.get("question_count", 20)
            },
            "startedAt": datetime.now().isoformat(),
            "completedAt": None,
            "outputFile": None,
            "sheetData": None,
            "error": None
        }
        active_sessions[session_id] = session_data
        return session_id
    
    def create_sheet(self, payload: GenerateInterviewSheetRequest) -> InterviewSheetResponse:
        """Create interview sheet from MDX file."""
        try:
            manager = InterviewSheetManager(agent_type=payload.agent_type)
            result = manager.create_sheet_from_mdx(mdx_filepath=payload.mdx_file)
            
            output_file = result.get("output_file") if payload.save else None
            
            return InterviewSheetResponse(
                ok=True,
                message="Interview sheet created",
                output_file=output_file,
                sheet=result.get("sheet"),
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    def generate_topic(
        self,
        payload: TopicGenerationRequest,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """Start generation for a single topic."""
        session_id = self._create_session(
            topic=payload.topic,
            agent_type=payload.agent_type.value,
            technology=payload.technology,
            roadmap=payload.roadmap,
            question_count=payload.question_count
        )
        
        # Start background generation
        background_tasks.add_task(self._generate_questions_background, session_id, payload)
        
        return SessionResponse(
            sessionId=session_id,
            message=f"Started generating {payload.question_count} questions for {payload.topic}"
        )
    
    def bulk_generate(
        self,
        payload: BulkGenerationRequest,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Start bulk generation for multiple topics."""
        session_ids = []
        
        for topic_data in payload.topics:
            session_id = self._create_session(
                topic=topic_data.name,
                agent_type=topic_data.agent_type.value,
                technology=topic_data.technology,
                roadmap=topic_data.roadmap,
                question_count=topic_data.question_count
            )
            session_ids.append(session_id)
        
        # Start background bulk generation
        background_tasks.add_task(self._bulk_generate_background, session_ids, payload)
        
        return {
            "sessionIds": session_ids,
            "message": f"Started bulk generation for {len(payload.topics)} topics"
        }
    
    async def _generate_questions_background(self, session_id: str, payload: TopicGenerationRequest):
        """Background task to generate questions for a topic."""
        try:
            append_log(session_id, "request_received", {
                "topic": payload.topic, 
                "question_count": payload.question_count,
                "agent_type": payload.agent_type.value
            })
            
            # Update session status
            active_sessions[session_id]["status"] = "in_progress"
            active_sessions[session_id]["progress"]["current_step"] = "Starting question generation..."
            
            # Initialize manager
            manager_kwargs = {}
            if payload.technology and payload.agent_type == AnswerAgentType.TECH:
                manager_kwargs["technology"] = payload.technology
                
            manager = InterviewSheetManager(agent_type=payload.agent_type, **manager_kwargs)
            
            # Update progress
            active_sessions[session_id]["progress"]["current_step"] = "Generating questions..."
            active_sessions[session_id]["progress"]["percent"] = 10
            
            # Create a mock MDX file for topic-based generation
            mock_mdx_content = f"""---
title: "{payload.topic} Interview Questions"
description: "Interview questions for {payload.topic}"
roadmap: "{payload.roadmap}"
difficulty: "{payload.difficulty}"
questionCount: {payload.question_count}
generateAnswers: {payload.generate_answers}
---

# {payload.topic} Interview Questions

Generate comprehensive interview questions for {payload.topic} topic covering various aspects and difficulty levels.

## Requirements:
- Generate {payload.question_count} relevant questions
- Cover different aspects of {payload.topic}
- Include questions suitable for {payload.difficulty.lower()} level
- Focus on practical and theoretical concepts
"""
            
            # Save mock MDX file
            mock_mdx_file = os.path.join(config.temp_dir, f"topic_{session_id}.mdx")
            os.makedirs(config.temp_dir, exist_ok=True)
            with open(mock_mdx_file, 'w', encoding='utf-8') as f:
                f.write(mock_mdx_content)
            
            # Step 1: Create the sheet structure
            active_sessions[session_id]["progress"]["current_step"] = "Creating sheet structure..."
            active_sessions[session_id]["progress"]["percent"] = 15
            
            sheet_result = manager.create_sheet_from_mdx(mdx_filepath=mock_mdx_file)
            
            if sheet_result.get("status") != "success":
                raise Exception(f"Failed to create sheet: {sheet_result.get('message')}")
            
            # Step 2: Generate questions
            active_sessions[session_id]["progress"]["current_step"] = "Generating questions..."
            active_sessions[session_id]["progress"]["percent"] = 35
            
            questions_result = manager.generate_questions_from_mdx(mdx_filepath=mock_mdx_file)
            
            if questions_result.get("status") != "success":
                raise Exception(f"Failed to generate questions: {questions_result.get('message')}")
            
            questions_file = questions_result.get("filepath")
            
            # Step 3: Add metadata to questions
            active_sessions[session_id]["progress"]["current_step"] = "Adding metadata to questions..."
            active_sessions[session_id]["progress"]["percent"] = 55
            
            metadata_result = manager.add_metadata_to_mdx(mdx_filepath=questions_file)
            
            if metadata_result.get("status") != "success":
                raise Exception(f"Failed to add metadata: {metadata_result.get('message')}")
            
            enhanced_file = metadata_result.get("enhanced_filepath")
            
            # Step 4: Generate answers if requested
            if payload.generate_answers:
                active_sessions[session_id]["progress"]["current_step"] = "Generating answers..."
                active_sessions[session_id]["progress"]["percent"] = 75
                
                answers_result = manager.generate_answers_from_mdx(mdx_filepath=enhanced_file)
                
                if answers_result.get("status") != "success":
                    raise Exception(f"Failed to generate answers: {answers_result.get('message')}")
            
            # Extract questions from the enhanced MDX file
            try:
                with open(enhanced_file or questions_file, 'r', encoding='utf-8') as f:
                    mdx_content = f.read()
                
                questions_from_mdx = manager._parse_questions_from_mdx(mdx_content)
                
                sheet_data = sheet_result.get("sheet_data", {})
                sheet_data["question_count"] = len(questions_from_mdx)
                sheet_data["questions"] = questions_from_mdx
                sheet_data["updated_at"] = datetime.now(timezone.utc).isoformat()
                
                active_sessions[session_id]["sheetData"] = sheet_data
            except Exception as e:
                active_sessions[session_id]["sheetData"] = sheet_result.get("sheet_data")
            
            # Update session with final status
            active_sessions[session_id]["status"] = "completed"
            active_sessions[session_id]["progress"]["percent"] = 100
            active_sessions[session_id]["progress"]["current_step"] = "Generation completed"
            active_sessions[session_id]["completedAt"] = datetime.now().isoformat()
            active_sessions[session_id]["outputFile"] = sheet_result.get("filepath")
            active_sessions[session_id]["progress"]["completed_questions"] = questions_result.get("questions_count", 0)
            
            # Cleanup temporary files
            for temp_file in [mock_mdx_file, questions_file, enhanced_file]:
                if temp_file and os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except Exception:
                        pass
            
            questions_count = questions_result.get("questions_count", 0)
            append_log(session_id, "generation_completed", {"topic": payload.topic, "questions": questions_count})
            
        except Exception as e:
            # Update session with error
            active_sessions[session_id]["status"] = "failed"
            active_sessions[session_id]["error"] = str(e)
            active_sessions[session_id]["progress"]["current_step"] = f"Failed: {str(e)}"
            active_sessions[session_id]["completedAt"] = datetime.now().isoformat()
            append_log(session_id, "generation_failed", {"error": str(e)})
    
    async def _bulk_generate_background(self, session_ids: List[str], payload: BulkGenerationRequest):
        """Background task to generate multiple topics."""
        tasks = []
        for i, (session_id, topic_data) in enumerate(zip(session_ids, payload.topics)):
            topic_payload = TopicGenerationRequest(
                topic=topic_data.name,
                agent_type=topic_data.agent_type,
                technology=topic_data.technology,
                question_count=topic_data.question_count,
                roadmap=topic_data.roadmap,
                difficulty=topic_data.difficulty,
                generate_answers=payload.generate_answers
            )
            task = self._generate_questions_background(session_id, topic_payload)
            tasks.append(task)
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    def list_sessions(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active/recent sessions."""
        sessions = list(active_sessions.values())
        
        if status:
            sessions = [s for s in sessions if s["status"] == status]
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x["startedAt"], reverse=True)
        
        return sessions
    
    def get_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Get progress for a specific session."""
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return active_sessions[session_id]
    
    def cancel_session(self, session_id: str) -> Dict[str, str]:
        """Cancel a running session."""
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        if session["status"] == "in_progress":
            session["status"] = "failed"
            session["error"] = "Cancelled by user"
            session["completedAt"] = datetime.now().isoformat()
            session["progress"]["current_step"] = "Cancelled"
            append_log(session_id, "session_cancelled", {})
        
        return {"message": "Session cancelled"}
    
    def retry_session(
        self,
        session_id: str,
        background_tasks: BackgroundTasks
    ) -> SessionResponse:
        """Retry a failed session."""
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        if session["status"] != "failed":
            raise HTTPException(status_code=400, detail="Can only retry failed sessions")
        
        # Create new session with same parameters
        new_session_id = self._create_session(
            topic=session["topic"],
            agent_type=session["agentType"],
            technology=session.get("technology"),
            roadmap=session["roadmap"],
            question_count=session["questionCount"]
        )
        
        # Create payload for retry
        from ...agents.interview.types import AnswerAgentType
        retry_payload = TopicGenerationRequest(
            topic=session["topic"],
            agent_type=AnswerAgentType(session["agentType"].upper()),
            technology=session.get("technology"),
            question_count=session["questionCount"],
            roadmap=session["roadmap"],
            difficulty="Medium",
            generate_answers=True
        )
        
        # Start background generation
        background_tasks.add_task(self._generate_questions_background, new_session_id, retry_payload)
        
        return SessionResponse(
            sessionId=new_session_id,
            message=f"Retrying generation for {session['topic']}"
        )
    
    def delete_session(self, session_id: str) -> Dict[str, str]:
        """Delete a session."""
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        del active_sessions[session_id]
        return {"message": "Session deleted"}
    
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

