"""
The Boring Agents - AI-powered content generation for The Boring Education

This package provides AI agents for automated content generation across:
- Shiksha: Tech courses with video/text content
- Interview Prep: Sheet-format questions and answers
- Projects: Real-life project ideas and implementations
"""

__version__ = "0.1.0"
__author__ = "The Boring Education"

from src.agents.base import BaseAgent
from src.core.config import Config

__all__ = ["Config", "BaseAgent"]
