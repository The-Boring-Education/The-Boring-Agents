"""Workflow nodes for interview sheet generation."""

from typing import Dict, Any
import logging

from src.agents.interview.workflow.state import InterviewWorkflowState
from src.agents.interview.common.metadata_generator import MetadataGenerator
from src.agents.interview.common.question_generator import QuestionGenerator
from src.agents.interview.common.workflow_utils import (
    handle_node_errors,
    check_skip_condition,
    log_node_execution,
    get_progress_update,
    create_error_state
)
from src.agents.interview.common.state_utils import (
    get_questions_needing_answers,
    count_completed_answers,
    normalize_question_metadata
)
from src.agents.interview.generators.base_generator import BaseAnswerGenerator
from src.agents.interview.generators.generic_generator import GenericAnswerGenerator
from src.agents.interview.generators.dsa_generator import DSAAnswerGenerator
from src.agents.interview.generators.tech_generator import TechAnswerGenerator
from src.agents.interview.generators.system_design_generator import SystemDesignAnswerGenerator
from src.agents.interview.types import AnswerAgentType
from src.agents.interview.session.session_manager import InterviewSessionManager
from src.core.config import config

logger = logging.getLogger(__name__)


@handle_node_errors("generate_metadata", "failed")
def generate_metadata_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    """Generate metadata for the interview sheet.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with metadata
    """
    session_id = state["session_id"]
    
    # Skip if already generated
    if check_skip_condition(state, "meta"):
        log_node_execution("generate_metadata", session_id, "skipping (already generated)")
        return {
            "status": "questions_generating",
            "current_step": "Generating questions..."
        }
    
    log_node_execution("generate_metadata", session_id)
    
    metadata_gen = MetadataGenerator()
    meta = metadata_gen.generate_sheet_meta(
        name=state["name"],
        description=state["description"],
        roadmap=state["roadmap"]
    )
    
    # Update session
    session_manager = InterviewSessionManager()
    session_manager.set_meta(session_id, meta)
    
    return {
        "meta": meta,
        "status": "questions_generating",
        "current_step": "Generating questions..."
    }


@handle_node_errors("generate_questions", "failed")
def generate_questions_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    """Generate questions for the interview sheet.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with questions
    """
    session_id = state["session_id"]
    
    # Skip if already generated
    if check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0):
        log_node_execution("generate_questions", session_id, "skipping (already generated)")
        questions = state.get("questions", [])
        return {
            "status": "answers_generating",
            "current_step": "Generating answers...",
            "progress": get_progress_update(0, len(questions), "Generating answers...")
        }
    
    log_node_execution("generate_questions", session_id)
    
    question_gen = QuestionGenerator()
    question_texts = question_gen.generate_questions(
        name=state["name"],
        description=state["description"],
        agent_type=state["agent_type"],
        question_count=state.get("question_count", 20),
        roadmap=state["roadmap"]
    )
    
    # Generate metadata for each question
    metadata_gen = MetadataGenerator()
    questions = []
    
    for question_text in question_texts:
        # Generate metadata
        metadata = metadata_gen.generate_question_metadata(
            question=question_text,
            topic=state["name"],
            context=state["description"]
        )
        
        # Create question dict with normalized metadata
        question = normalize_question_metadata({
            "title": question_text[:100],  # Max 100 chars
            "question": question_text,
            "answer": "",  # Will be filled in next step
            "frequency": metadata["frequency"],
            "priority": metadata["priority"],
            "companyTypes": metadata["companyTypes"]
        })
        questions.append(question)
    
    # Update session
    session_manager = InterviewSessionManager()
    for question in questions:
        session_manager.add_question(session_id, question)
    session_manager.update_progress(
        session_id,
        completed=0,
        total=len(questions),
        current_step="Questions generated, ready for answers"
    )
    
    return {
        "questions": questions,
        "question_texts": question_texts,
        "status": "answers_generating",
        "current_step": "Generating answers...",
        "progress": get_progress_update(0, len(questions), "Generating answers...")
    }


@handle_node_errors("generate_answers", "failed")
def generate_answers_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    """Generate answers for all questions.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with answers
    """
    session_id = state["session_id"]
    questions = state.get("questions", [])
    
    if not questions:
        logger.warning(f"No questions found for session {session_id}")
        return create_error_state("No questions to generate answers for", "failed")
    
    # Check which questions need answers
    questions_needing_answers = get_questions_needing_answers(questions)
    
    if not questions_needing_answers:
        log_node_execution("generate_answers", session_id, "skipping (all answers generated)")
        return {
            "status": "finalizing",
            "current_step": "Finalizing sheet...",
            "progress": get_progress_update(len(questions), len(questions), "All answers generated")
        }
    
    log_node_execution("generate_answers", session_id, f"generating {len(questions_needing_answers)} answers")
    
    # Get appropriate generator
    session_manager = InterviewSessionManager()
    session_data = session_manager.get_session(session_id)
    technology = session_data.get("technology") if session_data else None
    generator = _get_answer_generator(state["agent_type"], technology)
    
    # Generate answer for each question that needs one
    completed_count = count_completed_answers(questions)
    
    for question in questions_needing_answers:
        question_index = questions.index(question)
        logger.info(f"Generating answer {question_index + 1}/{len(questions)}")
        
        answer_result = generator.generate_answer(
            question=question["question"],
            topic=state["name"],
            difficulty="Medium",  # Can be enhanced to detect difficulty
            frequency=question["frequency"],
            priority=question["priority"],
            company_types=question["companyTypes"]
        )
        
        # Handle structured response
        if hasattr(answer_result, 'answer'):  # Check if it's an object with 'answer' attribute (like InterviewQuestionResponse)
            question["answer"] = answer_result.answer
            
            # Convert resources to dicts if they are objects
            resources = getattr(answer_result, 'resources', [])
            question["resources"] = [
                res.model_dump() if hasattr(res, 'model_dump') else res 
                for res in resources
            ]
            
            # Update metadata if provided in answer
            if getattr(answer_result, 'company_types', None):
                question["companyTypes"] = answer_result.company_types
            if getattr(answer_result, 'difficulty', None):
                question["difficulty"] = answer_result.difficulty
            if getattr(answer_result, 'frequency', None):
                question["frequency"] = answer_result.frequency
            if getattr(answer_result, 'priority', None):
                question["priority"] = answer_result.priority
        else:
            # Legacy string response
            question["answer"] = str(answer_result)
        
        completed_count += 1
        
        # Update session after each answer
        session_manager.update_progress(
            session_id,
            completed=completed_count,
            total=len(questions),
            current_step=f"Generated answer {completed_count}/{len(questions)}"
        )
    
    return {
        "questions": questions,
        "status": "finalizing",
        "current_step": "Finalizing sheet...",
        "progress": get_progress_update(len(questions), len(questions), "All answers generated")
    }


