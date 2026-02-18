"""Interview workflow: state, graph, nodes, and orchestrator in one file.

This is the single source of truth for the interview generation pipeline:
  State definition → LangGraph graph → Node functions → Orchestrator
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.core.config import config
from src.core.orchestrator import (
    BaseWorkflowOrchestrator,
    check_skip_condition,
    create_error_state,
    get_progress_update,
    handle_node_errors,
    log_node_execution,
)
from src.core.session import SessionStatus
from src.agents.interview.generators import AnswerAgentType, get_generator
from src.agents.interview.session import InterviewSessionManager
from src.agents.interview.utils import (
    COMPANY_TYPES,
    MetadataGenerator,
    QuestionGenerator,
    generate_cover_image_url,
    generate_slug,
    get_schema_defaults,
    validate_frequency,
    validate_priority,
    validate_sheet_structure,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 1. State
# ═══════════════════════════════════════════════════════════════════════════

class InterviewWorkflowState(TypedDict):
    session_id: str
    name: str
    description: str
    agent_type: str
    roadmap: str
    question_count: int

    status: str
    current_step: str
    error: Optional[str]

    meta: Optional[str]
    questions: List[Dict[str, Any]]
    question_texts: List[str]

    progress: Dict[str, Any]

    output_file: Optional[str]
    sheet_data: Optional[Dict[str, Any]]


_DEFAULT_PROGRESS: Dict[str, Any] = {"current_step": "Initializing...", "completed": 0, "total": 0}


def create_initial_state(
    session_id: str, name: str, description: str,
    agent_type: str, roadmap: str, question_count: int = 20,
) -> InterviewWorkflowState:
    return {
        "session_id": session_id, "name": name, "description": description,
        "agent_type": agent_type, "roadmap": roadmap, "question_count": question_count,
        "status": "pending", "current_step": "Initializing...", "error": None,
        "meta": None, "questions": [], "question_texts": [],
        "progress": {**_DEFAULT_PROGRESS}, "output_file": None, "sheet_data": None,
    }


def state_from_session(session_data: Dict[str, Any]) -> InterviewWorkflowState:
    return {
        "session_id": session_data.get("session_id", ""),
        "name": session_data.get("name", ""),
        "description": session_data.get("description", ""),
        "agent_type": session_data.get("agent_type", "generic"),
        "roadmap": session_data.get("roadmap", "Tech"),
        "question_count": session_data.get("question_count", 20),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get("current_step", "Initializing..."),
        "error": None,
        "meta": session_data.get("meta"),
        "questions": session_data.get("questions", []),
        "question_texts": [],
        "progress": session_data.get("progress", {**_DEFAULT_PROGRESS}),
        "output_file": session_data.get("output_file"),
        "sheet_data": None,
    }


def determine_resume_status(state: InterviewWorkflowState) -> str:
    has_meta = bool(state.get("meta"))
    has_questions = bool(state.get("questions"))
    all_answered = has_questions and all(q.get("answer") for q in state["questions"])
    if has_meta and all_answered:
        return "finalizing"
    if has_meta and has_questions:
        return "answers_generating"
    if has_meta:
        return "questions_generating"
    return "metadata_generating"


VALID_TRANSITIONS: Dict[str, List[str]] = {
    "pending": ["pending", "metadata_generating", "failed"],
    "metadata_generating": ["metadata_generating", "questions_generating", "failed"],
    "questions_generating": ["questions_generating", "answers_generating", "failed"],
    "answers_generating": ["answers_generating", "finalizing", "failed"],
    "finalizing": ["finalizing", "completed", "failed"],
    "completed": ["completed"],
    "failed": ["failed"],
}


def validate_state_transition(from_status: str, to_status: str) -> bool:
    return to_status in VALID_TRANSITIONS.get(from_status, [])


def get_questions_needing_answers(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [q for q in questions if not q.get("answer")]


def count_completed_answers(questions: List[Dict[str, Any]]) -> int:
    return sum(1 for q in questions if q.get("answer"))


def normalize_question_metadata(question: Dict[str, Any]) -> Dict[str, Any]:
    frequency = question.get("frequency", "Asked Sometimes")
    if not validate_frequency(frequency):
        frequency = "Asked Sometimes"
    priority = question.get("priority", "Medium")
    if not validate_priority(priority):
        priority = "Medium"
    company_types = question.get("companyTypes", [])
    if not isinstance(company_types, list):
        company_types = []
    company_types = [ct for ct in company_types if ct in COMPANY_TYPES]
    if not company_types:
        company_types = ["Startup", "MNC"]
    title = question.get("title", question.get("question", "")[:100])
    if len(title) > 100:
        title = title[:100]
    return {
        "title": title, "question": question.get("question", ""),
        "answer": question.get("answer", ""), "frequency": frequency,
        "priority": priority, "companyTypes": company_types,
        "resources": question.get("resources", []),
    }


# ═══════════════════════════════════════════════════════════════════════════
# 2. Nodes
# ═══════════════════════════════════════════════════════════════════════════

_session_manager = None


def _get_session_manager() -> InterviewSessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = InterviewSessionManager()
    return _session_manager


@handle_node_errors("generate_metadata", "failed")
def generate_metadata_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]
    if check_skip_condition(state, "meta"):
        log_node_execution("generate_metadata", session_id, "skipping (already generated)")
        return {"status": "questions_generating", "current_step": "Generating questions..."}
    log_node_execution("generate_metadata", session_id)
    meta = MetadataGenerator().generate_sheet_meta(
        name=state["name"], description=state["description"], roadmap=state["roadmap"],
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
            "status": "answers_generating", "current_step": "Generating answers...",
            "progress": get_progress_update(0, len(questions), "Generating answers..."),
        }
    log_node_execution("generate_questions", session_id)
    question_texts = QuestionGenerator().generate_questions(
        name=state["name"], description=state["description"],
        agent_type=state["agent_type"], question_count=state.get("question_count", 20),
        roadmap=state["roadmap"],
    )
    metadata_gen = MetadataGenerator()
    questions = []
    for text in question_texts:
        meta = metadata_gen.generate_question_metadata(question=text, topic=state["name"], context=state["description"])
        questions.append(normalize_question_metadata({
            "title": text[:100], "question": text, "answer": "",
            "frequency": meta["frequency"], "priority": meta["priority"], "companyTypes": meta["companyTypes"],
        }))
    sm = _get_session_manager()
    for q in questions:
        sm.add_question(session_id, q)
    sm.update_progress(session_id, completed=0, total=len(questions), current_step="Questions generated, ready for answers")
    return {
        "questions": questions, "question_texts": question_texts,
        "status": "answers_generating", "current_step": "Generating answers...",
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
            "status": "finalizing", "current_step": "Finalizing sheet...",
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
            question=question["question"], topic=state["name"], difficulty="Medium",
            frequency=question["frequency"], priority=question["priority"],
            company_types=question["companyTypes"],
        )
        completed_count += 1
        sm.update_progress(session_id, completed=completed_count, total=len(questions),
                           current_step=f"Generated answer {completed_count}/{len(questions)}")
    return {
        "questions": questions, "status": "finalizing", "current_step": "Finalizing sheet...",
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
        "name": state["name"], "slug": generate_slug(state["name"]),
        "description": state["description"], "meta": state.get("meta", ""),
        "coverImageURL": generate_cover_image_url(state["name"]),
        "liveOn": datetime.now(timezone.utc).isoformat(),
        "roadmap": state["roadmap"],
        "isPremium": defaults["isPremium"], "price": defaults["price"],
        "discountPercentage": defaults["discountPercentage"],
        "appliedCoupon": defaults["appliedCoupon"], "features": defaults["features"],
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
        "sheet_data": sheet_data, "output_file": output_file,
        "status": "completed", "current_step": "Sheet completed successfully",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 3. Graph
# ═══════════════════════════════════════════════════════════════════════════

def create_workflow_graph():
    wf = StateGraph[InterviewWorkflowState, None, InterviewWorkflowState, InterviewWorkflowState](InterviewWorkflowState)
    wf.add_node("generate_metadata", generate_metadata_node)
    wf.add_node("persist_after_metadata", persist_state_node)
    wf.add_node("generate_questions", generate_questions_node)
    wf.add_node("persist_after_questions", persist_state_node)
    wf.add_node("generate_answers", generate_answers_node)
    wf.add_node("persist_after_answers", persist_state_node)
    wf.add_node("finalize", finalize_node)
    wf.set_entry_point("generate_metadata")
    wf.add_edge("generate_metadata", "persist_after_metadata")
    wf.add_edge("persist_after_metadata", "generate_questions")
    wf.add_edge("generate_questions", "persist_after_questions")
    wf.add_edge("persist_after_questions", "generate_answers")
    wf.add_edge("generate_answers", "persist_after_answers")
    wf.add_edge("persist_after_answers", "finalize")
    wf.add_edge("finalize", END)
    return wf.compile()


# ═══════════════════════════════════════════════════════════════════════════
# 4. Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

_SYNC_FIELDS = ["meta", "questions", "status", "progress", "output_file"]


class InterviewWorkflowOrchestrator(BaseWorkflowOrchestrator):
    def __init__(self):
        super().__init__(
            graph=create_workflow_graph(),
            session_manager=InterviewSessionManager(),
            state_from_session_fn=state_from_session,
            determine_resume_status_fn=determine_resume_status,
            sync_fields=_SYNC_FIELDS,
        )

    def start_generation(
        self, name: str, description: str, agent_type: str,
        roadmap: str = "Tech", technology: Optional[str] = None, question_count: int = 20,
    ) -> str:
        try:
            AnswerAgentType(agent_type.lower())
        except ValueError:
            raise ValueError(f"Invalid agent type: {agent_type}")
        session_id = self.session_manager.create_session(
            name=name, description=description, agent_type=agent_type.lower(),
            roadmap=roadmap, question_count=question_count,
        )
        if technology:
            data = self.session_manager.get_session(session_id)
            if data:
                data["technology"] = technology
                self.session_manager.save_session(session_id, data)
        logger.info("Started generation workflow for session %s", session_id)
        return session_id

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        base = super().get_session_status(session_id)
        data = self.session_manager.get_session(session_id)
        if data:
            base.update({"name": data.get("name"), "roadmap": data.get("roadmap"), "description": data.get("description")})
        return base
