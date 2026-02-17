"""System Design answer generator for system design interview questions."""

from typing import Dict, Optional, List, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.agents.interview.generators.base_generator import BaseAnswerGenerator
from src.agents.interview.models import InterviewQuestionResponse


class SystemDesignAnswerGenerator(BaseAnswerGenerator):
    """Generator for system design interview questions with reasoning-based answers."""
    
    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for system design answer generation."""
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
            partial_variables={"format_instructions": self._get_output_parser().get_format_instructions()},
            template="""
You are a Senior System Design Architect and Expert with 10+ years of experience designing scalable systems at companies like:
- FAANG (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**System Design Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

**DATA CONSTRAINTS (CRITICAL):**
- **Frequency**: MUST be one of ["Most Asked", "Asked Frequently", "Asked Sometimes"].
- **Priority**: MUST be one of ["High", "Medium", "Low"].
- **Company Types**: List of strings.

Create a detailed system design answer with deep reasoning and architectural thinking.

**CRITICAL INSTRUCTION:**
The "answer" field in your JSON response MUST contain the ENTIRE long-form answer below as a single markdown string.
Do NOT summarize. Do NOT shorten. The answer MUST be 1000-2000+ words with ALL the sections below.
Use markdown headings (##### ), bullet points, bold, and code blocks for formatting.
Do NOT use emojis anywhere in the response.
Write naturally — avoid generic AI phrases like "Let's dive in", "In conclusion", "comprehensive", "robust". Write like a senior architect explaining to a colleague.

##### Answer

Give a concise, high-level answer (2-3 lines) outlining the core architectural approach.

##### System Architecture Overview

**High-Level Design:**
- Core components and their responsibilities
- System boundaries and interfaces
- Key architectural patterns used
- Overall system flow

**Reasoning:**
- Why this architecture was chosen
- Trade-offs considered
- Alternative approaches and why they were rejected

##### Requirements Analysis

**Functional Requirements:**
- What the system must do
- Key features and capabilities
- User interactions and workflows

**Non-Functional Requirements:**
- Scalability requirements
- Performance expectations
- Availability and reliability needs
- Consistency requirements

**Reasoning:**
- How requirements influence design decisions
- Priority of different requirements
- Constraints and assumptions

##### Component Design

**Core Components:**
- Detailed design of each major component
- Data models and schemas
- APIs and interfaces
- Component interactions

**Reasoning:**
- Why each component is necessary
- How components work together
- Design patterns applied
- Separation of concerns

##### Data Storage and Management

**Database Design:**
- Data models and schemas
- Database selection (SQL vs NoSQL)
- Data partitioning and sharding strategies
- Replication and consistency models

**Caching Strategy:**
- What to cache and why
- Cache invalidation strategies
- Cache layers and hierarchies

**Reasoning:**
- Why specific storage solutions were chosen
- Trade-offs between consistency and availability
- Scalability considerations

##### Scalability and Performance

**Scaling Strategies:**
- Horizontal vs vertical scaling
- Load balancing approaches
- Database scaling techniques
- CDN and edge caching

**Performance Optimization:**
- Bottleneck identification
- Optimization techniques
- Monitoring and metrics

**Reasoning:**
- How system handles growth
- Performance vs cost trade-offs
- When to scale different components

##### Reliability and Fault Tolerance

**High Availability:**
- Redundancy strategies
- Failover mechanisms
- Disaster recovery plans

**Error Handling:**
- Failure scenarios
- Graceful degradation
- Circuit breakers and retries

**Reasoning:**
- Why specific reliability patterns were chosen
- Cost vs reliability trade-offs
- Failure mode analysis

##### Security Considerations

**Security Measures:**
- Authentication and authorization
- Data encryption
- API security
- DDoS protection

**Reasoning:**
- Security threats addressed
- Security vs performance trade-offs
- Compliance requirements

##### Real-World Examples

**Indian Tech Company Examples:**
- How Flipkart handles similar challenges
- How Zomato scales their system
- How Paytm ensures reliability
- How Swiggy optimizes performance

**Global Examples:**
- Similar systems at scale
- Lessons learned from industry
- Best practices applied

##### Interview Tips

**How to Approach:**
- Step-by-step interview strategy
- What interviewers are looking for
- Common follow-up questions
- How to demonstrate reasoning

**Key Points to Emphasize:**
- Trade-off analysis
- Scalability thinking
- Real-world constraints
- Continuous improvement mindset

## Writing Style:
- Write like you are mentoring a senior engineer colleague
- Focus on reasoning and trade-offs
- Include specific numbers and metrics where applicable
- Be practical and realistic
- Show deep architectural thinking

**REMINDER:** The "answer" field must contain the FULL markdown-formatted response with ALL sections above. Minimum 1000 words. Do NOT truncate or summarize. Do NOT use emojis.

{format_instructions}
"""
        )

    def _get_output_parser(self) -> PydanticOutputParser:
        """Get the output parser for system design questions."""
        return PydanticOutputParser(pydantic_object=InterviewQuestionResponse)
    
    def _get_answer_structure(self) -> Dict[str, str]:
        """Get the expected answer structure for system design questions."""
        return {
            "Direct Answer": "Direct Answer",
            "System Architecture Overview": "System Architecture Overview",
            "Requirements Analysis": "Requirements Analysis",
            "Component Design": "Component Design",
            "Data Storage": "Data Storage",
            "Scalability": "Scalability",
            "Reliability": "Reliability",
            "Security Considerations": "Security Considerations",
            "Interview Tips": "Interview Tips"
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

