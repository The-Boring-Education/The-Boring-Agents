"""Shared utilities for interview prep agent.

Contains:
- Schema constants and validation (matching Mongoose models)
- QuestionGenerator — LLM-based question generation
- MetadataGenerator — LLM-based sheet/question metadata generation
"""

from typing import Any, Dict, List, Optional

from langchain_core.prompts import PromptTemplate
from slugify import slugify

from src.agents.base import BaseAgent

# ---------------------------------------------------------------------------
# Schema constants (matching TypeScript Mongoose enums)
# ---------------------------------------------------------------------------

ROADMAPS: List[str] = ["Frontend", "Backend", "Fullstack", "Tech"]
INTERVIEW_QUESTION_FREQUENCY: List[str] = ["Most Asked", "Asked Frequently", "Asked Sometimes"]
PRIORITY_LEVELS: List[str] = ["High", "Medium", "Low"]
COMPANY_TYPES: List[str] = ["Startup", "MidSize", "MNC", "FAANG"]


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def generate_slug(name: str) -> str:
    return slugify(name, lowercase=True)


def generate_cover_image_url(topic: Optional[str] = None) -> str:
    return "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=800&h=400&fit=crop&crop=center&q=80"


def validate_roadmap(roadmap: str) -> bool:
    return roadmap in ROADMAPS


def validate_frequency(frequency: str) -> bool:
    return frequency in INTERVIEW_QUESTION_FREQUENCY


def validate_priority(priority: str) -> bool:
    return priority in PRIORITY_LEVELS


def validate_company_types(company_types: List[str]) -> bool:
    return all(ct in COMPANY_TYPES for ct in company_types)


def get_schema_defaults() -> Dict[str, Any]:
    return {
        "isPremium": False,
        "price": 0,
        "discountPercentage": 0,
        "appliedCoupon": None,
        "features": [],
        "resources": [],
    }


def transform_to_camel_case(field_name: str) -> str:
    parts = field_name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def validate_sheet_structure(sheet_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    errors: List[str] = []
    for field in ("name", "slug", "description", "coverImageURL", "liveOn", "roadmap"):
        if field not in sheet_data:
            errors.append(f"Missing required field: {field}")
    if "roadmap" in sheet_data and not validate_roadmap(sheet_data["roadmap"]):
        errors.append(f"Invalid roadmap value: {sheet_data['roadmap']}. Must be one of {ROADMAPS}")
    for i, q in enumerate(sheet_data.get("questions", [])):
        errors.extend(validate_question_structure(q, i))
    return len(errors) == 0, errors


def validate_question_structure(question: Dict[str, Any], index: int = 0) -> List[str]:
    errors: List[str] = []
    for field in ("title", "question", "answer", "frequency", "priority"):
        if field not in question:
            errors.append(f"Question {index}: Missing required field: {field}")
    if "title" in question and len(question["title"]) > 100:
        errors.append(f"Question {index}: Title exceeds 100 characters")
    if "frequency" in question and not validate_frequency(question["frequency"]):
        errors.append(f"Question {index}: Invalid frequency value: {question['frequency']}")
    if "priority" in question and not validate_priority(question["priority"]):
        errors.append(f"Question {index}: Invalid priority value: {question['priority']}")
    if "companyTypes" in question:
        if not isinstance(question["companyTypes"], list):
            errors.append(f"Question {index}: companyTypes must be a list")
        elif not validate_company_types(question["companyTypes"]):
            errors.append(f"Question {index}: Invalid companyTypes values")
    if "resources" in question:
        if not isinstance(question["resources"], list):
            errors.append(f"Question {index}: resources must be a list")
        else:
            for r_idx, resource in enumerate(question["resources"]):
                if not isinstance(resource, dict):
                    errors.append(f"Question {index}, Resource {r_idx}: must be a dictionary")
                elif "type" not in resource or "url" not in resource:
                    errors.append(f"Question {index}, Resource {r_idx}: missing type or url")
    return errors


# ---------------------------------------------------------------------------
# QuestionGenerator
# ---------------------------------------------------------------------------

class QuestionGenerator(BaseAgent):
    """Generates interview questions via LLM based on sheet parameters."""

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "generate_questions": PromptTemplate(
                input_variables=["name", "description", "agent_type", "question_count", "roadmap"],
                template="""
You are an expert interview question generator for The Boring Education. Generate comprehensive interview questions based on the following requirements.

**Sheet Name:** {name}
**Description:** {description}
**Agent Type:** {agent_type}
**Question Count:** {question_count}
**Roadmap:** {roadmap}

Based on the requirements, generate a comprehensive list of interview questions that:
1. Cover all the topics mentioned in the description
2. Follow the difficulty distribution (Easy/Medium/Hard)
3. Are relevant for Indian tech companies and job market
4. Include practical, real-world scenarios
5. Test both conceptual understanding and implementation skills
6. Are suitable for the target audience mentioned
7. Match the style of {agent_type} questions

For {agent_type} questions:
- Generic: Focus on aptitude, reasoning, and basic concepts
- DSA: Include stepwise problems, real-world examples, not pure Leetcode style
- Tech: Include code examples and technology-specific concepts
- System Design: Focus on reasoning, architecture, and scalability

Please generate questions in a numbered list format:
1. [Question 1]
2. [Question 2]
3. [Question 3]
...and so on

Generate exactly {question_count} questions covering all the topics comprehensively. Make sure questions are:
- Clear and specific
- Interview-appropriate
- Practical and job-relevant
- Covering different difficulty levels
- Technology-specific where applicable

Questions:
""",
            )
        }

    def generate_content(self, content_type: str = "generate_questions", **kwargs) -> Dict[str, Any]:
        if content_type == "generate_questions":
            return self.generate_questions(
                name=kwargs.get("name", ""),
                description=kwargs.get("description", ""),
                agent_type=kwargs.get("agent_type", "generic"),
                question_count=kwargs.get("question_count", 20),
                roadmap=kwargs.get("roadmap", "Tech"),
            )
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_questions(
        self, name: str, description: str, agent_type: str, question_count: int = 20, roadmap: str = "Tech",
    ) -> List[str]:
        prompt = self._format_prompt(
            "generate_questions", name=name, description=description,
            agent_type=agent_type, question_count=question_count, roadmap=roadmap,
        )
        result = self._generate_with_prompt(prompt)
        return self._parse_questions(result, question_count)

    @staticmethod
    def _parse_questions(text: str, max_questions: int) -> List[str]:
        questions: List[str] = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit():
                for i, ch in enumerate(line):
                    if ch in (".", ")", "-") and i > 0:
                        q = line[i + 1:].strip()
                        break
                else:
                    q = line
            elif line.startswith("-"):
                q = line[1:].strip()
            else:
                continue
            if q and len(q) > 10:
                questions.append(q)
                if len(questions) >= max_questions:
                    break
        return questions[:max_questions]


