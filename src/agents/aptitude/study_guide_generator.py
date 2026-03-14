"""Study guide generator for aptitude interview prep.

Generates structured markdown study guides for aptitude topics,
following the same BaseAgent pattern as AptitudeAnswerGenerator.
"""

import logging
from typing import Any, Dict

from langchain_core.prompts import PromptTemplate

from src.agents.aptitude.prompts import (
    STUDY_GUIDE_ANSWER_STRUCTURE,
    STUDY_GUIDE_PROMPT,
)
from src.agents.base import BaseAgent

logger = logging.getLogger(__name__)

STUDY_GUIDE_PROMPT_VARS = ["topic", "sub_category"]


class AptitudeStudyGuideGenerator(BaseAgent):
    """Generates structured study guides for aptitude topics."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_content(
        self, content_type: str = "study_guide", **kwargs
    ) -> Dict[str, Any]:
        if content_type == "study_guide":
            guide = self.generate_guide(
                topic=kwargs.get("topic", ""),
                sub_category=kwargs.get("sub_category", ""),
            )
            return {"status": "success", "content": guide}
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_guide(self, topic: str, sub_category: str = "") -> str:
        """Generate a structured study guide for the given topic.

        Args:
            topic: Topic name (e.g., "Time and Work")
            sub_category: Sub-category (e.g., "ARITHMETIC_APTITUDE")

        Returns:
            Markdown string with Core Concepts, Solving Plan, and Examples.
        """
        self.logger.info("Generating study guide for topic: %s...", topic)

        prompt_template = PromptTemplate(
            input_variables=STUDY_GUIDE_PROMPT_VARS,
            template=STUDY_GUIDE_PROMPT,
        )

        prompt = prompt_template.format(
            topic=topic,
            sub_category=sub_category,
        )

        raw_guide = self._generate_with_prompt(prompt)
        validated = self._validate_sections(raw_guide, topic, sub_category)
        self.logger.info("Study guide generated successfully for: %s", topic)
        return validated.strip()

    def _validate_sections(self, guide: str, topic: str, sub_category: str) -> str:
        """Verify all 3 required sections are present; patch missing ones."""
        missing = [
            name
            for name, keyword in STUDY_GUIDE_ANSWER_STRUCTURE.items()
            if keyword.lower() not in guide.lower()
        ]

        if not missing:
            return guide

        self.logger.warning(
            "Missing sections in study guide: %s — patching...", missing
        )
        for section in missing:
            patch_prompt = (
                f"Generate a '{section}' section for a study guide on the aptitude topic: {topic}.\n"
                f"Sub-category: {sub_category}\n"
                f"Write only the section content, starting with the ### {section} header.\n"
                f"Keep it concise, actionable, and focused on Indian campus placement exams."
            )
            guide += f"\n\n{self._generate_with_prompt(patch_prompt)}"

        return guide
