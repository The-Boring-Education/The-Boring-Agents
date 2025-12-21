from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional, List, Dict, Any
import uuid
import asyncio
import json
import os
from datetime import datetime, timezone

from ..agents.interview.interview_sheet_manager import InterviewSheetManager
from ..agents.interview.types import AnswerAgentType
from ..core.config import config
from ..utils.session_logger import append_log, read_logs


# Session management
active_sessions: Dict[str, Dict[str, Any]] = {}


class GenerateInterviewSheetRequest(BaseModel):
    mdx_file: str = Field(..., description="Path to MDX requirements or questions file")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.GENERIC)
    technology: Optional[str] = Field(default=None)
    save: bool = Field(default=True)


class TopicGenerationRequest(BaseModel):
    """Request payload for single-topic generation."""

    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(..., description="Topic name to generate questions for")
    agent_type: AnswerAgentType = Field(default=AnswerAgentType.TECH, alias="agentType")
    technology: Optional[str] = Field(default=None)
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    roadmap: str = Field(default="Tech")
    difficulty: str = Field(default="Medium")
    generate_answers: bool = Field(default=True, alias="generateAnswers")

    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class BulkTopicRequest(BaseModel):
    """Topic definition for bulk generation."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    agent_type: AnswerAgentType = Field(alias="agentType")
    technology: Optional[str] = None
    question_count: int = Field(default=20, ge=1, le=100, alias="questionCount")
    roadmap: str = Field(default="Tech")
    difficulty: str = Field(default="Medium")

    @field_validator("agent_type", mode="before")
    @classmethod
    def _normalize_agent_type(cls, value):
        if isinstance(value, str):
            return value.lower()
        return value


class BulkGenerationRequest(BaseModel):
    """Request payload for bulk topic generation."""

    model_config = ConfigDict(populate_by_name=True)

    topics: List[BulkTopicRequest]
    generate_answers: bool = Field(default=True, alias="generateAnswers")
    auto_publish: bool = Field(default=False, alias="autoPublish")


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


# ==================== NEW MODELS FOR QUESTION MANAGEMENT ====================

class InterviewQuestion(BaseModel):
    """Single interview question with all metadata."""
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique question ID")
    question: str = Field(..., description="The actual question text")
    difficulty: str = Field(default="Medium", description="Easy, Medium, Hard, or Intermediate")
    category: Optional[str] = Field(default=None, description="Topic category")
    answer: Optional[str] = Field(default=None, description="Full answer with explanation")
    # explanation: Optional[str] = Field(default=None, description="Additional explanation")
    frequency: Optional[str] = Field(default="Asked Sometimes", description="How frequently asked: Most Asked, Asked Frequently, Asked Sometimes")
    priority: Optional[str] = Field(default="Medium", description="Priority level: High, Medium, Low")
    company_types: Optional[List[str]] = Field(
        default=["Startup", "MNC"], 
        description="Relevant company types: Startup, MidSize, MNC, FAANG")
    followup_questions: Optional[List[str]] = Field(default=None, description="Related follow-up questions")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class UpdateQuestionRequest(BaseModel):
    """Request model for updating a single question."""
    
    question: Optional[str] = Field(default=None, description="Updated question text")
    difficulty: Optional[str] = Field(default=None, description="Updated difficulty level")
    category: Optional[str] = Field(default=None, description="Updated category")
    answer: Optional[str] = Field(default=None, description="Updated answer")
    # explanation: Optional[str] = Field(default=None, description="Updated explanation")
    followup_questions: Optional[List[str]] = Field(default=None, description="Updated follow-up questions")
    frequency: Optional[str] = Field(default=None, description="Updated frequency")
    priority: Optional[str] = Field(default=None, description="Updated priority")


class QuestionManagementResponse(BaseModel):
    """Standard response for question management operations."""
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class PaginatedQuestionsResponse(BaseModel):
    """Paginated questions response."""
    
    total: int = Field(..., description="Total questions in sheet")
    skip: int = Field(..., description="Skip count")
    limit: int = Field(..., description="Limit per page")
    count: int = Field(..., description="Questions in this page")
    questions: List[Dict[str, Any]] = Field(..., description="Paginated questions")



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
        # Log the received payload
        print(f"🔍 DEBUG: Received request - Topic: {payload.topic}, Question Count: {payload.question_count}")
        append_log(session_id, "request_received", {
            "topic": payload.topic, 
            "question_count": payload.question_count,
            "agent_type": payload.agent_type.value
        })
        
        # Update session status
        active_sessions[session_id]["status"] = "in_progress"
        active_sessions[session_id]["progress"]["current_step"] = "Starting question generation..."
        
        # Use the agent type directly (already an enum)
        agent_type_enum = payload.agent_type
        
        # Initialize manager
        manager_kwargs = {}
        if payload.technology and payload.agent_type == AnswerAgentType.TECH:
            manager_kwargs["technology"] = payload.technology
            
        manager = InterviewSheetManager(agent_type=agent_type_enum, **manager_kwargs)
        
        # Update progress
        active_sessions[session_id]["progress"]["current_step"] = "Generating questions..."
        active_sessions[session_id]["progress"]["percent"] = 10
        
        # Create a mock MDX file for topic-based generation
        print(f"🔍 DEBUG: Creating MDX with question_count={payload.question_count}")
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
        
        # Step 3: Add metadata to questions (required for answer generation)
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
        
        # Extract questions from the enhanced MDX file to include in sheetData
        try:
            with open(enhanced_file or questions_file, 'r', encoding='utf-8') as f:
                mdx_content = f.read()
            
            # Parse questions from MDX to populate sheetData
            questions_from_mdx = manager._parse_questions_from_mdx(mdx_content)
            print(f"🔍 DEBUG: Parsed {len(questions_from_mdx)} questions from MDX")
            
            # Update sheetData with generated questions
            sheet_data = sheet_result.get("sheet_data", {})
            sheet_data["question_count"] = len(questions_from_mdx)
            sheet_data["questions"] = questions_from_mdx
            sheet_data["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            active_sessions[session_id]["sheetData"] = sheet_data
            print(f"✅ Updated sheetData with {len(questions_from_mdx)} questions")
        except Exception as e:
            print(f"⚠️ Warning: Could not extract questions for sheetData: {str(e)}")
            # Still return the sheet, just without questions populated in the response
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
                    print(f"✅ Cleaned up temp file: {temp_file}")
                except Exception as e:
                    print(f"⚠️ Failed to cleanup temp file {temp_file}: {str(e)}")
            
        append_log(session_id, "generation_completed", {"topic": payload.topic, "questions": questions_result.get("questions_count", 0)})
        
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
            agent_type=topic_data.agent_type,
            technology=topic_data.technology,
            question_count=topic_data.question_count,
            roadmap=topic_data.roadmap,
            difficulty=topic_data.difficulty,
            generate_answers=payload.generate_answers
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
        agent_type=payload.agent_type.value,
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
            agent_type=topic_data.agent_type.value,
            technology=topic_data.technology,
            roadmap=topic_data.roadmap,
            question_count=topic_data.question_count
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


# ==================== NEW ENDPOINTS FOR QUESTION MANAGEMENT ====================

@router.get("/session/{session_id}/sheet")
def get_session_sheet(session_id: str):
    """
    Retrieve the complete interview sheet for a session.
    
    Returns the sheet with all questions for frontend display and editing.
    This is called after generation completes to load questions into the editor.
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    sheet_data = session.get("sheetData", {})
    
    if not sheet_data:
        raise HTTPException(status_code=404, detail="Sheet data not found for session")
    
    return sheet_data


