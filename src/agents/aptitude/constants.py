"""Aptitude topic definitions and category mappings.

Source of truth for all aptitude categories, subcategories, and topics.
The agent uses this to validate input and determine the answer format.
"""

from typing import Dict, List, Any

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

TOPIC_REGISTRY: List[Dict[str, Any]] = [
    # ─── Quantitative > Arithmetic Aptitude ───────────────────────────────
    {"name": "Problem on Trains", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Time and Distance", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Height and Distance", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Time and Work", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Simple Interest", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Compound Interest", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Profit and Loss", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Partnership", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Percentage", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Calendar", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Probability", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Clocks", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Average", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Area", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Volume and Surface Areas", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Ratio", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Proportion", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Surds and Indices", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Pipes and Cisterns", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Races and Games", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Logarithms", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Stocks and Shares", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "Simplification", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},
    {"name": "HCF and LCM", "category": "QUANTITATIVE", "subCategory": "ARITHMETIC_APTITUDE"},

    # ─── Quantitative > Data Interpretation ───────────────────────────────
    {"name": "Table Charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},
    {"name": "Bar Charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},
    {"name": "Pie Charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},
    {"name": "Line Charts", "category": "QUANTITATIVE", "subCategory": "DATA_INTERPRETATION"},

    # ─── Verbal > Verbal Ability ──────────────────────────────────────────
    {"name": "Spotting Errors", "category": "VERBAL", "subCategory": "VERBAL_ABILITY"},
    {"name": "Synonyms", "category": "VERBAL", "subCategory": "VERBAL_ABILITY"},
    {"name": "Antonyms", "category": "VERBAL", "subCategory": "VERBAL_ABILITY"},

    # ─── Reasoning > Logical Reasoning ────────────────────────────────────
    {"name": "Number Series", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Letter and Symbol Series", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Verbal Classification", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Analogies", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Matching Definition", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Logical Games", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Cause and Effect", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Statement and Assumption", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Logical Distance", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Deduction", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Theme Detection", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Analyzing Arguments", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Logical Problems", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},
    {"name": "Making Judgments", "category": "REASONING", "subCategory": "LOGICAL_REASONING"},

    # ─── Interview > GD Round ─────────────────────────────────────────────
    {"name": "Politics", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "Economics", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "Social Issues", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "Technology", "category": "INTERVIEW", "subCategory": "GD_ROUND"},
    {"name": "General Topics", "category": "INTERVIEW", "subCategory": "GD_ROUND"},

    # ─── Interview > HR Interview ────────────────────────────────────────
    {"name": "Self Introduction", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Career Goals", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Work Experience", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Behavioral Questions", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "Strengths and Weaknesses", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
    {"name": "General HR Questions", "category": "INTERVIEW", "subCategory": "HR_INTERVIEW"},
]


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


def validate_topic_name(topic_name: str) -> bool:
    """Check if a topic name exists in the registry."""
    return any(t["name"].lower() == topic_name.lower() for t in TOPIC_REGISTRY)


def get_topic_info(topic_name: str) -> Dict[str, Any]:
    """Get full topic info by name (case-insensitive)."""
    for t in TOPIC_REGISTRY:
        if t["name"].lower() == topic_name.lower():
            return {**t, "answerFormatType": SUB_CATEGORY_FORMAT_MAP[t["subCategory"]]}
    raise ValueError(f"Topic not found: {topic_name}")
