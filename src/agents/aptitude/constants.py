"""Aptitude topic definitions and category mappings.

Source of truth for all aptitude categories, subcategories, and topics.
Must stay in sync with TBE-Web's APTITUDE_TOPICS constant in lib/constants/api.ts.
When adding a new topic, update BOTH this file and TBE-Web.
"""

from typing import Dict, List, Any, Optional

SUB_CATEGORY_FORMAT_MAP: Dict[str, str] = {
    "ARITHMETIC_APTITUDE": "SPEED",
    "DATA_INTERPRETATION": "SPEED",
    "VERBAL_ABILITY": "RULES",
    "LOGICAL_REASONING": "SPEED",
    "GD_ROUND": "PERSPECTIVE",
    "HR_INTERVIEW": "BEHAVIORAL",
}

CATEGORY_SUB_CATEGORY_MAP: Dict[str, List[str]] = {
    "QUANTITATIVE": ["ARITHMETIC_APTITUDE", "DATA_INTERPRETATION"],
    "VERBAL": ["VERBAL_ABILITY"],
    "REASONING": ["LOGICAL_REASONING"],
    "INTERVIEW": ["GD_ROUND", "HR_INTERVIEW"],
}

MIN_QUESTIONS_PER_TOPIC = 10

TOPIC_REGISTRY: List[Dict[str, Any]] = [
    # ─── Quantitative > Arithmetic Aptitude ───────────────────────────────
    {"name": "Problem on Trains", "slug": "problem-on-trains", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Time and Distance", "slug": "time-and-distance", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Height and Distance", "slug": "height-and-distance", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Time and Work", "slug": "time-and-work", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Simple Interest", "slug": "simple-interest", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Compound Interest", "slug": "compound-interest", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Profit and Loss", "slug": "profit-and-loss", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Partnership", "slug": "partnership", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Percentage", "slug": "percentage", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Calendar", "slug": "calendar", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Probability", "slug": "probability", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Clocks", "slug": "clocks", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Average", "slug": "average", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Area", "slug": "area", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Volume and Surface Areas", "slug": "volume-and-surface-areas", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Ratio", "slug": "ratio", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Proportion", "slug": "proportion", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Surds and Indices", "slug": "surds-and-indices", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Pipes and Cisterns", "slug": "pipes-and-cisterns", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Races and Games", "slug": "races-and-games", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Logarithms", "slug": "logarithms", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Stocks and Shares", "slug": "stocks-and-shares", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Simplification", "slug": "simplification", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "HCF and LCM", "slug": "hcf-and-lcm", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},

    # ─── Quantitative > Data Interpretation ───────────────────────────────
    {"name": "Table Charts", "slug": "table-charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},
    {"name": "Bar Charts", "slug": "bar-charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},
    {"name": "Pie Charts", "slug": "pie-charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},
    {"name": "Line Charts", "slug": "line-charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},

    # ─── Verbal > Verbal Ability ──────────────────────────────────────────
    {"name": "Spotting Errors", "slug": "spotting-errors", "category": "VERBAL", "subCategory": "VERBAL_ABILITY"},
    {"name": "Synonyms", "slug": "synonyms", "category": "VERBAL", "subCategory": "VERBAL_ABILITY"},
    {"name": "Antonyms", "slug": "antonyms", "category": "VERBAL", "subCategory": "VERBAL_ABILITY"},

    # ─── Reasoning > Logical Reasoning ────────────────────────────────────
    {"name": "Number Series", "slug": "number-series", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Letter and Symbol Series", "slug": "letter-and-symbol-series", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Verbal Classification", "slug": "verbal-classification", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Analogies", "slug": "analogies", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Matching Definition", "slug": "matching-definition", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Logical Games", "slug": "logical-games", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Cause and Effect", "slug": "cause-and-effect", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Statement and Assumption", "slug": "statement-and-assumption", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Logical Distance", "slug": "logical-distance", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Deduction", "slug": "deduction", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Theme Detection", "slug": "theme-detection", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Analyzing Arguments", "slug": "analyzing-arguments", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Logical Problems", "slug": "logical-problems", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Making Judgments", "slug": "making-judgments", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},

    # ─── Interview > GD Round ─────────────────────────────────────────────
    {"name": "Politics", "slug": "politics", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "Economics", "slug": "economics", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "Social Issues", "slug": "social-issues", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "Technology", "slug": "technology", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "General Topics", "slug": "general-topics", "category": "INTERVIEW", "subCategory": "GD_ROUND"},

    # ─── Interview > HR Interview ─────────────────────────────────────────
    {"name": "Self Introduction", "slug": "self-introduction", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Career Goals", "slug": "career-goals", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Work Experience", "slug": "work-experience", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Behavioral Questions", "slug": "behavioral-questions", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Strengths and Weaknesses", "slug": "strengths-and-weaknesses", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "General HR Questions", "slug": "general-hr-questions", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
]

TOPIC_SLUG_SET = frozenset(t["slug"] for t in TOPIC_REGISTRY)

_SLUG_INDEX: Dict[str, Dict[str, Any]] = {t["slug"]: t for t in TOPIC_REGISTRY}
_NAME_INDEX: Dict[str, Dict[str, Any]] = {t["name"].lower(): t for t in TOPIC_REGISTRY}


def get_format_for_sub_category(sub_category: str) -> str:
    """Return the answer format type for a given sub-category."""
    fmt = SUB_CATEGORY_FORMAT_MAP.get(sub_category.upper())
    if not fmt:
        raise ValueError(
            f"Unknown sub-category: {sub_category}. "
            f"Valid: {list(SUB_CATEGORY_FORMAT_MAP.keys())}"
        )
    return fmt


def get_topics_for_sub_category(sub_category: str) -> List[Dict[str, Any]]:
    """Return all topics for a given sub-category."""
    return [
        t for t in TOPIC_REGISTRY
        if t["subCategory"] == sub_category.upper()
    ]


def validate_topic_slug(slug: str) -> bool:
    """Check if a topic slug exists in the registry."""
    return slug in TOPIC_SLUG_SET


def get_topic_by_slug(slug: str) -> Dict[str, Any]:
    """Get full topic info by slug, including derived answerFormatType."""
    topic = _SLUG_INDEX.get(slug)
    if not topic:
        raise ValueError(f"Topic slug not found: {slug}. Check TOPIC_REGISTRY.")
    return {**topic, "answerFormatType": SUB_CATEGORY_FORMAT_MAP[topic["subCategory"]]}


def validate_topic_name(topic_name: str) -> bool:
    """Check if a topic name exists in the registry."""
    return topic_name.lower() in _NAME_INDEX


def get_topic_info(topic_name: str) -> Dict[str, Any]:
    """Get full topic info by name (case-insensitive), including slug and answerFormatType."""
    topic = _NAME_INDEX.get(topic_name.lower())
    if not topic:
        raise ValueError(f"Topic not found: {topic_name}")
    return {**topic, "answerFormatType": SUB_CATEGORY_FORMAT_MAP[topic["subCategory"]]}


def resolve_topic(identifier: str) -> Dict[str, Any]:
    """Resolve a topic by slug or name. Returns full topic info with answerFormatType."""
    if identifier in _SLUG_INDEX:
        return get_topic_by_slug(identifier)
    if identifier.lower() in _NAME_INDEX:
        return get_topic_info(identifier)
    raise ValueError(
        f"Unknown topic: '{identifier}'. Provide a valid slug or name from TOPIC_REGISTRY."
    )
