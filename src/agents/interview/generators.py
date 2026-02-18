"""Answer generators for interview prep.

Contains:
- BaseAnswerGenerator (ABC with shared quality-check / MDX pipeline)
- Concrete generators: Generic, DSA, Tech, SystemDesign
- get_generator() factory to instantiate by AnswerAgentType
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from langchain_core.prompts import PromptTemplate

from src.agents.base import BaseAgent
from src.agents.interview.prompts import (
    DSA_ANSWER_STRUCTURE,
    DSA_PROMPT,
    GENERIC_ANSWER_STRUCTURE,
    GENERIC_PROMPT,
    SYSTEM_DESIGN_ANSWER_STRUCTURE,
    SYSTEM_DESIGN_PROMPT,
    TECH_ANSWER_STRUCTURE,
    get_tech_prompt,
)


class AnswerAgentType(Enum):
    GENERIC = "generic"
    DSA = "dsa"
    TECH = "tech"
    SYSTEM_DESIGN = "system_design"


# ---------------------------------------------------------------------------
# MDX formatting (inlined — single consumer)
# ---------------------------------------------------------------------------

def format_answer_as_mdx(answer: str) -> str:
    """Convert raw LLM answer to clean MDX."""
    answer = _fix_headers(answer)
    answer = _fix_code_blocks(answer)
    answer = _fix_lists(answer)
    answer = _fix_spacing(answer)
    return answer.strip()


def _fix_headers(text: str) -> str:
    lines: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("#"):
            hashes = len(stripped) - len(stripped.lstrip("#"))
            content = stripped.lstrip("#").strip()
            if hashes < 5:
                line = f"##### {content}"
        lines.append(line)
    return "\n".join(lines)


def _fix_code_blocks(text: str) -> str:
    lines = text.split("\n")
    result: list[str] = []
    in_block = False
    for line in lines:
        if line.strip().startswith("```"):
            if not in_block:
                in_block = True
                lang = line.strip()[3:].strip() or "text"
                result.append(f"```{lang}")
            else:
                in_block = False
                result.append("```")
        else:
            result.append(line)
    if in_block:
        result.append("```")
    return "\n".join(result)


def _fix_lists(text: str) -> str:
    lines = text.split("\n")
    result: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith("- ") or stripped.startswith("* ")) and i > 0:
            prev = lines[i - 1].strip()
            if prev and not prev.startswith("-") and not prev.startswith("*") and not prev.startswith("#"):
                result.append("")
        result.append(line)
    return "\n".join(result)


def _fix_spacing(text: str) -> str:
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text


def validate_mdx_structure(mdx_content: str) -> Dict[str, Any]:
    lines = mdx_content.split("\n")
    headers = [l.strip() for l in lines if l.strip().startswith("#")]
    code_starts = sum(1 for l in lines if l.strip().startswith("```") and len(l.strip()) > 3)
    code_ends = sum(1 for l in lines if l.strip() == "```")
    return {
        "valid": True,
        "headers": headers,
        "header_count": len(headers),
        "has_code_blocks": code_starts > 0,
        "code_blocks_balanced": code_starts == code_ends,
        "line_count": len(lines),
        "word_count": len(mdx_content.split()),
    }


# ---------------------------------------------------------------------------
# Base answer generator
# ---------------------------------------------------------------------------

class BaseAnswerGenerator(BaseAgent, ABC):
    """Abstract base for answer generators.

    Subclasses implement _get_answer_prompt_template and _get_answer_structure.
    The generate_answer / generate_content pipeline is fully handled here.
    """

    @abstractmethod
    def _get_answer_prompt_template(self) -> PromptTemplate:
        pass

    @abstractmethod
    def _get_answer_structure(self) -> Dict[str, str]:
        pass

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
            question=question, topic=topic, difficulty=difficulty,
            frequency=frequency, priority=priority,
            company_types=", ".join(company_types) if company_types else "All types",
        )
        raw = self._generate_with_prompt(prompt)
        improved = self._apply_quality_improvements(raw, question, topic, difficulty)
        mdx = format_answer_as_mdx(improved)
        self.logger.info("Answer generated successfully")
        return mdx

    def generate_content(self, content_type: str = "answer", **kwargs) -> Dict[str, Any]:
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

    def _apply_quality_improvements(self, answer: str, question: str, topic: str, difficulty: str) -> str:
        required = self._get_answer_structure()
        missing = [name for name, kw in required.items() if kw.lower() not in answer.lower()]
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
        formatted: list[str] = []
        in_code = False
        for line in lines:
            if line.strip().startswith("```"):
                if not in_code:
                    in_code = True
                    lang = line.strip()[3:].strip() or "text"
                    formatted.append(f"```{lang}")
                else:
                    in_code = False
                    formatted.append("```")
            else:
                formatted.append(line)
        return "\n".join(formatted)


# ---------------------------------------------------------------------------
# Concrete generators
# ---------------------------------------------------------------------------

_PROMPT_VARS = ["question", "topic", "difficulty", "frequency", "priority", "company_types"]


class GenericAnswerGenerator(BaseAnswerGenerator):
    def _get_answer_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(input_variables=_PROMPT_VARS, template=GENERIC_PROMPT)

    def _get_answer_structure(self) -> Dict[str, str]:
        return GENERIC_ANSWER_STRUCTURE


class DSAAnswerGenerator(BaseAnswerGenerator):
    def _get_answer_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(input_variables=_PROMPT_VARS, template=DSA_PROMPT)

    def _get_answer_structure(self) -> Dict[str, str]:
        return DSA_ANSWER_STRUCTURE


class SystemDesignAnswerGenerator(BaseAnswerGenerator):
    def _get_answer_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(input_variables=_PROMPT_VARS, template=SYSTEM_DESIGN_PROMPT)

    def _get_answer_structure(self) -> Dict[str, str]:
        return SYSTEM_DESIGN_ANSWER_STRUCTURE


class TechAnswerGenerator(BaseAnswerGenerator):
    """Technology-specific generator — prompt varies with the technology."""

    def __init__(self, technology: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.technology = technology or "General Tech"
        self.custom_params["technology"] = self.technology

    def _get_answer_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(input_variables=_PROMPT_VARS, template=get_tech_prompt(self.technology))

    def _get_answer_structure(self) -> Dict[str, str]:
        return TECH_ANSWER_STRUCTURE

    def generate_answer(
        self,
        question: str,
        topic: str,
        difficulty: str = "Medium",
        frequency: str = "Asked Sometimes",
        priority: str = "Medium",
        company_types: Optional[List[str]] = None,
        technology: Optional[str] = None,
    ) -> str:
        if technology and technology != self.technology:
            self.technology = technology
            self.custom_params["technology"] = technology
        return super().generate_answer(
            question=question, topic=topic, difficulty=difficulty,
            frequency=frequency, priority=priority, company_types=company_types,
        )


# ---------------------------------------------------------------------------
# Generator registry / factory
# ---------------------------------------------------------------------------

_GENERATOR_REGISTRY: Dict[AnswerAgentType, type] = {
    AnswerAgentType.GENERIC: GenericAnswerGenerator,
    AnswerAgentType.DSA: DSAAnswerGenerator,
    AnswerAgentType.TECH: TechAnswerGenerator,
    AnswerAgentType.SYSTEM_DESIGN: SystemDesignAnswerGenerator,
}


def get_generator(agent_type, **kwargs) -> BaseAnswerGenerator:
    """Instantiate a generator by AnswerAgentType enum or string name."""
    if isinstance(agent_type, str):
        try:
            agent_type = AnswerAgentType(agent_type.lower())
        except ValueError:
            raise ValueError(f"Unknown agent type: {agent_type}")
    cls = _GENERATOR_REGISTRY.get(agent_type)
    if cls is None:
        raise ValueError(f"Unknown agent type: {agent_type}")
    return cls(**kwargs)
