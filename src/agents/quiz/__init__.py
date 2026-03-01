"""Quiz generation agent -- public API.

Import everything you need from the flat module files:
  generators.py  -- QuizAgentType, QuizDifficulty, generators, get_generator
  session.py     -- QuizSessionManager
  workflow.py    -- QuizWorkflowOrchestrator, state helpers
  prompts.py     -- prompt templates as constants
"""

from src.agents.quiz.generators import (
    QuizAgentType,
    QuizDifficulty,
    QuizMetadataGenerator,
    QuizQuestionGenerator,
    get_generator,
)
from src.agents.quiz.session import QuizSessionManager
from src.agents.quiz.workflow import QuizWorkflowOrchestrator

__all__ = [
    "QuizAgentType",
    "QuizDifficulty",
    "QuizMetadataGenerator",
    "QuizQuestionGenerator",
    "get_generator",
    "QuizSessionManager",
    "QuizWorkflowOrchestrator",
]
