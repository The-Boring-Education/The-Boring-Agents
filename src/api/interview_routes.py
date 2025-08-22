from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
import asyncio
import json
import os
from datetime import datetime

from ..agents.interview.interview_sheet_manager import InterviewSheetManager
from ..agents.interview.types import AnswerAgentType
from ..core.config import config
from ..utils.session_logger import append_log, get_session_logs


# Session management
active_sessions: Dict[str, Dict[str, Any]] = {}


class GenerateInterviewSheetRequest(BaseModel):
    mdx_file: str = Field(..., description="Path to MDX requirements or questions file")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.GENERIC)
    technology: Optional[str] = Field(default=None)
    save: bool = Field(default=True)


class TopicGenerationRequest(BaseModel):
    topic: str = Field(..., description="Topic name to generate questions for")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.TECH)
    technology: Optional[str] = Field(default=None)
    question_count: int = Field(default=20, ge=5, le=100)
    roadmap: str = Field(default="Tech")
    difficulty: str = Field(default="Medium")
    generate_answers: bool = Field(default=True)


class BulkTopicRequest(BaseModel):
    name: str
    agentType: str
    technology: Optional[str] = None
    questionCount: int = Field(default=20, ge=5, le=100)
    roadmap: str = Field(default="Tech")
    difficulty: str = Field(default="Medium")


class BulkGenerationRequest(BaseModel):
    topics: List[BulkTopicRequest]
    generateAnswers: bool = Field(default=True)
    autoPublish: bool = Field(default=False)


class InterviewGenerationSession(BaseModel):
    sessionId: str
    topic: str
    agentType: str
    technology: Optional[str] = None
    roadmap: str
    questionCount: int
    status: str  # pending, in_progress, completed, failed
    progress: Dict[str, Any]
    startedAt: str
    completedAt: Optional[str] = None
    outputFile: Optional[str] = None
    sheetData: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class InterviewSheetResponse(BaseModel):
    ok: bool
    message: str
    output_file: Optional[str] = None
    sheet: Optional[dict] = None


class SessionResponse(BaseModel):
    sessionId: str
    message: str


class TopicTemplate(BaseModel):
    name: str
    description: str
    agentTypes: List[str]
    suggestedQuestionCount: int
    difficulty: str
    roadmaps: List[str]
    category: Optional[str] = None
    tags: Optional[List[str]] = None


class RoadmapSuggestion(BaseModel):
    name: str
    description: str
    topics: List[str]
    technologies: List[str]
    difficulty: str
    estimatedTime: Optional[str] = None


router = APIRouter(prefix="/interview", tags=["interview"])


# Helper functions
def create_session(topic: str, agent_type: str, **kwargs) -> str:
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


async def generate_questions_background(session_id: str, payload: TopicGenerationRequest):
    """Background task to generate questions for a topic"""
    try:
        # Update session status
        active_sessions[session_id]["status"] = "in_progress"
        active_sessions[session_id]["progress"]["current_step"] = "Starting question generation..."
        
        # Convert agent type string to enum
        agent_type_map = {
            "tech": AnswerAgentType.TECH,
            "dsa": AnswerAgentType.DSA,
            "generic": AnswerAgentType.GENERIC,
            "system_design": AnswerAgentType.SYSTEM_DESIGN
        }
        agent_type_enum = agent_type_map.get(payload.agent_type.lower(), AnswerAgentType.TECH)
        
        # Initialize manager
        manager_kwargs = {}
        if payload.technology and payload.agent_type.lower() == "tech":
            manager_kwargs["technology"] = payload.technology
            
        manager = InterviewSheetManager(agent_type=agent_type_enum, **manager_kwargs)
        
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
        
        # Generate the sheet
        active_sessions[session_id]["progress"]["current_step"] = "Processing with AI agents..."
        active_sessions[session_id]["progress"]["percent"] = 30
        
        result = manager.create_sheet_from_mdx(mdx_filepath=mock_mdx_file)
        
        # Update session with results
        active_sessions[session_id]["status"] = "completed"
        active_sessions[session_id]["progress"]["percent"] = 100
        active_sessions[session_id]["progress"]["current_step"] = "Generation completed"
        active_sessions[session_id]["completedAt"] = datetime.now().isoformat()
        active_sessions[session_id]["outputFile"] = result.get("output_file")
        active_sessions[session_id]["sheetData"] = result.get("sheet")
        
        # Cleanup mock file
        if os.path.exists(mock_mdx_file):
            os.remove(mock_mdx_file)
            
        append_log(session_id, "generation_completed", {"topic": payload.topic, "questions": len(result.get("sheet", {}).get("questions", []))})
        
    except Exception as e:
        # Update session with error
        active_sessions[session_id]["status"] = "failed"
        active_sessions[session_id]["error"] = str(e)
        active_sessions[session_id]["progress"]["current_step"] = f"Failed: {str(e)}"
        active_sessions[session_id]["completedAt"] = datetime.now().isoformat()
        append_log(session_id, "generation_failed", {"error": str(e)})