def persist_state_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    """Persist state to session file.
    
    Args:
        state: Current workflow state
        
    Returns:
        State (unchanged, just persisted)
    """
    session_id = state["session_id"]
    log_node_execution("persist_state", session_id)
    
    try:
        session_manager = InterviewSessionManager()
        session_data = session_manager.get_session(session_id)
        
        if session_data:
            # Update session data with current state
            session_data.update({
                "status": state.get("status", session_data.get("status")),
                "meta": state.get("meta", session_data.get("meta")),
                "questions": state.get("questions", session_data.get("questions", [])),
                "progress": state.get("progress", session_data.get("progress", {})),
                "output_file": state.get("output_file", session_data.get("output_file"))
            })
            
            session_manager.save_session(session_id, session_data)
        
        return {}  # No state changes, just persistence
    except Exception as e:
        logger.error(f"Error persisting state: {e}")
        return {}  # Don't fail workflow on persistence errors


@handle_node_errors("finalize", "failed")
def finalize_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    """Finalize sheet and create output JSON.
    
    Args:
        state: Current workflow state
        
    Returns:
        Updated state with final sheet data and output file
    """
    session_id = state["session_id"]
    
    # Skip if already finalized
    if check_skip_condition(state, "output_file") and check_skip_condition(state, "sheet_data"):
        log_node_execution("finalize", session_id, "skipping (already finalized)")
        return {
            "status": "completed",
            "current_step": "Sheet completed"
        }
    
    log_node_execution("finalize", session_id)
    
    try:
        from datetime import datetime, timezone
        from ..common.schema_utils import (
            generate_slug,
            generate_cover_image_url,
            get_schema_defaults,
            validate_sheet_structure
        )
        import json
        import os
        
        # Build final sheet data matching Mongoose schema
        defaults = get_schema_defaults()
        sheet_data = {
            "name": state["name"],
            "slug": generate_slug(state["name"]),
            "description": state["description"],
            "meta": state.get("meta", ""),
            "coverImageURL": generate_cover_image_url(state["name"]),
            "liveOn": datetime.now(timezone.utc).isoformat(),
            "roadmap": state["roadmap"],
            "isPremium": defaults["isPremium"],
            "price": defaults["price"],
            "discountPercentage": defaults["discountPercentage"],
            "appliedCoupon": defaults["appliedCoupon"],
            "features": defaults["features"],
            "questions": state["questions"]
        }
        
        # Validate structure
        is_valid, errors = validate_sheet_structure(sheet_data)
        if not is_valid:
            logger.warning(f"Sheet structure validation errors: {errors}")
            # Continue anyway, but log warnings
        
        # Save to output file
        output_dir = os.path.join(config.output_dir, "interview_sheets")
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"{generate_slug(state['name'])}.json"
        output_file = os.path.join(output_dir, output_filename)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sheet_data, f, indent=2, ensure_ascii=False)
        
        # Update session
        session_manager = InterviewSessionManager()
        from src.core.session.session_types import SessionStatus
        session_manager.set_output_file(state["session_id"], output_file, sheet_data)
        session_manager.update_status(
            state["session_id"],
            SessionStatus.COMPLETED,
            current_step="Sheet finalized and saved"
        )
        
        return {
            "sheet_data": sheet_data,
            "output_file": output_file,
            "status": "completed",
            "current_step": "Sheet completed successfully"
        }
    except Exception as e:
        logger.error(f"Error finalizing sheet: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "current_step": f"Failed: {str(e)}"
        }


def _get_answer_generator(agent_type: str, technology: str = None) -> BaseAnswerGenerator:
    """Get the appropriate answer generator for the agent type.
    
    Args:
        agent_type: Agent type string
        technology: Optional technology name for tech generator
        
    Returns:
        Answer generator instance
    """
    agent_type_enum = AnswerAgentType(agent_type.lower())
    
    if agent_type_enum == AnswerAgentType.GENERIC:
        return GenericAnswerGenerator()
    elif agent_type_enum == AnswerAgentType.DSA:
        return DSAAnswerGenerator()
    elif agent_type_enum == AnswerAgentType.TECH:
        return TechAnswerGenerator(technology=technology)
    elif agent_type_enum == AnswerAgentType.SYSTEM_DESIGN:
        return SystemDesignAnswerGenerator()
    else:
        return GenericAnswerGenerator()

