"""Tech answer generator for technology-specific interview questions."""

from typing import Dict, Optional, List
from langchain_core.prompts import PromptTemplate

from src.agents.interview.generators.base_generator import BaseAnswerGenerator
from langchain_core.output_parsers import PydanticOutputParser
from src.agents.interview.models import InterviewQuestionResponse


class TechAnswerGenerator(BaseAnswerGenerator):
    """Generator for technology-specific interview questions with code examples."""
    
    def __init__(self, technology: Optional[str] = None, **kwargs):
        """Initialize tech answer generator.
        
        Args:
            technology: Technology name (e.g., "React", "Python", "Node.js")
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.technology = technology or "General Tech"
        # Store technology in custom_params for compatibility
        self.custom_params['technology'] = self.technology
    
    def _get_output_parser(self) -> Optional[PydanticOutputParser]:
        """Get output parser for tech answers."""
        return PydanticOutputParser(pydantic_object=InterviewQuestionResponse)

    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for tech answer generation."""
        technology = self.technology or "General Tech"
        
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types", "format_instructions"],
            template=f"""
You are a Senior Tech Interviewer and Expert Software Engineer with 10+ years of experience in {technology} and the Indian tech industry.

**Question**: {{question}}
**Topic**: {{topic}}
**Technology**: {technology}
**Difficulty**: {{difficulty}}
**Frequency**: {{frequency}}
**Priority**: {{priority}}
**Company Types**: {{company_types}}

**CRITICAL INSTRUCTION:**
The "answer" field in your JSON response MUST contain the ENTIRE long-form answer as a single markdown string.
Do NOT summarize. Do NOT shorten. The answer MUST be 800-1500+ words with ALL sections below.
Use markdown headings (##### ), bullet points, bold text, and code blocks for formatting.
Do NOT use emojis anywhere in the response.
Write naturally — avoid generic AI phrases like "Let's dive in", "In conclusion", "It's important to note that", "It's worth mentioning", "comprehensive", "robust", "leverage", "utilize". Write like a senior engineer explaining to a colleague, not like a textbook.

---

Write the answer following this EXACT structure (include ALL sections in the "answer" field):

##### Answer

A confident 2-3 sentence answer that directly addresses the question. This is what the interviewer wants to hear first.

##### Detailed Explanation

- **What is it?** Clear definition with precise technical terminology
- **How it works internally:** Go beyond surface-level. Explain the internal mechanism, architecture, or algorithm
- **Where and why is this used?** Practical use cases, performance implications, trade-offs, and when to use vs. alternatives
- Use analogies for complex topics where helpful
- 2-3 substantial paragraphs of solid technical prose

##### Code Example

Provide production-grade code in a markdown code block:
- Add concise comments explaining complex logic
- Show realistic usage context, not toy examples
- If comparing approaches, show both (e.g., class vs hooks, callback vs async/await)

##### Answer at a Glance

4-6 crisp bullet points that summarize the core takeaways:
- Performance implications / Time Complexity
- Trade-offs (Pros/Cons)
- Edge cases and gotchas
- Common mistakes developers make

##### Real-World Context

How this applies in real products and companies:
- Relate to real scenarios (handling high traffic, payment flows, real-time systems, etc.)
- Why companies care about this in production

##### How Interviewers Ask This

1. [First variation of how this question is commonly phrased]
2. [Second variation]
3. [Third variation]

##### Interview Tips

**What to say:**
- Key concepts interviewers want to hear
- How to structure your verbal answer

**What NOT to say:**
- Common mistakes and misconceptions
- Red flags that hurt your impression

##### Follow-up Questions to Prepare

List 2-3 likely follow-up questions the interviewer will ask next.

---

**DATA CONSTRAINTS (CRITICAL):**
- **Frequency**: MUST be one of ["Most Asked", "Asked Frequently", "Asked Sometimes"]. Do NOT use other values.
- **Priority**: MUST be one of ["High", "Medium", "Low"].
- **Company Types**: List of strings.

**REMINDER:** The "answer" field must contain the FULL markdown-formatted response with ALL sections above. Minimum 800 words. Do NOT truncate or summarize into a short paragraph. Do NOT use emojis.

**FORMAT INSTRUCTIONS:**
{{format_instructions}}
"""
        )
    
    def generate_answer(
        self,
        question: str,
        topic: str,
        difficulty: str = "Medium",
        frequency: str = "Asked Sometimes",
        priority: str = "Medium",
        company_types: Optional[List[str]] = None,
        technology: Optional[str] = None
    ) -> InterviewQuestionResponse:
        """Generate a tech-specific answer.
        
        Args:
            question: The interview question
            topic: Topic/subject area
            difficulty: Difficulty level
            frequency: How often the question is asked
            priority: Priority level
            company_types: Types of companies that ask this question
            technology: Technology name (overrides instance technology if provided)
            
        Returns:
            InterviewQuestionResponse object
        """
        # Use provided technology or fall back to instance technology
        tech = technology or self.technology or "General Tech"
        if tech != self.technology:
            self.technology = tech
            self.custom_params['technology'] = tech
        
        return super().generate_answer(
            question=question,
            topic=topic,
            difficulty=difficulty,
            frequency=frequency,
            priority=priority,
            company_types=company_types
        )
    
    def generate_content(self, content_type: str, **kwargs) -> Dict:
        """Generate content based on type."""
        if content_type == "answer":
            answer = self.generate_answer(
                question=kwargs.get("question", ""),
                topic=kwargs.get("topic", ""),
                difficulty=kwargs.get("difficulty", "Medium"),
                frequency=kwargs.get("frequency", "Asked Sometimes"),
                priority=kwargs.get("priority", "Medium"),
                company_types=kwargs.get("company_types", ["Startup", "MNC"]),
                technology=kwargs.get("technology", self.technology)
            )
            return {
                "status": "success",
                "answer": answer,
                "content_type": "answer"
            }
        else:
            raise ValueError(f"Unknown content type: {content_type}")