async def bulk_generate_background(session_ids: List[str], payload: BulkGenerationRequest):
    """Background task to generate multiple topics"""
    tasks = []
    for i, (session_id, topic_data) in enumerate(zip(session_ids, payload.topics)):
        topic_payload = TopicGenerationRequest(
            topic=topic_data.name,
            agent_type=AnswerAgentType(topic_data.agentType.upper()),
            technology=topic_data.technology,
            question_count=topic_data.questionCount,
            roadmap=topic_data.roadmap,
            difficulty=topic_data.difficulty,
            generate_answers=payload.generateAnswers
        )
        task = generate_questions_background(session_id, topic_payload)
        tasks.append(task)
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks, return_exceptions=True)


# API Routes

@router.post("/create-sheet", response_model=InterviewSheetResponse)
def create_sheet(payload: GenerateInterviewSheetRequest):
    """Legacy endpoint for MDX-based sheet creation"""
    manager = InterviewSheetManager(agent_type=payload.agent_type)
    try:
        result = manager.create_sheet_from_mdx(mdx_filepath=payload.mdx_file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    output_file = result.get("output_file") if payload.save else None
    return InterviewSheetResponse(
        ok=True,
        message="Interview sheet created",
        output_file=output_file,
        sheet=result.get("sheet"),
    )


@router.post("/generate-topic", response_model=SessionResponse)
async def generate_topic(payload: TopicGenerationRequest, background_tasks: BackgroundTasks):
    """Generate questions for a single topic"""
    session_id = create_session(
        topic=payload.topic,
        agent_type=payload.agent_type,
        technology=payload.technology,
        roadmap=payload.roadmap,
        question_count=payload.question_count
    )
    
    # Start background generation
    background_tasks.add_task(generate_questions_background, session_id, payload)
    
    return SessionResponse(
        sessionId=session_id,
        message=f"Started generating {payload.question_count} questions for {payload.topic}"
    )


@router.post("/bulk-generate")
async def bulk_generate(payload: BulkGenerationRequest, background_tasks: BackgroundTasks):
    """Start bulk generation for multiple topics"""
    session_ids = []
    
    for topic_data in payload.topics:
        session_id = create_session(
            topic=topic_data.name,
            agent_type=topic_data.agentType,
            technology=topic_data.technology,
            roadmap=topic_data.roadmap,
            question_count=topic_data.questionCount
        )
        session_ids.append(session_id)
    
    # Start background bulk generation
    background_tasks.add_task(bulk_generate_background, session_ids, payload)
    
    return {
        "sessionIds": session_ids,
        "message": f"Started bulk generation for {len(payload.topics)} topics"
    }


@router.get("/sessions")
def list_sessions(status: Optional[str] = None):
    """List all active/recent sessions"""
    sessions = list(active_sessions.values())
    
    if status:
        sessions = [s for s in sessions if s["status"] == status]
    
    # Sort by start time (newest first)
    sessions.sort(key=lambda x: x["startedAt"], reverse=True)
    
    return sessions


@router.get("/session/{session_id}/progress")
def get_session_progress(session_id: str):
    """Get progress for a specific session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return active_sessions[session_id]


@router.post("/session/{session_id}/cancel")
def cancel_session(session_id: str):
    """Cancel a running session"""
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


@router.post("/session/{session_id}/retry")
async def retry_session(session_id: str, background_tasks: BackgroundTasks):
    """Retry a failed session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    if session["status"] != "failed":
        raise HTTPException(status_code=400, detail="Can only retry failed sessions")
    
    # Create new session with same parameters
    new_session_id = create_session(
        topic=session["topic"],
        agent_type=session["agentType"],
        technology=session.get("technology"),
        roadmap=session["roadmap"],
        question_count=session["questionCount"]
    )
    
    # Create payload for retry
    retry_payload = TopicGenerationRequest(
        topic=session["topic"],
        agent_type=AnswerAgentType(session["agentType"].upper()),
        technology=session.get("technology"),
        question_count=session["questionCount"],
        roadmap=session["roadmap"],
        difficulty="Medium",  # Default for retry
        generate_answers=True
    )
    
    # Start background generation
    background_tasks.add_task(generate_questions_background, new_session_id, retry_payload)
    
    return SessionResponse(
        sessionId=new_session_id,
        message=f"Retrying generation for {session['topic']}"
    )


@router.get("/topic-templates")
def get_topic_templates():
    """Get available topic templates"""
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
    return templates


@router.get("/roadmap-suggestions")
def get_roadmap_suggestions():
    """Get roadmap suggestions"""
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
    return roadmaps


@router.delete("/session/{session_id}")
def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del active_sessions[session_id]
    return {"message": "Session deleted"}

