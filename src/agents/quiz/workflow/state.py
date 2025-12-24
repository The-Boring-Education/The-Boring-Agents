from typing import TypedDict, List, Dict, Any, Optional

class QuizWorkflowState(TypedDict):
    """State schema for quiz generation workflow."""

    # Session information
    session_id: str
    topic: str  # Quiz topic (e.g., "React.js")
    description: str
    agent_type: str  # "generic", "tech", "dsa", "conceptual"
    question_count: int
    target_audience: str  # "developers", "beginners", etc.
    difficulty: str  # "easy", "medium", "hard"

    # Status tracking
    status: str  # pending, in_progress, completed, failed
    current_step: str
    error: Optional[str]

    # Generated content
    category_metadata: Optional[Dict[str, Any]]
    questions: List[Dict[str, Any]]

    # Progress tracking
    progress: Dict[str, Any]

    # Output
    output_file: Optional[str]
    quiz_data: Optional[Dict[str, Any]]