# ---------------------------------------------------------------------------
# MetadataGenerator
# ---------------------------------------------------------------------------

class MetadataGenerator(BaseAgent):
    """Generates sheet and question metadata via LLM."""

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        return {
            "sheet_meta": PromptTemplate(
                input_variables=["name", "description", "roadmap"],
                template="""
Generate comprehensive metadata content for an interview sheet.

**Sheet Name:** {name}
**Description:** {description}
**Roadmap:** {roadmap}

Create engaging metadata that:
1. Summarizes what the sheet covers
2. Highlights key topics and technologies
3. Explains the value for interview preparation
4. Mentions target audience and difficulty level
5. Includes real-world application context

Keep it concise (150-200 words), engaging, and professional.

Metadata:
""",
            ),
            "question_metadata": PromptTemplate(
                input_variables=["question", "topic", "context"],
                template="""
You are an expert interview question analyst with 20+ years of experience in tech hiring. Analyze the following interview question and provide appropriate metadata.

**Question:** {question}
**Topic:** {topic}
**Context:** {context}

Based on your extensive experience, determine:

1. **Frequency**: How often this question is asked in interviews
   - "Most Asked" (asked in 80%+ of interviews)
   - "Asked Frequently" (asked in 50-80% of interviews)
   - "Asked Sometimes" (asked in 20-50% of interviews)

2. **Priority**: How important this question is for interview success
   - "High" (critical for passing the interview)
   - "Medium" (important but not critical)
   - "Low" (nice to know but not essential)

3. **Company Types**: Which types of companies typically ask this question (can select multiple)
   - "Startup" (early-stage companies, fast-paced)
   - "MidSize" (growing companies, established processes)
   - "MNC" (multinational corporations, formal processes)
   - "FAANG" (top tech companies, high standards)

Provide your analysis in this exact format:
Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
Priority: [High/Medium/Low]
Company Types: [Startup, MidSize, MNC, FAANG] (select relevant ones, comma-separated)
""",
            ),
        }

    def generate_content(self, content_type: str = "sheet_meta", **kwargs) -> Dict[str, Any]:
        if content_type == "sheet_meta":
            return self.generate_sheet_meta(
                name=kwargs.get("name", ""), description=kwargs.get("description", ""),
                roadmap=kwargs.get("roadmap", "Tech"),
            )
        if content_type == "question_metadata":
            return self.generate_question_metadata(
                question=kwargs.get("question", ""), topic=kwargs.get("topic", ""),
                context=kwargs.get("context", ""),
            )
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_sheet_meta(self, name: str, description: str, roadmap: str = "Tech") -> str:
        prompt = self._format_prompt("sheet_meta", name=name, description=description, roadmap=roadmap)
        return self._generate_with_prompt(prompt).strip()

    def generate_question_metadata(self, question: str, topic: str, context: str = "") -> Dict[str, Any]:
        prompt = self._format_prompt("question_metadata", question=question, topic=topic, context=context)
        result = self._generate_with_prompt(prompt)
        metadata = self._parse_metadata_result(result)
        if not validate_frequency(metadata["frequency"]):
            metadata["frequency"] = "Asked Sometimes"
        if not validate_priority(metadata["priority"]):
            metadata["priority"] = "Medium"
        if not validate_company_types(metadata["companyTypes"]):
            metadata["companyTypes"] = ["Startup", "MNC"]
        return metadata

    @staticmethod
    def _parse_metadata_result(result: str) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {"frequency": "Asked Sometimes", "priority": "Medium", "companyTypes": ["Startup", "MNC"]}
        for line in result.split("\n"):
            line = line.strip()
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key, value = key.strip().lower(), value.strip()
            if key == "frequency" and value in INTERVIEW_QUESTION_FREQUENCY:
                metadata["frequency"] = value
            elif key == "priority" and value in PRIORITY_LEVELS:
                metadata["priority"] = value
            elif key == "company types":
                valid = [ct.strip() for ct in value.split(",") if ct.strip() in COMPANY_TYPES]
                if valid:
                    metadata["companyTypes"] = valid
        return metadata
