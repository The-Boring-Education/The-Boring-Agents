"""Workflow nodes for quiz generation."""

from typing import Dict, Any
import logging

from src.agents.quiz.generators.metadata_generator import QuizMetadataGenerator
from src.agents.quiz.generators.question_generator import QuizQuestionGenerator
from src.agents.quiz.session.session_manager import QuizSessionManager
from src.agents.quiz.workflow.state import QuizWorkflowState
from src.agents.quiz.workflow.workflow_utils import (
    handle_node_errors,
    check_skip_condition,
    log_node_execution,
    get_progress_update,
)

logger = logging.getLogger(__name__)

@handle_node_errors("generate_questions", "failed")
def generate_questions_node(state: QuizWorkflowState) -> Dict[str, Any]:
    """Generate questions for the quiz."""
    session_id = state["session_id"]

    # Skip if already generated
    if check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0):
        log_node_execution("generate_questions", session_id, "skipping (already generated)")
        return {
            "status": "metadata_generating",
            "current_step": "Generating category metadata..."
        }
    
    log_node_execution("generate_questions", session_id)

    question_generator = QuizQuestionGenerator()
    questions = question_generator.generate_questions(
        topic=state["topic"],
        question_count=state["question_count"],
        difficulty=state["difficulty"],
        target_audience=state["target_audience"]
    )

    # Update session
    session_manager = QuizSessionManager()
    for question in questions:
        session_manager.add_question(session_id, question)

    session_manager.update_progress(
        session_id,
        completed=len(questions),
        total=state["question_count"],
        current_step=f"Generated {len(questions)} questions"
    )

    return {
        "questions": questions,
        "status": "metadata_generating",
        "current_step": "Generating category metadata...",
        "progress": get_progress_update(len(questions), state["question_count"], "Questions generated")
    }

@handle_node_errors("generate_metadata", "failed")
def generate_category_metadata_node(state: QuizWorkflowState) -> Dict[str, Any]:
    """Generate category metadata for the quiz."""
    session_id = state["session_id"]

    # Skip if already generated
    if check_skip_condition(state, "category_metadata"):
        log_node_execution("generate_category_metadata", session_id, "skipping (already generated)")
        return {
            "status": "finalizing",
            "current_step": "Finalizing quiz..."
        }
    
    log_node_execution("generate_category_metadata", session_id)

    metadata_generator = QuizMetadataGenerator()
    metadata = metadata_generator.generate_category_metadata(
        topic=state["topic"],
        question_count=len(state["questions"])
    )

    # Update session
    session_manager = QuizSessionManager()
    session_manager.set_category_metadata(session_id, metadata)
    
    return {
        "category_metadata": metadata,
        "status": "finalizing",
        "current_step": "Finalizing quiz..."
    }

def persist_state_node(state: QuizWorkflowState) -> Dict[str, Any]:
    """Persist state to session file."""
    session_id = state["session_id"]
    log_node_execution("persist_state", session_id)
    
    try:
        session_manager = QuizSessionManager()
        session_data = session_manager.get_session(session_id)
        
        if session_data:
            session_data.update({
                "status": state.get("status", session_data.get("status")),
                "questions": state.get("questions", session_data.get("questions", [])),
                "category_metadata": state.get("category_metadata", session_data.get("category_metadata")),
                "progress": state.get("progress", session_data.get("progress", {})),
                "output_file": state.get("output_file", session_data.get("output_file"))
            })
            
            session_manager.save_session(session_id, session_data)
        
        return {}  # No state changes, just persistence
    except Exception as e:
        logger.error(f"Error persisting state: {e}")
        return {}  # Don't fail workflow on persistence errors

@handle_node_errors("finalize", "failed")
def finalize_quiz_node(state: QuizWorkflowState) -> Dict[str, Any]:
    """Finalize quiz and create output JSON matching Quiz.ts schema."""
    session_id = state["session_id"]

    # Skip if already finalized
    if check_skip_condition(state, "output_file") and check_skip_condition(state, "quiz_data"):
        log_node_execution("finalize", session_id, "skipping (already finalized)")
        return {
            "status": "completed",
            "current_step": "Quiz completed"
        }

    log_node_execution("finalize", session_id)

    try:
        from datetime import datetime, timezone
        import json
        import os
        from src.core.config import config
        
        # Build final quiz data matching Quiz.ts schema
        quiz_data = {
            "categoryName": state["category_metadata"]["categoryName"],
            "categoryDescription": state["category_metadata"]["categoryDescription"],
            "categoryIcon": state["category_metadata"]["categoryIcon"],
            "questions": state["questions"],
            "isActive": True
        }
        
        # Save to output file
        output_dir = os.path.join(config.output_dir, "quizzes")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"quiz_{state['topic'].lower().replace(' ', '_')}.json"
        output_file = os.path.join(output_dir, output_filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(quiz_data, f, indent=2, ensure_ascii=False)
        
        # Update session
        session_manager = QuizSessionManager()
        from src.core.session.session_types import SessionStatus
        session_manager.set_output_file(session_id, output_file, quiz_data)
        session_manager.update_status(
            session_id,
            SessionStatus.COMPLETED,
            current_step="Quiz finalized and saved"
        )
        
        return {
            "quiz_data": quiz_data,
            "output_file": output_file,
            "status": "completed",
            "current_step": "Quiz completed successfully"
        }
    except Exception as e:
        logger.error(f"Error finalizing quiz: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "current_step": f"Failed: {str(e)}"
        }
        