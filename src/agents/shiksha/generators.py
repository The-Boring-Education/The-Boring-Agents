"""Shiksha generators: course outline and chapter MDX generation.

All LLM calls for the shiksha agent live in this module — workflow nodes
must never construct a chat model directly.
"""

import json
import logging
import re
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate

from src.agents.base import BaseAgent
from src.agents.shiksha.prompts import (
    SHIKSHA_CHAPTER_PROMPT,
    SHIKSHA_OUTLINE_PROMPT,
)

logger = logging.getLogger(__name__)

ALLOWED_ROADMAPS = {
    "FRONTEND",
    "BACKEND",
    "FULLSTACK",
    "DSA",
    "AI",
    "DATA",
    "GTM",
}

ALLOWED_DIFFICULTY = {"EASY", "MEDIUM", "HARD"}


def _parse_json_object(response: str) -> Dict[str, Any]:
    """Parse first JSON object found in response text."""
    try:
        start = response.find("{")
        end = response.rfind("}") + 1
        if start != -1 and end > start:
            payload = json.loads(response[start:end])
        else:
            payload = json.loads(response)
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _slugify(value: str) -> str:
    """Convert free text into kebab-case slug/key."""
    slug = value.strip().lower().replace("_", "-").replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug


def _normalize_difficulty(value: str, default: str = "MEDIUM") -> str:
    normalized_default = (default or "MEDIUM").upper()
    if normalized_default not in ALLOWED_DIFFICULTY:
        normalized_default = "MEDIUM"
    candidate = (value or "").upper()
    return candidate if candidate in ALLOWED_DIFFICULTY else normalized_default


def _unique_keys(keys: List[str]) -> List[str]:
    """Ensure chapter keys are unique, suffixing duplicates."""
    seen: Dict[str, int] = {}
    result: List[str] = []
    for key in keys:
        base = key or "chapter"
        if base not in seen:
            seen[base] = 1
            result.append(base)
        else:
            seen[base] += 1
            candidate = f"{base}-{seen[base]}"
            while candidate in seen:
                seen[base] += 1
                candidate = f"{base}-{seen[base]}"
            seen[candidate] = 1
            result.append(candidate)
    return result


class OutlineGenerator(BaseAgent):
    """Generates a Shiksha course outline (metadata + chapter list)."""

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "outline": PromptTemplate(
                input_variables=["topic", "chapter_count", "difficulty"],
                template=SHIKSHA_OUTLINE_PROMPT,
            ),
        }

    def generate_content(self, **kwargs) -> Dict[str, Any]:
        return self.generate_outline(
            topic=kwargs.get("topic", ""),
            chapter_count=int(kwargs.get("chapter_count", 5)),
            difficulty=str(kwargs.get("difficulty", "MEDIUM")),
        )

    def generate_outline(
        self,
        *,
        topic: str,
        chapter_count: int = 5,
        difficulty: str = "MEDIUM",
    ) -> Dict[str, Any]:
        """Generate and normalize a course outline for the topic."""
        prompt = self._format_prompt(
            "outline",
            topic=topic,
            chapter_count=chapter_count,
            difficulty=difficulty.upper(),
        )
        response = self._generate_with_prompt(prompt)
        raw = _parse_json_object(response)

        if not raw:
            logger.warning("Shiksha outline parse failed for topic '%s'", topic)

        return normalize_outline(
            raw,
            topic=topic,
            chapter_count=chapter_count,
            difficulty=difficulty,
        )


