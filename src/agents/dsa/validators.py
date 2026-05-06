"""Validation and normalization helpers for DSA agent outputs."""

from typing import Any, Dict, List

from src.agents.dsa.schema import (
    ALLOWED_COMPANY_TYPES,
    ALLOWED_DSA_DIFFICULTY,
    ALLOWED_DSA_DOMAIN,
    ALLOWED_DSA_TOPICS,
    COMPANY_ALIAS_MAP,
    TOPIC_ALIAS_MAP,
)


def topic_to_slug(topic: str) -> str:
    """Convert user topic into URL-friendly slug."""
    return "-".join(topic.strip().lower().split())


def topic_to_enum(topic: str) -> str:
    """Convert user topic into uppercase enum-like format."""
    return "_".join(topic.strip().upper().split())


def _as_string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _normalize_domain(values: List[str]) -> List[str]:
    normalized = [value.strip().upper() for value in values if value.strip()]
    valid = [value for value in normalized if value in ALLOWED_DSA_DOMAIN]
    return valid or ["DSA"]


def _normalize_company_types(values: List[str]) -> List[str]:
    normalized = []
    for value in values:
        key = value.strip().lower().replace("-", "_").replace(" ", "_")
        canonical = COMPANY_ALIAS_MAP.get(key)
        if canonical and canonical in ALLOWED_COMPANY_TYPES:
            normalized.append(canonical)
    if not normalized:
        return ["MNC", "FAANG"]
    return list(dict.fromkeys(normalized))


def _normalize_topics(values: List[str], *, topic: str) -> List[str]:
    normalized = []
    for value in values:
        stripped = value.strip()
        if not stripped:
            continue
        alias = TOPIC_ALIAS_MAP.get(stripped.lower())
        topic_enum = alias or topic_to_enum(stripped)
        if topic_enum in ALLOWED_DSA_TOPICS:
            normalized.append(topic_enum)

    if not normalized:
        fallback = TOPIC_ALIAS_MAP.get(topic.strip().lower()) or topic_to_enum(topic)
        if fallback in ALLOWED_DSA_TOPICS:
            normalized = [fallback]
        else:
            normalized = ["ARRAY"]
    return list(dict.fromkeys(normalized))


def _normalize_difficulty(value: str, default_difficulty: str) -> str:
    normalized_default = default_difficulty.upper()
    if normalized_default not in ALLOWED_DSA_DIFFICULTY:
        normalized_default = "MEDIUM"
    candidate = value.upper()
    if candidate in ALLOWED_DSA_DIFFICULTY:
        return candidate
    return normalized_default


def normalize_question(
    item: Dict[str, Any],
    *,
    topic: str,
    index: int,
    force_real_world: bool = False,
    default_difficulty: str = "MEDIUM",
) -> Dict[str, Any]:
    """Normalize one DSA question into the API-compatible shape."""
    topic_enum = topic_to_enum(topic)

    title = str(item.get("title") or f"{topic.title()} Question {index + 1}").strip()
    answer = str(item.get("answer") or "Solution explanation not provided.").strip()
    difficulty = _normalize_difficulty(
        str(item.get("difficulty") or default_difficulty), default_difficulty
    )

    domains = _normalize_domain(_as_string_list(item.get("domain")))
    company_types = _normalize_company_types(_as_string_list(item.get("companyTypes")))
    topics = _normalize_topics(_as_string_list(item.get("topics")) or [topic_enum], topic=topic)

    resources = item.get("resources") if isinstance(item.get("resources"), dict) else {}
    sections = item.get("sections") if isinstance(item.get("sections"), dict) else {}

    normalized = {
        "title": title,
        "answer": answer,
        "difficulty": difficulty,
        "domain": domains,
        "companyTypes": company_types,
        "topics": topics,
        "isRealWorldProblem": bool(item.get("isRealWorldProblem", False)),
        "resources": {
            "youtubeURL": str(resources.get("youtubeURL") or ""),
            "leetcodeURL": str(resources.get("leetcodeURL") or ""),
            "blogURL": str(resources.get("blogURL") or ""),
        },
        "sections": {
            "first_principles": sections.get(
                "first_principles",
                {
                    "paragraphs": [
                        f"Use {topic.title()} fundamentals to reason from constraints before coding."
                    ],
                    "key_observation": f"Model the {topic.lower()} pattern first, then optimize.",
                },
            ),
            "examples": sections.get(
                "examples",
                [
                    {
                        "label": "Example 1",
                        "input": "sample input",
                        "output": "sample output",
                        "explanation": "Walk through the logic with the core pattern.",
                        "step_by_step": ["Understand input", "Apply pattern", "Return answer"],
                    }
                ],
            ),
            "ways_to_solve": sections.get(
                "ways_to_solve",
                [
                    {
                        "approach_number": 1,
                        "name": "Optimal pattern-based approach",
                        "description": "Use a focused data-structure strategy for this topic.",
                        "time_complexity": "O(n)",
                        "time_reason": "Single pass across input.",
                        "space_complexity": "O(n)",
                        "space_reason": "Auxiliary structure for lookups.",
                        "verdict": "optimal",
                        "verdict_label": "Optimal",
                    }
                ],
            ),
            "working_code": sections.get(
                "working_code",
                {
                    "default_language": "python",
                    "languages": {
                        "python": {
                            "code": "def solve(nums):\n    # implement topic pattern\n    return nums"
                        }
                    },
                },
            ),
        },
    }

    if force_real_world:
        normalized["isRealWorldProblem"] = True

    return normalized


