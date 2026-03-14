"""Aptitude answer generation agent.

Generates structured answers for campus placement aptitude questions
across four formats: SPEED, RULES, PERSPECTIVE, and BEHAVIORAL.
"""

from src.agents.aptitude.constants import (
    CATEGORY_SUB_CATEGORY_MAP,
    MIN_QUESTIONS_PER_TOPIC,
    SUB_CATEGORY_FORMAT_MAP,
    TOPIC_REGISTRY,
    TOPIC_SLUG_SET,
    get_format_for_sub_category,
    get_topic_by_slug,
    get_topic_info,
    get_topics_for_sub_category,
    resolve_topic,
    validate_topic_name,
    validate_topic_slug,
)
from src.agents.aptitude.generators import (
    AptitudeAnswerGenerator,
    get_aptitude_generator,
)
from src.agents.aptitude.validators import (
    validate_answer_structure,
    validate_batch_payload,
    validate_question_payload,
    validate_topic_payload,
)
from src.agents.aptitude.workflow import AptitudeWorkflow

__all__ = [
    "AptitudeAnswerGenerator",
    "AptitudeWorkflow",
    "CATEGORY_SUB_CATEGORY_MAP",
    "MIN_QUESTIONS_PER_TOPIC",
    "SUB_CATEGORY_FORMAT_MAP",
    "TOPIC_REGISTRY",
    "TOPIC_SLUG_SET",
    "get_aptitude_generator",
    "get_format_for_sub_category",
    "get_topic_by_slug",
    "get_topic_info",
    "get_topics_for_sub_category",
    "resolve_topic",
    "validate_answer_structure",
    "validate_batch_payload",
    "validate_question_payload",
    "validate_topic_name",
    "validate_topic_payload",
    "validate_topic_slug",
]