class ChapterGenerator(BaseAgent):
    """Generates MDX content for a single Shiksha chapter."""

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "chapter": PromptTemplate(
                input_variables=[
                    "topic",
                    "course_name",
                    "chapter_key",
                    "chapter_title",
                    "difficulty",
                ],
                template=SHIKSHA_CHAPTER_PROMPT,
            ),
        }

    def generate_content(self, **kwargs) -> Dict[str, Any]:
        return self.generate_chapter(
            topic=kwargs.get("topic", ""),
            course_name=kwargs.get("course_name", ""),
            chapter_key=kwargs.get("chapter_key", ""),
            chapter_title=kwargs.get("chapter_title", ""),
            difficulty=str(kwargs.get("difficulty", "MEDIUM")),
        )

    def generate_chapter(
        self,
        *,
        topic: str,
        course_name: str,
        chapter_key: str,
        chapter_title: str,
        difficulty: str = "MEDIUM",
    ) -> Dict[str, Any]:
        """Generate and normalize one chapter's MDX content."""
        prompt = self._format_prompt(
            "chapter",
            topic=topic,
            course_name=course_name,
            chapter_key=chapter_key,
            chapter_title=chapter_title,
            difficulty=difficulty.upper(),
        )
        response = self._generate_with_prompt(prompt)
        raw = _parse_json_object(response)

        if not raw:
            logger.warning("Shiksha chapter parse failed for key '%s'", chapter_key)

        return normalize_chapter(
            raw,
            chapter_key=chapter_key,
            chapter_title=chapter_title,
        )


def normalize_outline(
    raw: Dict[str, Any],
    *,
    topic: str,
    chapter_count: int,
    difficulty: str,
) -> Dict[str, Any]:
    """Normalize raw outline JSON into the validator-compatible shape."""
    if not isinstance(raw, dict):
        raw = {}

    name = str(raw.get("name") or f"{topic} Course").strip()[:120]
    slug = _slugify(str(raw.get("slug") or name or topic)) or "course"
    description = str(
        raw.get("description") or f"Learn {topic} with hands-on chapters."
    ).strip()

    roadmap = str(raw.get("roadmap") or "FRONTEND").upper()
    if roadmap not in ALLOWED_ROADMAPS:
        roadmap = "FRONTEND"

    difficulty_level = _normalize_difficulty(
        str(raw.get("difficultyLevel") or difficulty), difficulty
    )

    features = raw.get("features")
    if isinstance(features, list):
        features = [str(f).strip() for f in features if str(f).strip()]
    if not features:
        features = ["Hands-on examples"]

    raw_chapters = raw.get("chapters")
    if not isinstance(raw_chapters, list):
        raw_chapters = []

    chapters: List[Dict[str, str]] = []
    for idx in range(chapter_count):
        source = (
            raw_chapters[idx]
            if idx < len(raw_chapters) and isinstance(raw_chapters[idx], dict)
            else {}
        )
        title = str(source.get("title") or f"{topic} Chapter {idx + 1}").strip()
        key = _slugify(str(source.get("key") or title)) or f"chapter-{idx + 1}"
        chapters.append({"key": key, "title": title})

    keys = _unique_keys([c["key"] for c in chapters])
    for chapter, key in zip(chapters, keys):
        chapter["key"] = key

    return {
        "name": name,
        "slug": slug,
        "description": description,
        "coverImageURL": str(raw.get("coverImageURL") or ""),
        "roadmap": roadmap,
        "difficultyLevel": difficulty_level,
        "isPremium": False,
        "features": features,
        "credits": [],
        "chapters": chapters,
    }


def normalize_chapter(
    raw: Dict[str, Any],
    *,
    chapter_key: str,
    chapter_title: str,
) -> Dict[str, Any]:
    """Normalize raw chapter JSON, preserving input key/title identity."""
    if not isinstance(raw, dict):
        raw = {}

    content = raw.get("content")
    if not isinstance(content, str) or not content.strip():
        content = (
            f"# {chapter_title}\n\n"
            f"Learn {chapter_title} with practical examples.\n\n"
            f"## Key ideas\n\nCore concepts explained step by step.\n\n"
            f"## Example\n\n```python\n# {chapter_title} example\n"
            f"print('hello')\n```\n"
        )

    return {
        "key": chapter_key,
        "title": chapter_title,
        "content": content,
        "isOptional": bool(raw.get("isOptional", False)),
        "credits": [],
    }