def normalize_questions(
    questions: List[Dict[str, Any]],
    *,
    topic: str,
    question_count: int,
    include_real_world: bool,
    difficulty: str,
) -> List[Dict[str, Any]]:
    """Normalize list of questions and enforce real-world defaults."""
    normalized: List[Dict[str, Any]] = []
    for idx in range(question_count):
        source = questions[idx] if idx < len(questions) and isinstance(questions[idx], dict) else {}
        force_real_world = include_real_world and idx == 0
        normalized.append(
            normalize_question(
                source,
                topic=topic,
                index=idx,
                force_real_world=force_real_world,
                default_difficulty=difficulty,
            )
        )

    if include_real_world:
        # Mark roughly 20% as real-world, minimum 1.
        step = max(1, question_count // 5)
        for idx in range(0, question_count, step):
            normalized[idx]["isRealWorldProblem"] = True

    return normalized


def normalize_study_guide(
    study_guide: Dict[str, Any],
    *,
    topic: str,
    question_titles: List[str],
) -> Dict[str, Any]:
    """Normalize DSA study guide into expected structure."""
    slug = topic_to_slug(topic)
    base_title = f"{topic.title()} - Complete Study Guide"

    sections = study_guide.get("sections") if isinstance(study_guide.get("sections"), list) else []
    if not sections:
        sections = [
            {
                "type": "intro",
                "sortOrder": 1,
                "content": {
                    "pageTitle": f"{topic.title()} Intro",
                    "subtitle": "Start here",
                    "openingParagraph": f"Learn {topic.title()} from first principles to interview-level confidence.",
                    "prereqCards": [],
                    "callouts": [],
                    "howToUseHeading": "How to use this guide",
                    "howToUseParagraphs": [
                        "Read concepts first, then pattern section, then practice from cheatsheet groups.",
                    ],
                },
            },
            {
                "id": None,
                "label": "Concepts",
                "type": "concept",
                "isDivider": False,
                "dividerLabel": None,
                "sortOrder": 2,
                "content": {
                    "pageTitle": f"{topic.title()} Core Concepts",
                    "subtitle": "Important building blocks",
                    "subsections": [
                        {
                            "subheading": "Core idea",
                            "bodyText": f"Understand the key invariant for {topic.title()} problems.",
                            "tableData": None,
                            "codeBlocks": [],
                            "sortOrder": 1,
                        }
                    ],
                },
            },
            {
                "id": None,
                "label": "Patterns",
                "type": "pattern",
                "isDivider": False,
                "dividerLabel": None,
                "sortOrder": 3,
                "content": {
                    "pageTitle": f"{topic.title()} Patterns",
                    "subtitle": "When to use which pattern",
                    "whatIsIt": "A reusable solving strategy.",
                    "triggerPhrases": ["find", "optimize", "track"],
                    "whenNotToUse": "When constraints require a different paradigm.",
                    "codeTemplates": [],
                    "visualAscii": None,
                    "workedExample": {
                        "problemTitle": question_titles[0] if question_titles else f"{topic.title()} Example",
                        "problemStatement": "Solve the example using the chosen pattern.",
                        "inputExample": "Input: [sample]",
                        "outputExample": "Output: [result]",
                        "bruteForceDesc": "Try all possibilities first as baseline.",
                        "coreTrick": "Preserve the core invariant while iterating.",
                        "dryRunSteps": [],
                        "solutionCode": [],
                        "timeComplexity": "O(n)",
                        "timeReason": "Single pass over input",
                        "spaceComplexity": "O(n)",
                        "spaceReason": "Auxiliary structure",
                        "leetcodeUrl": "",
                        "youtubeSearch": "",
                    },
                    "practiceQuestions": [],
                },
            },
            {
                "id": None,
                "label": "Cheatsheet",
                "type": "cheatsheet",
                "isDivider": False,
                "dividerLabel": None,
                "sortOrder": 4,
                "content": {
                    "pageTitle": f"{topic.title()} Cheatsheet",
                    "subtitle": "Quick recall",
                    "patternRows": [],
                    "decisionGuide": "Map constraints to the simplest valid pattern.",
                    "questionGroups": [],
                    "oneThingToRemember": [
                        "State and protect your invariant before coding."
                    ],
                },
            },
        ]

        sections[0].update(
            {
                "id": None,
                "label": "Intro",
                "isDivider": False,
                "dividerLabel": None,
            }
        )

    return {
        "topicId": str(study_guide.get("topicId") or slug),
        "title": str(study_guide.get("title") or base_title),
        "hasGuide": bool(study_guide.get("hasGuide", True)),
        "sections": sections,
    }
