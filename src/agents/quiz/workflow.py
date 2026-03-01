"""Quiz workflow: state, graph, nodes, and orchestrator in one file.

Single source of truth for the quiz generation pipeline:
  State definition -> LangGraph graph -> Node functions -> Orchestrator
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.core.config import config
from src.core.orchestrator import (
    BaseWorkflowOrchestrator,
    check_skip_condition,
    get_progress_update,
    handle_node_errors,
    log_node_execution,
)
from src.core.session import SessionStatus
from src.agents.quiz.generators import (
    QuizAgentType,
    QuizDifficulty,
    QuizMetadataGenerator,
    QuizQuestionGenerator,
)
from src.agents.quiz.session import QuizSessionManager
from src.agents.interview.utils import generate_slug

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 1. State
# ═══════════════════════════════════════════════════════════════════════════

class QuizWorkflowState(TypedDict):
    session_id: str
    topic: str
    description: str
    agent_type: str
    question_count: int
    target_audience: str
    difficulty: str

    status: str
    current_step: str
    error: Optional[str]

    category_metadata: Optional[Dict[str, Any]]
    questions: List[Dict[str, Any]]

    progress: Dict[str, Any]

    output_file: Optional[str]
    quiz_data: Optional[Dict[str, Any]]


_DEFAULT_PROGRESS: Dict[str, Any] = {
    "current_step": "Initializing...",
    "completed": 0,
    "total": 0,
}


def create_initial_state(
    session_id: str,
    topic: str,
    description: str,
    agent_type: str,
    question_count: int = 20,
    target_audience: str = "developers",
    difficulty: str = "medium",
) -> QuizWorkflowState:
    return {
        "session_id": session_id,
        "topic": topic,
        "description": description,
        "agent_type": agent_type,
        "question_count": question_count,
        "target_audience": target_audience,
        "difficulty": difficulty,
        "status": "pending",
        "current_step": "Initializing...",
        "error": None,
        "category_metadata": None,
        "questions": [],
        "progress": {**_DEFAULT_PROGRESS},
        "output_file": None,
        "quiz_data": None,
    }


def state_from_session(session_data: Dict[str, Any]) -> QuizWorkflowState:
    return {
        "session_id": session_data.get("session_id", ""),
        "topic": session_data.get("topic", ""),
        "description": session_data.get("description", ""),
        "agent_type": session_data.get("agent_type", "generic"),
        "question_count": session_data.get("question_count", 20),
        "target_audience": session_data.get("target_audience", "developers"),
        "difficulty": session_data.get("difficulty", "medium"),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get("current_step", "Initializing..."),
        "error": None,
        "category_metadata": session_data.get("category_metadata"),
        "questions": session_data.get("questions", []),
        "progress": session_data.get("progress", {**_DEFAULT_PROGRESS}),
        "output_file": session_data.get("output_file"),
        "quiz_data": session_data.get("quiz_data"),
    }


def determine_resume_status(state: QuizWorkflowState) -> str:
    has_questions = bool(state.get("questions"))
    has_metadata = bool(state.get("category_metadata"))
    has_output = bool(state.get("output_file"))

    if has_questions and has_metadata and has_output:
        return "completed"
    if has_questions and has_metadata:
        return "finalizing"
    if has_questions:
        return "metadata_generating"
    return "questions_generating"


# ═══════════════════════════════════════════════════════════════════════════
# 2. Nodes
# ═══════════════════════════════════════════════════════════════════════════

_session_manager = None


def _get_session_manager() -> QuizSessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = QuizSessionManager()
    return _session_manager


@handle_node_errors("generate_questions", "failed")
def generate_questions_node(state: QuizWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "questions", check_func=lambda q: q and len(q) > 0):
        log_node_execution("generate_questions", session_id, "skipping (already generated)")
        return {
            "status": "metadata_generating",
            "current_step": "Generating category metadata...",
        }

    log_node_execution("generate_questions", session_id)

    question_generator = QuizQuestionGenerator()
    questions = question_generator.generate_batch_questions(
        topic=state["topic"],
        question_count=state["question_count"],
        difficulty=QuizDifficulty(state["difficulty"]),
        target_audience=state["target_audience"],
    )

    sm = _get_session_manager()
    for question in questions:
        sm.add_question(session_id, question)

    sm.update_progress(
        session_id,
        completed=len(questions),
        total=state["question_count"],
        current_step=f"Generated {len(questions)} questions",
    )

    return {
        "questions": questions,
        "status": "metadata_generating",
        "current_step": "Generating category metadata...",
        "progress": get_progress_update(len(questions), state["question_count"], "Questions generated"),
    }


@handle_node_errors("generate_metadata", "failed")
def generate_category_metadata_node(state: QuizWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "category_metadata"):
        log_node_execution("generate_category_metadata", session_id, "skipping (already generated)")
        return {
            "status": "finalizing",
            "current_step": "Finalizing quiz...",
        }

    log_node_execution("generate_category_metadata", session_id)

    metadata_generator = QuizMetadataGenerator()
    metadata = metadata_generator.generate_category_metadata(
        topic=state["topic"],
        question_count=len(state.get("questions", [])),
    )

    sm = _get_session_manager()
    sm.set_category_metadata(session_id, metadata)

    return {
        "category_metadata": metadata,
        "status": "finalizing",
        "current_step": "Finalizing quiz...",
    }


def persist_state_node(state: QuizWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]
    log_node_execution("persist_state", session_id)

    try:
        sm = _get_session_manager()
        session_data = sm.get_session(session_id)
        if session_data:
            for field in ("status", "questions", "category_metadata", "output_file"):
                if field in state:
                    session_data[field] = state.get(field, session_data.get(field))
            sm.save_session(session_id, session_data)
    except Exception as exc:
        logger.error("Error persisting state: %s", exc)

    return {}


@handle_node_errors("finalize", "failed")
def finalize_quiz_node(state: QuizWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "output_file") and check_skip_condition(state, "quiz_data"):
        log_node_execution("finalize", session_id, "skipping (already finalized)")
        return {"status": "completed", "current_step": "Quiz completed"}

    log_node_execution("finalize", session_id)

    category_metadata = state.get("category_metadata") or {}
    quiz_data = {
        "categoryName": category_metadata.get("categoryName", state.get("topic", "")),
        "categoryDescription": category_metadata.get("categoryDescription", state.get("description", "")),
        "categoryIcon": category_metadata.get("categoryIcon", ""),
        "questions": state["questions"],
        "isActive": True,
    }

    output_dir = os.path.join(config.output_dir, "quizzes")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"quiz_{generate_slug(state['topic'])}.json"
    output_file = os.path.join(output_dir, output_filename)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(quiz_data, f, indent=2, ensure_ascii=False)

    sm = _get_session_manager()
    sm.set_output_file(session_id, output_file, quiz_data)
    sm.update_status(session_id, SessionStatus.COMPLETED, current_step="Quiz finalized and saved")

    return {
        "quiz_data": quiz_data,
        "output_file": output_file,
        "status": "completed",
        "current_step": "Quiz completed successfully",
    }


# ═══════════════════════════════════════════════════════════════════════════
# 3. Graph
# ═══════════════════════════════════════════════════════════════════════════

def create_workflow_graph():
    wf = StateGraph[QuizWorkflowState, None, QuizWorkflowState, QuizWorkflowState](QuizWorkflowState)

    wf.add_node("generate_questions", generate_questions_node)
    wf.add_node("persist_after_questions", persist_state_node)
    wf.add_node("generate_metadata", generate_category_metadata_node)
    wf.add_node("persist_after_metadata", persist_state_node)
    wf.add_node("finalize", finalize_quiz_node)

    wf.set_entry_point("generate_questions")

    wf.add_edge("generate_questions", "persist_after_questions")
    wf.add_edge("persist_after_questions", "generate_metadata")
    wf.add_edge("generate_metadata", "persist_after_metadata")
    wf.add_edge("persist_after_metadata", "finalize")
    wf.add_edge("finalize", END)

    return wf.compile()


# ═══════════════════════════════════════════════════════════════════════════
# 4. Orchestrator
# ═══════════════════════════════════════════════════════════════════════════

_SYNC_FIELDS = ["category_metadata", "questions", "status", "progress", "output_file"]


class QuizWorkflowOrchestrator(BaseWorkflowOrchestrator):
    def __init__(self):
        super().__init__(
            graph=create_workflow_graph(),
            session_manager=QuizSessionManager(),
            state_from_session_fn=state_from_session,
            determine_resume_status_fn=determine_resume_status,
            sync_fields=_SYNC_FIELDS,
        )

    def start_generation(
        self,
        topic: str,
        description: str,
        agent_type: str,
        question_count: int = 20,
        target_audience: str = "developers",
        difficulty: str = "medium",
    ) -> str:
        try:
            QuizAgentType(agent_type.lower())
        except ValueError:
            raise ValueError(f"Invalid agent type: {agent_type}")

        session_id = self.session_manager.create_session(
            topic=topic,
            description=description,
            agent_type=agent_type.lower(),
            question_count=question_count,
            target_audience=target_audience,
            difficulty=difficulty,
        )
        logger.info("Started quiz generation workflow for session %s", session_id)
        return session_id

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        base = super().get_session_status(session_id)
        data = self.session_manager.get_session(session_id)
        if data:
            base.update({
                "topic": data.get("topic"),
                "description": data.get("description"),
                "difficulty": data.get("difficulty"),
                "target_audience": data.get("target_audience"),
            })
        return base
