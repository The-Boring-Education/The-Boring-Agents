"""State schema for LangGraph workflow."""

from typing import TypedDict, List, Dict, Any, Optional


class InterviewWorkflowState(TypedDict):
    """State schema for interview sheet generation workflow."""
    
    # Session information
    session_id: str
    name: str
    description: str
    agent_type: str
    roadmap: str
    
    # Status tracking
    status: str  # pending, metadata_generating, questions_generating, answers_generating, completed, failed
    current_step: str
    error: Optional[str]
    
    # Generated content
    meta: Optional[str]
    questions: List[Dict[str, Any]]  # List of question dicts with title, question, answer, frequency, priority, companyTypes
    question_texts: List[str]  # Raw question texts before metadata is added
    
    # Progress tracking
    progress: Dict[str, Any]
    
    # Output
    output_file: Optional[str]
    sheet_data: Optional[Dict[str, Any]]  # Final sheet data matching Mongoose schema

