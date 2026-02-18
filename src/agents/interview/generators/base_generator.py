"""Base answer generator for interview agents.

Subclasses only need to implement:
- _get_answer_prompt_template() -> the LLM prompt
- _get_answer_structure()       -> required section keywords for quality checks
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent
from src.agents.interview.common.mdx_utils import format_answer_as_mdx


class BaseAnswerGenerator(BaseAgent, ABC):
    """Abstract base class for all answer generators."""

    @abstractmethod
    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Return the PromptTemplate used for answer generation."""
        pass

    @abstractmethod
    def _get_answer_structure(self) -> Dict[str, str]:
        """Return {section_name: keyword} for quality-check validation."""
        pass

    # -- public API (single source of truth for all generators) ---------------

    def generate_answer(
        self,
        question: str,
        topic: str,
        difficulty: str = "Medium",
        frequency: str = "Asked Sometimes",
        priority: str = "Medium",
        company_types: Optional[List[str]] = None,
    ) -> str:
        if company_types is None:
            company_types = ["Startup", "MNC"]

        self.logger.info("Generating answer for: %s...", question[:50])

        prompt = self._get_answer_prompt_template().format(
            question=question,
            topic=topic,
            difficulty=difficulty,
            frequency=frequency,
            priority=priority,
            company_types=", ".join(company_types) if company_types else "All types",
        )

        raw_answer = self._generate_with_prompt(prompt)
        improved_answer = self._apply_quality_improvements(raw_answer, question, topic, difficulty)
        mdx_answer = format_answer_as_mdx(improved_answer)

        self.logger.info("Answer generated successfully")
        return mdx_answer

    def generate_content(self, content_type: str = "answer", **kwargs) -> Dict[str, Any]:
        """Single implementation -- subclasses should NOT override this."""
        if content_type == "answer":
            answer = self.generate_answer(
                question=kwargs.get("question", ""),
                topic=kwargs.get("topic", ""),
                difficulty=kwargs.get("difficulty", "Medium"),
                frequency=kwargs.get("frequency", "Asked Sometimes"),
                priority=kwargs.get("priority", "Medium"),
                company_types=kwargs.get("company_types", ["Startup", "MNC"]),
            )
            return {"status": "success", "answer": answer, "content_type": "answer"}
        raise ValueError(f"Unknown content type: {content_type}")

    # -- quality improvement helpers ------------------------------------------

    def _apply_quality_improvements(
        self, answer: str, question: str, topic: str, difficulty: str,
    ) -> str:
        required_sections = self._get_answer_structure()
        missing = [name for name, kw in required_sections.items() if kw.lower() not in answer.lower()]

        if missing:
            for section in missing:
                prompt = f"Generate a brief {section} section for this interview question: {question}\nTopic: {topic}"
                answer += f"\n\n{self._generate_with_prompt(prompt)}"

        return self._ensure_proper_formatting(answer)

    @staticmethod
    def _ensure_proper_formatting(answer: str) -> str:
        answer = answer.replace("###", "#####").replace("##", "#####")
        answer = answer.replace("\n\n\n", "\n\n")

        if "```" not in answer:
            return answer

        lines = answer.split("\n")
        formatted: List[str] = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    lang = line.strip()[3:].strip() or "text"
                    formatted.append(f"```{lang}")
                else:
                    in_code_block = False
                    formatted.append("```")
            else:
                formatted.append(line)

        return "\n".join(formatted)
