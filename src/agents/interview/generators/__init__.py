"""Interview answer generators with registry-based factory.

Usage:
    from src.agents.interview.generators import get_generator
    generator = get_generator("tech", technology="React")
    answer = generator.generate_answer(question=..., topic=...)
"""

from typing import Dict, Type

from src.agents.interview.types import AnswerAgentType
from src.agents.interview.generators.base_generator import BaseAnswerGenerator
from src.agents.interview.generators.generic_generator import GenericAnswerGenerator
from src.agents.interview.generators.dsa_generator import DSAAnswerGenerator
from src.agents.interview.generators.tech_generator import TechAnswerGenerator
from src.agents.interview.generators.system_design_generator import SystemDesignAnswerGenerator

GENERATOR_REGISTRY: Dict[AnswerAgentType, Type[BaseAnswerGenerator]] = {
    AnswerAgentType.GENERIC: GenericAnswerGenerator,
    AnswerAgentType.DSA: DSAAnswerGenerator,
    AnswerAgentType.TECH: TechAnswerGenerator,
    AnswerAgentType.SYSTEM_DESIGN: SystemDesignAnswerGenerator,
}


def get_generator(agent_type: str, **kwargs) -> BaseAnswerGenerator:
    """Factory: return the correct generator for the given agent_type string.

    Raises ValueError if agent_type is not recognized.
    """
    enum_val = AnswerAgentType(agent_type.lower())
    cls = GENERATOR_REGISTRY[enum_val]
    return cls(**kwargs)


__all__ = [
    "BaseAnswerGenerator",
    "GenericAnswerGenerator",
    "DSAAnswerGenerator",
    "TechAnswerGenerator",
    "SystemDesignAnswerGenerator",
    "get_generator",
    "GENERATOR_REGISTRY",
]
