"""Validation utilities for aptitude payloads and generated answers.

Validates:
- Input payload (topic slug, questions list)
- Generated answer structure (required sections per format type)
"""

from typing import Any, Dict, List, Optional

from src.agents.aptitude.constants import MIN_QUESTIONS_PER_TOPIC, TOPIC_SLUG_SET
from src.agents.aptitude.prompts import ANSWER_STRUCTURE_MAP

VALID_CATEGORIES = {"QUANTITATIVE", "VERBAL", "REASONING", "INTERVIEW"}
VALID_SUB_CATEGORIES = {
    "ARITHMETIC_APTITUDE", "DATA_INTERPRETATION",
    "VERBAL_ABILITY",
    "LOGICAL_REASONING",
    "GD_ROUND", "HR_INTERVIEW",
}
VALID_FORMATS = {"SPEED", "RULES", "PERSPECTIVE", "BEHAVIORAL"}
VALID_DIFFICULTIES = {"EASY", "MEDIUM", "HARD"}


def validate_topic_payload(
    topic: str,
    questions: Optional[List[str]] = None,
    num_questions: Optional[int] = None,
) -> Dict[str, Any]:
    """Validate the input payload for topic processing."""
    errors: List[str] = []

    if not topic or not topic.strip():
        errors.append("topic is required and cannot be empty")

    if questions and not isinstance(questions, list):
        errors.append("questions must be a list if provided")
    elif questions:
        for idx, q in enumerate(questions):
            if not q or not isinstance(q, str) or not q.strip():
                errors.append(f"Question at index {idx} is empty or invalid")
            elif len(q.strip()) < 10:
                errors.append(f"Question at index {idx} is too short (min 10 chars)")

    if num_questions is not None and num_questions < 1:
        errors.append("num_questions must be a positive integer")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_question_payload(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single question payload for DB insertion."""
    errors: List[str] = []

    if not question_data.get("question"):
        errors.append("question text is required")

    if not question_data.get("topic"):
        errors.append("topic (slug) is required")
    elif question_data["topic"] not in TOPIC_SLUG_SET:
        errors.append(f"Invalid topic slug: {question_data['topic']}")

    difficulty = question_data.get("difficulty", "MEDIUM")
    if isinstance(difficulty, str) and difficulty.upper() not in VALID_DIFFICULTIES:
        errors.append(f"Invalid difficulty: {difficulty}. Valid: {sorted(VALID_DIFFICULTIES)}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_answer_structure(
    answer: str,
    format_type: str,
) -> Dict[str, Any]:
    """Validate that a generated answer contains all required sections."""
    if not answer or not answer.strip():
        return {
            "valid": False,
            "errors": ["Answer is empty"],
            "missing_sections": [],
            "section_coverage": {},
        }

    fmt = format_type.upper()
    if fmt not in ANSWER_STRUCTURE_MAP:
        return {
            "valid": False,
            "errors": [f"Unknown format type: {format_type}"],
            "missing_sections": [],
            "section_coverage": {},
        }

    required = ANSWER_STRUCTURE_MAP[fmt]
    answer_lower = answer.lower()

    section_coverage: Dict[str, bool] = {}
    missing: List[str] = []

    for section_name, keyword in required.items():
        present = keyword.lower() in answer_lower
        section_coverage[section_name] = present
        if not present:
            missing.append(section_name)

    return {
        "valid": len(missing) == 0,
        "errors": [f"Missing section: {s}" for s in missing] if missing else [],
        "missing_sections": missing,
        "section_coverage": section_coverage,
    }


def validate_batch_payload(topics: List[str]) -> Dict[str, Any]:
    """Validate a batch processing payload (list of topic slugs/names)."""
    errors: List[str] = []

    if not topics or not isinstance(topics, list):
        return {"valid": False, "errors": ["topics must be a non-empty list"]}

    for idx, topic in enumerate(topics):
        if not topic or not isinstance(topic, str) or not topic.strip():
            errors.append(f"Topic at index {idx} is empty or invalid")

    return {"valid": len(errors) == 0, "errors": errors}
