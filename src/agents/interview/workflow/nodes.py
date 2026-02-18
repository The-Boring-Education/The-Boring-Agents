"""Workflow nodes for interview sheet generation.

Each node is a pure function that receives InterviewWorkflowState and returns
a partial state update dict. Session persistence is handled via a shared
session manager obtained through _get_session_manager().
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Dict, Any

from src.core.config import config
from src.core.session.session_types import SessionStatus
from src.core.workflow.workflow_utils import (
    handle_node_errors,
    check_skip_condition,
    log_node_execution,
    get_progress_update,
    create_error_state,
)
from src.agents.interview.workflow.state import (
    InterviewWorkflowState,
    get_questions_needing_answers,
    count_completed_answers,
    normalize_question_metadata,
)
from src.agents.interview.common.metadata_generator import MetadataGenerator
from src.agents.interview.common.question_generator import QuestionGenerator
from src.agents.interview.common.schema_utils import (
    generate_slug,
    generate_cover_image_url,
    get_schema_defaults,
    validate_sheet_structure,
)
from src.agents.interview.generators import get_generator

logger = logging.getLogger(__name__)

# Lazy singleton so nodes don't each create a fresh manager.
_session_manager = None


def _get_session_manager():
    global _session_manager
    if _session_manager is None:
        from src.agents.interview.session.session_manager import InterviewSessionManager
        _session_manager = InterviewSessionManager()
    return _session_manager


# ---------------------------------------------------------------------------
# Nodes
# ---------------------------------------------------------------------------

@handle_node_errors("generate_metadata", "failed")
def generate_metadata_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "meta"):
        log_node_execution("generate_metadata", session_id, "skipping (already generated)")
        return {"status": "questions_generating", "current_step": "Generating questions..."}

    log_node_execution("generate_metadata", session_id)

    meta = MetadataGenerator().generate_sheet_meta(
        name=state["name"],
        description=state["description"],
        roadmap=state["roadmap"],
    )

    _get_session_manager().set_meta(session_id, meta)

    return {"meta": meta, "status": "questions_generating", "current_step": "Generating questions..."}


@handle_node_errors("generate_questions", "failed")
def generate_questions_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0):
        log_node_execution("generate_questions", session_id, "skipping (already generated)")
        questions = state.get("questions", [])
        return {
            "status": "answers_generating",
            "current_step": "Generating answers...",
            "progress": get_progress_update(0, len(questions), "Generating answers..."),
        }

    log_node_execution("generate_questions", session_id)

    question_texts = QuestionGenerator().generate_questions(
        name=state["name"],
        description=state["description"],
        agent_type=state["agent_type"],
        question_count=state.get("question_count", 20),
        roadmap=state["roadmap"],
    )

    metadata_gen = MetadataGenerator()
    questions = []
    for text in question_texts:
        meta = metadata_gen.generate_question_metadata(
            question=text, topic=state["name"], context=state["description"],
        )
        questions.append(normalize_question_metadata({
            "title": text[:100],
            "question": text,
            "answer": "",
            "frequency": meta["frequency"],
            "priority": meta["priority"],
            "companyTypes": meta["companyTypes"],
        }))

    sm = _get_session_manager()
    for q in questions:
        sm.add_question(session_id, q)
    sm.update_progress(session_id, completed=0, total=len(questions), current_step="Questions generated, ready for answers")

    return {
        "questions": questions,
        "question_texts": question_texts,
        "status": "answers_generating",
        "current_step": "Generating answers...",
        "progress": get_progress_update(0, len(questions), "Generating answers..."),
    }


@handle_node_errors("generate_answers", "failed")
def generate_answers_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]
    questions = state.get("questions", [])

    if not questions:
        logger.warning("No questions found for session %s", session_id)
        return create_error_state("No questions to generate answers for")

    needing = get_questions_needing_answers(questions)
    if not needing:
        log_node_execution("generate_answers", session_id, "skipping (all answers generated)")
        return {
            "status": "finalizing",
            "current_step": "Finalizing sheet...",
            "progress": get_progress_update(len(questions), len(questions), "All answers generated"),
        }

    log_node_execution("generate_answers", session_id, f"generating {len(needing)} answers")

    sm = _get_session_manager()
    session_data = sm.get_session(session_id)
    technology = session_data.get("technology") if session_data else None

    generator = get_generator(state["agent_type"], technology=technology) if technology else get_generator(state["agent_type"])

    completed_count = count_completed_answers(questions)

    for question in needing:
        idx = questions.index(question)
        logger.info("Generating answer %d/%d", idx + 1, len(questions))

        question["answer"] = generator.generate_answer(
            question=question["question"],
            topic=state["name"],
            difficulty="Medium",
            frequency=question["frequency"],
            priority=question["priority"],
            company_types=question["companyTypes"],
        )
        completed_count += 1

        sm.update_progress(
            session_id,
            completed=completed_count,
            total=len(questions),
            current_step=f"Generated answer {completed_count}/{len(questions)}",
        )

    return {
        "questions": questions,
        "status": "finalizing",
        "current_step": "Finalizing sheet...",
        "progress": get_progress_update(len(questions), len(questions), "All answers generated"),
    }


def persist_state_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]
    log_node_execution("persist_state", session_id)

    try:
        sm = _get_session_manager()
        session_data = sm.get_session(session_id)
        if session_data:
            for field in ("status", "meta", "questions", "progress", "output_file"):
                if field in state:
                    session_data[field] = state.get(field, session_data.get(field))
            sm.save_session(session_id, session_data)
    except Exception as e:
        logger.error("Error persisting state: %s", e)

    return {}


@handle_node_errors("finalize", "failed")
def finalize_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "output_file") and check_skip_condition(state, "sheet_data"):
        log_node_execution("finalize", session_id, "skipping (already finalized)")
        return {"status": "completed", "current_step": "Sheet completed"}

    log_node_execution("finalize", session_id)

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
        "questions": state["questions"],
    }

    is_valid, errors = validate_sheet_structure(sheet_data)
    if not is_valid:
        logger.warning("Sheet structure validation errors: %s", errors)

    output_dir = os.path.join(config.output_dir, "interview_sheets")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{generate_slug(state['name'])}.json")

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(sheet_data, f, indent=2, ensure_ascii=False)

    sm = _get_session_manager()
    sm.set_output_file(session_id, output_file, sheet_data)
    sm.update_status(session_id, SessionStatus.COMPLETED, current_step="Sheet finalized and saved")

    return {
        "sheet_data": sheet_data,
        "output_file": output_file,
        "status": "completed",
        "current_step": "Sheet completed successfully",
    }
