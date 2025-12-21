"""Shared prompt templates for interview agents."""

from langchain_core.prompts import PromptTemplate
from typing import Dict


def get_base_prompts() -> Dict[str, PromptTemplate]:
    """Get base prompt templates.
    
    Returns:
        Dictionary of base prompt templates
    """
    return {}


def get_agent_specific_prompts(agent_type: str) -> Dict[str, PromptTemplate]:
    """Get agent-specific prompt variations.
    
    Args:
        agent_type: Agent type (generic, dsa, tech, system_design)
        
    Returns:
        Dictionary of agent-specific prompts
    """
    return {}

