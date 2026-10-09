"""Shiksha workflow: state, graph, nodes, and orchestrator in one file.

Pipeline: generate_outline -> generate_chapters -> finalize (Course Bundle).
Follows the DSA workflow shape exactly.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.agents.shiksha.generators import (
    ChapterGenerator,
    OutlineGenerator,
    _slugify,
)
from src.agents.shiksha.session import ShikshaSessionManager
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

BUNDLE_SCHEMA_VERSION = "shiksha-course@1"


class ShikshaWorkflowState(TypedDict):
    session_id: str
    topic: str
    chapter_count: int
    difficulty: str

    status: str
    current_step: str
    error: Optional[str]

    outline: Optional[Dict[str, Any]]
    chapters: List[Dict[str, Any]]
    progress: Dict[str, Any]

    output_file: Optional[str]
    bundle: Optional[Dict[str, Any]]


_DEFAULT_PROGRESS: Dict[str, Any] = {
    "current_step": "Initializing...",
    "completed": 0,
    "total": 0,
}


def state_from_session(session_data: Dict[str, Any]) -> ShikshaWorkflowState:
    return {
        "session_id": session_data.get("session_id", ""),
        "topic": session_data.get("topic", ""),
        "chapter_count": int(session_data.get("chapter_count", 5)),
        "difficulty": str(session_data.get("difficulty", "MEDIUM")),
        "status": session_data.get("status", "pending"),
        "current_step": session_data.get("progress", {}).get(
            "current_step", "Initializing..."
        ),
        "error": None,
        "outline": session_data.get("outline"),
        "chapters": session_data.get("chapters", []),
        "progress": session_data.get("progress", {**_DEFAULT_PROGRESS}),
        "output_file": session_data.get("output_file"),
        "bundle": session_data.get("bundle"),
    }


def determine_resume_status(state: ShikshaWorkflowState) -> str:
    has_outline = bool(state.get("outline"))
    has_chapters = bool(state.get("chapters"))
    has_output = bool(state.get("output_file"))

    if has_outline and has_chapters and has_output:
        return "completed"
    if has_outline and has_chapters:
        return "finalizing"
    if has_outline:
        return "chapters_generating"
    return "outline_generating"


_session_manager = None


def _get_session_manager() -> ShikshaSessionManager:
    global _session_manager
    if _session_manager is None:
        _session_manager = ShikshaSessionManager()
    return _session_manager


@handle_node_errors("generate_outline", "failed")
def generate_outline_node(state: ShikshaWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "outline"):
        log_node_execution(
            "generate_outline", session_id, "skipping (already generated)"
        )
        return {
            "status": "chapters_generating",
            "current_step": "Generating chapters...",
        }

    log_node_execution("generate_outline", session_id)

    generator = OutlineGenerator()
    outline = generator.generate_outline(
        topic=state["topic"],
        chapter_count=state["chapter_count"],
        difficulty=state["difficulty"],
    )

    sm = _get_session_manager()
    sm.set_outline(session_id, outline)
    sm.update_progress(
        session_id,
        completed=1,
        total=state["chapter_count"] + 1,
        current_step="Outline generated",
    )

    return {
        "outline": outline,
        "status": "chapters_generating",
        "current_step": "Generating chapters...",
        "progress": get_progress_update(
            1, state["chapter_count"] + 1, "Outline generated"
        ),
    }


@handle_node_errors("generate_chapters", "failed")
def generate_chapters_node(state: ShikshaWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "chapters", check_func=lambda c: c and len(c) > 0):
        log_node_execution(
            "generate_chapters", session_id, "skipping (already generated)"
        )
        return {
            "status": "finalizing",
            "current_step": "Finalizing course bundle...",
        }

    log_node_execution("generate_chapters", session_id)

    outline = state.get("outline") or {}
    planned = outline.get("chapters", []) or []
    course_name = outline.get("name", state["topic"])

    generator = ChapterGenerator()
    chapters: List[Dict[str, Any]] = []
    for item in planned:
        chapter = generator.generate_chapter(
            topic=state["topic"],
            course_name=course_name,
            chapter_key=item.get("key", ""),
            chapter_title=item.get("title", ""),
            difficulty=state["difficulty"],
        )
        chapters.append(chapter)

    sm = _get_session_manager()
    sm.set_chapters(session_id, chapters)
    sm.update_progress(
        session_id,
        completed=len(chapters) + 1,
        total=state["chapter_count"] + 1,
        current_step="Chapters generated",
    )

    return {
        "chapters": chapters,
        "status": "finalizing",
        "current_step": "Finalizing course bundle...",
        "progress": get_progress_update(
            len(chapters) + 1,
            state["chapter_count"] + 1,
            "Chapters generated",
        ),
    }


@handle_node_errors("finalize", "failed")
def finalize_shiksha_node(state: ShikshaWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]

    if check_skip_condition(state, "output_file") and check_skip_condition(
        state, "bundle"
    ):
        log_node_execution("finalize", session_id, "skipping (already finalized)")
        return {"status": "completed", "current_step": "Shiksha bundle completed"}

    log_node_execution("finalize", session_id)

    outline = state.get("outline") or {}
    course = {
        "name": outline.get("name", state["topic"]),
        "slug": outline.get("slug", _slugify(state["topic"]) or "course"),
        "description": outline.get("description", ""),
        "coverImageURL": outline.get("coverImageURL", ""),
        "roadmap": outline.get("roadmap", "FRONTEND"),
        "difficultyLevel": outline.get("difficultyLevel", state["difficulty"]),
        "isPremium": False,
        "features": outline.get("features", []),
        "credits": [],
    }

    bundle = {
        "schemaVersion": BUNDLE_SCHEMA_VERSION,
        "course": course,
        "chapters": state.get("chapters", []),
    }

    output_dir = os.path.join(config.output_dir, "shiksha")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = f"shiksha_{course['slug']}.json"
    output_file = os.path.join(output_dir, output_filename)

    with open(output_file, "w", encoding="utf-8") as file_obj:
        json.dump(bundle, file_obj, indent=2, ensure_ascii=False)

    sm = _get_session_manager()
    sm.set_output_file(session_id, output_file, bundle)
    sm.update_status(
        session_id,
        SessionStatus.COMPLETED,
        current_step="Shiksha bundle finalized and saved",
    )

    return {
        "bundle": bundle,
        "output_file": output_file,
        "status": "completed",
        "current_step": "Shiksha bundle completed successfully",
    }


def create_workflow_graph():
    workflow = StateGraph[
        ShikshaWorkflowState, None, ShikshaWorkflowState, ShikshaWorkflowState
    ](ShikshaWorkflowState)

    workflow.add_node("generate_outline", generate_outline_node)
    workflow.add_node("generate_chapters", generate_chapters_node)
    workflow.add_node("finalize", finalize_shiksha_node)

    workflow.set_entry_point("generate_outline")
    workflow.add_edge("generate_outline", "generate_chapters")
    workflow.add_edge("generate_chapters", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


_SYNC_FIELDS = [
    "outline",
    "chapters",
    "status",
    "progress",
    "output_file",
    "bundle",
]


class ShikshaWorkflowOrchestrator(BaseWorkflowOrchestrator):
    """Orchestrator for Shiksha course bundle generation."""

    def __init__(self):
        super().__init__(
            graph=create_workflow_graph(),
            session_manager=ShikshaSessionManager(),
            state_from_session_fn=state_from_session,
            determine_resume_status_fn=determine_resume_status,
            sync_fields=_SYNC_FIELDS,
        )

    def start_generation(
        self,
        *,
        topic: str,
        chapter_count: int = 5,
        difficulty: str = "MEDIUM",
    ) -> str:
        session_id = self.session_manager.create_session(
            topic=topic,
            chapter_count=chapter_count,
            difficulty=difficulty.upper(),
        )
        logger.info("Started Shiksha generation workflow for session %s", session_id)
        return session_id

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        base = super().get_session_status(session_id)
        data = self.session_manager.get_session(session_id)
        if data:
            base.update(
                {
                    "topic": data.get("topic"),
                    "chapter_count": data.get("chapter_count", 5),
                    "difficulty": data.get("difficulty", "MEDIUM"),
                    "outline": data.get("outline"),
                    "bundle": data.get("bundle"),
                }
            )
        return base
