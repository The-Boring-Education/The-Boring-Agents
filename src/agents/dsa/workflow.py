"""Dedicated DSA workflow: questions + study guide generation."""

import json
import logging
import os
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.agents.dsa.generators import DSAContentGenerator
from src.agents.dsa.session import DSASessionManager
from src.agents.dsa.validators import topic_to_slug
from src.core.config import config
from src.core.orchestrator import (
    BaseWorkflowOrchestrator,
    check_skip_condition,
    get_progress_update,
    handle_node_errors,
    log_node_execution,
)
from src.core.session import SessionStatus

logger = logging.getLogger(__name__)


class DSAWorkflowState(TypedDict):
    session_id: str
    topic: str
    question_count: int
    include_real_world: bool
    difficulty: str

    status: str
    current_step: str
    error: Optional[str]

    questions: List[Dict[str, Any]]
    study_guide: Optional[Dict[str, Any]]
    progress: Dict[str, Any]

    output_file: Optional[str]
    dsa_data: Optional[Dict[str, Any]]


_DEFAULT_PROGRESS: Dict[str, Any] = {
    "current_step": "Initializing...",
    "completed": 0,
    "total": 0,
}


def state_from_session(session_data: Dict[str, Any]) -> DSAWorkflowState:
    return {
        "session_id": session_data.get("session_id", ""),
        "topic": session_data.get("topic", ""),
        "question_count": int(session_data.get("question_count", 20)),
        "include_real_world": bool(session_data.get("include_real_world", True)),
        "difficulty": str(session_data.get("difficulty", "MEDIUM")),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get("current_step", "Initializing..."),
        "error": None,
        "questions": session_data.get("questions", []),
        "study_guide": session_data.get("study_guide"),
        "progress": session_data.get("progress", {**_DEFAULT_PROGRESS}),
        "output_file": session_data.get("output_file"),
        "dsa_data": session_data.get("dsa_data"),
    }


def determine_resume_status(state: DSAWorkflowState) -> str:
    has_questions = bool(state.get("questions"))
    has_guide = bool(state.get("study_guide"))
    has_output = bool(state.get("output_file"))

    if has_questions and has_guide and has_output:
        return "completed"
    if has_questions and has_guide:
        return "finalizing"
    if has_questions:
        return "study_guide_generating"
    return "questions_generating"


_session_manager = None


def _get_session_manager() -> DSASessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = DSASessionManager()
    return _session_manager


@handle_node_errors("generate_questions", "failed")
def generate_questions_node(state: DSAWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0):
        log_node_execution("generate_questions", session_id, "skipping (already generated)")
        return {
            "status": "study_guide_generating",
            "current_step": "Generating study guide...",
        }

    log_node_execution("generate_questions", session_id)

    generator = DSAContentGenerator()
    questions = generator.generate_questions(
        topic=state["topic"],
        question_count=state["question_count"],
        include_real_world=state["include_real_world"],
        difficulty=state["difficulty"],
    )

    sm = _get_session_manager()
    sm.set_questions(session_id, questions)
    sm.update_progress(
        session_id,
        completed=len(questions),
        total=state["question_count"],
        current_step="Questions generated",
    )

    return {
        "questions": questions,
        "status": "study_guide_generating",
        "current_step": "Generating study guide...",
        "progress": get_progress_update(
            len(questions), state["question_count"], "Questions generated"
        ),
    }


@handle_node_errors("generate_study_guide", "failed")
def generate_study_guide_node(state: DSAWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "study_guide"):
        log_node_execution("generate_study_guide", session_id, "skipping (already generated)")
        return {
            "status": "finalizing",
            "current_step": "Finalizing DSA package...",
        }

    log_node_execution("generate_study_guide", session_id)

    generator = DSAContentGenerator()
    study_guide = generator.generate_study_guide(
        topic=state["topic"],
        questions=state.get("questions", []),
    )

    sm = _get_session_manager()
    sm.set_study_guide(session_id, study_guide)

    return {
        "study_guide": study_guide,
        "status": "finalizing",
        "current_step": "Finalizing DSA package...",
    }


@handle_node_errors("finalize", "failed")
def finalize_dsa_node(state: DSAWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "output_file") and check_skip_condition(state, "dsa_data"):
        log_node_execution("finalize", session_id, "skipping (already finalized)")
        return {"status": "completed", "current_step": "DSA generation completed"}

    log_node_execution("finalize", session_id)

    dsa_data = {
        "topic": state["topic"],
        "questions": state.get("questions", []),
        "studyGuide": state.get("study_guide"),
        "metadata": {
            "questionCount": len(state.get("questions", [])),
            "includeRealWorld": state.get("include_real_world", True),
            "difficulty": state.get("difficulty", "MEDIUM"),
        },
    }

    output_dir = os.path.join(config.output_dir, "dsa")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"dsa_{topic_to_slug(state['topic'])}.json"
    output_file = os.path.join(output_dir, output_filename)

    with open(output_file, "w", encoding="utf-8") as file_obj:
        json.dump(dsa_data, file_obj, indent=2, ensure_ascii=False)

    sm = _get_session_manager()
    sm.set_output_file(session_id, output_file, dsa_data)
    sm.update_status(
        session_id,
        SessionStatus.COMPLETED,
        current_step="DSA package finalized and saved",
    )

    return {
        "dsa_data": dsa_data,
        "output_file": output_file,
        "status": "completed",
        "current_step": "DSA generation completed successfully",
    }


def create_workflow_graph():
    workflow = StateGraph[DSAWorkflowState, None, DSAWorkflowState, DSAWorkflowState](
        DSAWorkflowState
    )

    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("generate_study_guide", generate_study_guide_node)
    workflow.add_node("finalize", finalize_dsa_node)

    workflow.set_entry_point("generate_questions")
    workflow.add_edge("generate_questions", "generate_study_guide")
    workflow.add_edge("generate_study_guide", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


_SYNC_FIELDS = ["questions", "study_guide", "status", "progress", "output_file"]


class DSAWorkflowOrchestrator(BaseWorkflowOrchestrator):
    """Orchestrator for dedicated DSA content generation."""

    def __init__(self):
        super().__init__(
            graph=create_workflow_graph(),
            session_manager=DSASessionManager(),
            state_from_session_fn=state_from_session,
            determine_resume_status_fn=determine_resume_status,
            sync_fields=_SYNC_FIELDS,
        )

    def start_generation(
        self,
        *,
        topic: str,
        question_count: int = 20,
        include_real_world: bool = True,
        difficulty: str = "MEDIUM",
    ) -> str:
        session_id = self.session_manager.create_session(
            topic=topic,
            question_count=question_count,
            include_real_world=include_real_world,
            difficulty=difficulty.upper(),
        )
        logger.info("Started DSA generation workflow for session %s", session_id)
        return session_id

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        base = super().get_session_status(session_id)
        data = self.session_manager.get_session(session_id)
        if data:
            base.update(
                {
                    "topic": data.get("topic"),
                    "question_count": data.get("question_count", 20),
                    "include_real_world": data.get("include_real_world", True),
                    "difficulty": data.get("difficulty", "MEDIUM"),
                    "study_guide": data.get("study_guide"),
                    "dsa_data": data.get("dsa_data"),
                }
            )
        return base
