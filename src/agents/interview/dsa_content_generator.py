"""DSA Content Generator — produces structured JSON sections for question detail pages.

Unlike the existing DSAAnswerGenerator which outputs markdown, this generator
produces a structured JSON object with 8 educational sections:
first_principles, constraints, examples, ways_to_solve, how_to_approach,
pseudo_code, working_code, common_mistakes.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional

from langchain_core.prompts import PromptTemplate

from src.agents.base import BaseAgent
from src.agents.interview.prompts import (
    DSA_CONTENT_ANSWER_STRUCTURE,
    DSA_CONTENT_PROMPT,
)

logger = logging.getLogger(__name__)

# Input variables for the DSA content prompt
_DSA_CONTENT_VARS = [
    "question", "topic", "difficulty",
    "constraints", "examples", "leetcode_url",
]

# Required top-level keys in the generated JSON
_REQUIRED_SECTIONS = list(DSA_CONTENT_ANSWER_STRUCTURE.keys())


class DSAContentGenerator(BaseAgent):
    """Generates structured DSA question content as JSON.

    This is a standalone generator (not based on BaseAnswerGenerator)
    because it outputs structured JSON instead of markdown text.
    """

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "dsa_content": PromptTemplate(
                input_variables=_DSA_CONTENT_VARS,
                template=DSA_CONTENT_PROMPT,
            ),
        }

    def generate_content(
        self,
        question: str,
        topic: str,
        difficulty: str = "Medium",
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None,
        leetcode_url: str = "",
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate structured DSA content sections for a question.

        Args:
            question: The DSA question title/name.
            topic: Primary topic (e.g. "Array", "Linked List").
            difficulty: "Easy", "Medium", or "Hard".
            constraints: List of constraint strings from LeetCode.
            examples: List of example dicts with input/output/explanation.
            leetcode_url: URL to the LeetCode problem.

        Returns:
            Dict with "status", "sections" (the 8-section JSON), and metadata.
        """
        if constraints is None:
            constraints = []
        if examples is None:
            examples = []

        self.logger.info("Generating DSA content for: %s...", question[:60])

        # Format constraints and examples as readable strings for the prompt
        constraints_str = "\n".join(
            f"- {c}" for c in constraints
        ) if constraints else "No constraints provided"

        examples_str = self._format_examples_for_prompt(examples)

        # Build and send prompt
        prompt = self._format_prompt(
            "dsa_content",
            question=question,
            topic=topic,
            difficulty=difficulty,
            constraints=constraints_str,
            examples=examples_str,
            leetcode_url=leetcode_url or "Not provided",
        )

        raw_response = self._generate_with_prompt(prompt)

        # Parse JSON from response
        sections = self._parse_json_response(raw_response)

        # Validate all required sections are present
        validation = self._validate_sections(sections)
        if not validation["valid"]:
            self.logger.warning(
                "Missing sections: %s — attempting repair",
                validation["missing"],
            )
            sections = self._repair_missing_sections(
                sections, validation["missing"],
                question, topic, difficulty,
            )

        self.logger.info("DSA content generated successfully for: %s", question[:60])

        return {
            "status": "success",
            "sections": sections,
            "question": question,
            "topic": topic,
            "difficulty": difficulty,
        }

    def _format_examples_for_prompt(self, examples: List[Dict[str, str]]) -> str:
        """Format example dicts into a readable string for the prompt."""
        if not examples:
            return "No examples provided"

        parts = []
        for i, ex in enumerate(examples, 1):
            input_text = ex.get("input") or ex.get("inputText", "")
            output_text = ex.get("output") or ex.get("outputText", "")
            explanation = ex.get("explanation", "")
            part = f"Example {i}:\n  Input: {input_text}\n  Output: {output_text}"
            if explanation:
                part += f"\n  Explanation: {explanation}"
            parts.append(part)

        return "\n".join(parts)

    def _parse_json_response(self, raw: str) -> Dict[str, Any]:
        """Extract and parse JSON from the LLM response.

        The LLM may wrap the JSON in markdown code fences or add
        text before/after. This method handles all those cases.
        """
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            # Remove opening fence (```json or ```)
            first_newline = cleaned.index("\n")
            cleaned = cleaned[first_newline + 1:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        # Try direct parse first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Try to find JSON object between first { and last }
        first_brace = cleaned.find("{")
        last_brace = cleaned.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_str = cleaned[first_brace:last_brace + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass

        # Last resort: try to fix common JSON issues
        try:
            # Remove trailing commas before } or ]
            fixed = re.sub(r",\s*([}\]])", r"\1", cleaned)
            first_brace = fixed.find("{")
            last_brace = fixed.rfind("}")
            if first_brace != -1 and last_brace != -1:
                return json.loads(fixed[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass

        self.logger.error("Failed to parse JSON from response (length=%d)", len(raw))
        raise ValueError(
            "LLM response could not be parsed as JSON. "
            "Raw response starts with: " + raw[:200]
        )

    def _validate_sections(self, sections: Dict[str, Any]) -> Dict[str, Any]:
        """Check that all 8 required sections are present and non-empty."""
        missing = [
            key for key in _REQUIRED_SECTIONS
            if key not in sections or not sections[key]
        ]
        return {
            "valid": len(missing) == 0,
            "missing": missing,
            "present": [k for k in _REQUIRED_SECTIONS if k in sections],
        }

    def _repair_missing_sections(
        self,
        sections: Dict[str, Any],
        missing: List[str],
        question: str,
        topic: str,
        difficulty: str,
    ) -> Dict[str, Any]:
        """Attempt to regenerate missing sections individually."""
        for section_name in missing:
            self.logger.info("Repairing missing section: %s", section_name)
            repair_prompt = (
                f"Generate ONLY the '{section_name}' section for this DSA question.\n"
                f"Question: {question}\n"
                f"Topic: {topic}\n"
                f"Difficulty: {difficulty}\n\n"
                f"Output a valid JSON object with just the '{section_name}' key "
                f"following the structure from the DSA content spec. "
                f"Output ONLY the JSON, no other text."
            )
            try:
                raw = self._generate_with_prompt(repair_prompt)
                parsed = self._parse_json_response(raw)
                if section_name in parsed:
                    sections[section_name] = parsed[section_name]
                    self.logger.info("Successfully repaired section: %s", section_name)
                else:
                    self.logger.warning(
                        "Repair for '%s' did not produce the expected key", section_name
                    )
            except Exception as e:
                self.logger.error("Failed to repair section '%s': %s", section_name, e)

        return sections
