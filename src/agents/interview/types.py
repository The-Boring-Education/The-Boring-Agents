"""Type definitions for interview agents."""

from enum import Enum


class AnswerAgentType(Enum):
    """Available answer creator agent types."""
    GENERIC = "generic"
    DSA = "dsa"
    TECH = "tech"  # Future implementation
    SYSTEM_DESIGN = "system_design"  # Future implementation 