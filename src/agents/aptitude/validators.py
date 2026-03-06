"""Validation utilities for aptitude payloads and generated answers.

Validates:
- Input payload (topic name, questions list)
- Generated answer structure (required sections per format type)
"""

from typing import Any, Dict, List, Optional

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
    topic_name: str,
    questions: List[str],
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate the input payload for topic processing."""
    errors: List[str] = []

    if not topic_name or not topic_name.strip():
        errors.append("topic_name is required and cannot be empty")

    if not questions or not isinstance(questions, list):
        errors.append("questions must be a non-empty list")
    elif len(questions) == 0:
        errors.append("At least one question is required")
    else:
        for idx, q in enumerate(questions):
            if not q or not isinstance(q, str) or not q.strip():
                errors.append(f"Question at index {idx} is empty or invalid")
            elif len(q.strip()) < 10:
                errors.append(f"Question at index {idx} is too short (min 10 chars)")

    if category and category.upper() not in VALID_CATEGORIES:
        errors.append(f"Invalid category: {category}. Valid: {sorted(VALID_CATEGORIES)}")

    if sub_category and sub_category.upper() not in VALID_SUB_CATEGORIES:
        errors.append(f"Invalid sub_category: {sub_category}. Valid: {sorted(VALID_SUB_CATEGORIES)}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_question_payload(question_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate a single question payload (for API uploads)."""
    errors: List[str] = []

    if not question_data.get("question"):
        errors.append("question text is required")

    if not question_data.get("topicId"):
        errors.append("topicId is required")

    difficulty = question_data.get("difficulty", "MEDIUM")
    if difficulty.upper() not in VALID_DIFFICULTIES:
        errors.append(f"Invalid difficulty: {difficulty}. Valid: {sorted(VALID_DIFFICULTIES)}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_answer_structure(
    answer: str,
    format_type: str,
) -> Dict[str, Any]:
    """Validate that a generated answer contains all required sections.

    Returns:
        Dict with valid (bool), missing_sections (list), section_coverage (dict)
    """
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


def validate_batch_payload(topics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Validate a batch processing payload."""
    errors: List[str] = []

    if not topics or not isinstance(topics, list):
        return {"valid": False, "errors": ["topics must be a non-empty list"]}

    for idx, topic in enumerate(topics):
        if not topic.get("name"):
            errors.append(f"Topic at index {idx} missing 'name'")
        questions = topic.get("questions", [])
        if not questions:
            errors.append(f"Topic '{topic.get('name', idx)}' has no questions")

    return {"valid": len(errors) == 0, "errors": errors}