@router.get("/session/{session_id}/questions", response_model=PaginatedQuestionsResponse)
def get_session_questions(session_id: str, skip: int = 0, limit: int = 100):
    """
    Get paginated list of questions from a session.
    
    Useful for infinite scroll or pagination in the UI.
    
    Query Parameters:
    - skip: Number of questions to skip (default: 0)
    - limit: Number of questions to return (default: 100)
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sheet_data = active_sessions[session_id].get("sheetData", {})
    questions = sheet_data.get("questions", [])
    
    paginated = questions[skip : skip + limit]
    
    return PaginatedQuestionsResponse(
        total=len(questions),
        skip=skip,
        limit=limit,
        count=len(paginated),
        questions=paginated
    )


@router.get("/session/{session_id}/questions/{question_id}")
def get_question(session_id: str, question_id: str):
    """
    Get a specific question by ID from a session.
    
    Used when editing a single question in a modal or separate editor.
    
    Path Parameters:
    - session_id: Session ID
    - question_id: Question ID
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sheet_data = active_sessions[session_id].get("sheetData", {})
    questions = sheet_data.get("questions", [])
    
    question = next((q for q in questions if q.get("id") == question_id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    return question


@router.put("/session/{session_id}/questions/{question_id}", response_model=QuestionManagementResponse)
def update_question(session_id: str, question_id: str, update: UpdateQuestionRequest):
    """
    Update a specific question in the session.
    
    Modifies question in memory. Changes persist only until session ends.
    To save permanently, export and send to MongoDB API.
    
    Path Parameters:
    - session_id: Session ID
    - question_id: Question ID to update
    
    Request Body: UpdateQuestionRequest (partial update - only provide fields to change)
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sheet_data = active_sessions[session_id].get("sheetData", {})
    questions = sheet_data.get("questions", [])
    
    question_index = next(
        (i for i, q in enumerate(questions) if q.get("id") == question_id),
        None
    )
    
    if question_index is None:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = questions[question_index]
    
    # Update only provided fields
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            question[field] = value
    
    # Update timestamp
    question["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Update in session
    questions[question_index] = question
    sheet_data["questions"] = questions
    sheet_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    active_sessions[session_id]["sheetData"] = sheet_data
    
    append_log(session_id, "question_updated", {"question_id": question_id})
    
    return QuestionManagementResponse(
        success=True,
        message=f"Question updated successfully",
        data={"question": question}
    )


@router.delete("/session/{session_id}/questions/{question_id}", response_model=QuestionManagementResponse)
def delete_question(session_id: str, question_id: str):
    """
    Delete a specific question from the session.
    
    Removes question from memory. Changes persist only until session ends.
    To save permanently, export and send to MongoDB API.
    
    Path Parameters:
    - session_id: Session ID
    - question_id: Question ID to delete
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sheet_data = active_sessions[session_id].get("sheetData", {})
    questions = sheet_data.get("questions", [])
    
    initial_count = len(questions)
    questions = [q for q in questions if q.get("id") != question_id]
    final_count = len(questions)
    
    if initial_count == final_count:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Update sheet data
    sheet_data["questions"] = questions
    sheet_data["question_count"] = final_count
    sheet_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    active_sessions[session_id]["sheetData"] = sheet_data
    
    append_log(session_id, "question_deleted", {
        "question_id": question_id,
        "remaining_questions": final_count
    })
    
    return QuestionManagementResponse(
        success=True,
        message=f"Question deleted successfully. Remaining: {final_count}",
        data={"remaining_questions": final_count, "question_count": final_count}
    )


@router.post("/session/{session_id}/questions", response_model=QuestionManagementResponse)
def add_question(session_id: str, question: InterviewQuestion):
    """
    Add a new question to the session.
    
    Allows users to manually add new questions to the sheet.
    Changes persist only until session ends.
    To save permanently, export and send to MongoDB API.
    
    Path Parameters:
    - session_id: Session ID
    
    Request Body: InterviewQuestion object
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sheet_data = active_sessions[session_id].get("sheetData", {})
    questions = sheet_data.get("questions", [])
    
    # Ensure question has unique ID
    if not question.id:
        question.id = str(uuid.uuid4())
    
    question_dict = question.dict()
    question_dict["created_at"] = datetime.now(timezone.utc).isoformat()
    question_dict["updated_at"] = question_dict["created_at"]
    
    questions.append(question_dict)
    
    # Update sheet data
    sheet_data["questions"] = questions
    sheet_data["question_count"] = len(questions)
    sheet_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    active_sessions[session_id]["sheetData"] = sheet_data
    
    append_log(session_id, "question_added", {"question_id": question.id})
    
    return QuestionManagementResponse(
        success=True,
        message=f"Question added successfully",
        data={"question": question_dict, "total_questions": len(questions)}
    )


@router.post("/session/{session_id}/sheet", response_model=QuestionManagementResponse)
def save_sheet_locally(session_id: str):
    """
    Save the current sheet to local JSON file.
    
    Useful for backup or exporting to external MongoDB API.
    File is saved to output/ directory with session_id in filename.
    
    Path Parameters:
    - session_id: Session ID
    """
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    sheet_data = active_sessions[session_id].get("sheetData", {})
    
    if not sheet_data:
        raise HTTPException(status_code=404, detail="No sheet data available")
    
    try:
        # Create backup filename
        topic = sheet_data.get("topic", "interview_sheet").replace(" ", "_").lower()
        filename = f"sheet_{topic}_{session_id}.json"
        filepath = os.path.join(config.output_dir, filename)
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sheet_data, f, indent=2, ensure_ascii=False)
        
        append_log(session_id, "sheet_saved_locally", {"filepath": filepath})
        
        return QuestionManagementResponse(
            success=True,
            message=f"Sheet saved to {filepath}",
            data={
                "filepath": filepath,
                "filename": filename,
                "question_count": len(sheet_data.get("questions", [])),
                "sheet_id": sheet_data.get("id")
            }
        )
        
    except Exception as e:
        append_log(session_id, "sheet_save_failed", {"error": str(e)})
        raise HTTPException(status_code=500, detail=f"Failed to save sheet: {str(e)}")


# ==================== END QUESTION MANAGEMENT ENDPOINTS ====================


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

