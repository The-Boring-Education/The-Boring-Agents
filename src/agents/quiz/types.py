"""
Type definitions for quiz agents.

These types are used by the Quiz LangGraph workflow.
"""

from enum import Enum


class QuizAgentType(Enum):
    """Available quiz generator agent types."""
    GENERIC = "generic"
    TECH = "tech"
    DSA = "dsa"
    CONCEPTUAL = "conceptual"


class QuizDifficulty(Enum):
    """Quiz difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

