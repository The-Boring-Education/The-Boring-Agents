"""Generic answer generator for aptitude and basic interview questions."""

from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.agents.interview.generators.base_generator import BaseAnswerGenerator
from src.agents.interview.models import InterviewQuestionResponse


class GenericAnswerGenerator(BaseAnswerGenerator):
    """Generator for generic/aptitude interview questions with basic reasoning."""
    
    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for generic answer generation."""
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
            partial_variables={"format_instructions": self._get_output_parser().get_format_instructions()},
            template="""
You are India's top tech instructor and interviewer with 500+ interviews at companies like FAANG, Indian Unicorns (Flipkart, Razorpay, Swiggy), and MNCs (Microsoft, Oracle, SAP).

**Interview Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

**CRITICAL INSTRUCTION:**
The "answer" field in your JSON response MUST contain the ENTIRE long-form answer below as a single markdown string.
Do NOT summarize. Do NOT shorten. The answer MUST be 800-1500+ words with ALL the sections below.
Use markdown headings (##### ), bullet points, bold, and code blocks for formatting.
Do NOT use emojis anywhere in the response.
Write naturally — avoid generic AI phrases like "Let's dive in", "In conclusion", "It's important to note that", "comprehensive", "robust", "leverage". Write like you are explaining to a friend, not writing a textbook.

---

Write the answer following this EXACT structure (include ALL sections):

##### Answer

A concise 2-3 sentence answer they can say in the first 30 seconds of the interview.

##### Detailed Explanation

- **What is it?** Clear definition in simple terms
- **Why does it exist?** The problem it solves
- **How does it work?** Step-by-step breakdown with technical depth
- Include concrete examples and code snippets where applicable
- Use bullet points for clarity

##### Code Example (if applicable)

Provide a practical code example in a markdown code block showing the concept in action. Include comments explaining each part.

##### Answer at a Glance

List 4-6 important takeaways as bullet points. These should be crisp, memorable facts — not generic filler.

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

List 2-3 follow-up questions the interviewer might ask after this one.

##### Memory Trick

A funny, memorable analogy using relatable context that helps remember the concept.

---

**DATA CONSTRAINTS (CRITICAL):**
- **Frequency**: MUST be one of ["Most Asked", "Asked Frequently", "Asked Sometimes"].
- **Priority**: MUST be one of ["High", "Medium", "Low"].
- **Company Types**: List of strings.

**REMINDER:** The "answer" field must contain the FULL markdown-formatted response with ALL sections above. Minimum 800 words. Do NOT truncate or summarize. Do NOT use emojis.

{format_instructions}
"""
        )

    def _get_output_parser(self) -> PydanticOutputParser:
        """Get the output parser for generic questions."""
        return PydanticOutputParser(pydantic_object=InterviewQuestionResponse)
    
    def _get_answer_structure(self) -> Dict[str, str]:
        """Get the expected answer structure for generic questions."""
        return {
            "Quick Answer": "Quick Answer",
            "Introduction": "Introduction",
            "Basic Reasoning": "Basic Reasoning",
            "Why This Concept Matters": "Why This Concept Matters",
            "Interview Pro Tips": "Interview Pro Tips"
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict:
        """Generate content based on type."""
        if content_type == "answer":
            answer = self.generate_answer(
                question=kwargs.get("question", ""),
                topic=kwargs.get("topic", ""),
                difficulty=kwargs.get("difficulty", "Medium"),
                frequency=kwargs.get("frequency", "Asked Sometimes"),
                priority=kwargs.get("priority", "Medium"),
                company_types=kwargs.get("company_types", ["Startup", "MNC"])
            )
            return {
                "status": "success",
                "answer": answer,
                "content_type": "answer"
            }
        else:
            raise ValueError(f"Unknown content type: {content_type}")

