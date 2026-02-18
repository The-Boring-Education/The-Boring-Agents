"""System Design answer generator for system design interview questions."""

from typing import Dict
from langchain_core.prompts import PromptTemplate

from src.agents.interview.generators.base_generator import BaseAnswerGenerator


class SystemDesignAnswerGenerator(BaseAnswerGenerator):
    """Generator for system design interview questions with reasoning-based answers."""

    def _get_answer_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
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

Create a WORLD-CLASS system design answer with deep reasoning and architectural thinking.

##### 🎯 Direct Answer

Give a concise, high-level answer (2-3 lines) outlining the core architectural approach.

##### 🏗️ System Architecture Overview

**High-Level Design:**
- Core components and their responsibilities
- System boundaries and interfaces
- Key architectural patterns used
- Overall system flow

**Reasoning:**
- Why this architecture was chosen
- Trade-offs considered
- Alternative approaches and why they were rejected

##### 📊 Requirements Analysis

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

##### 🔧 Component Design

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

##### 💾 Data Storage & Management

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

##### ⚡ Scalability & Performance

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

##### 🔒 Reliability & Fault Tolerance

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

##### 🔐 Security Considerations

**Security Measures:**
- Authentication and authorization
- Data encryption
- API security
- DDoS protection

**Reasoning:**
- Security threats addressed
- Security vs performance trade-offs
- Compliance requirements

##### 📈 Real-World Examples

**Indian Tech Company Examples:**
- How Flipkart handles similar challenges
- How Zomato scales their system
- How Paytm ensures reliability
- How Swiggy optimizes performance

**Global Examples:**
- Similar systems at scale
- Lessons learned from industry
- Best practices applied

##### 🎤 Interview Tips

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
- Write like you're mentoring a senior engineer
- Focus on reasoning and trade-offs
- Use diagrams and visual descriptions
- Include specific numbers and metrics
- Be practical and realistic
- Show deep architectural thinking

Make this answer so good that candidates will:
1. Understand the reasoning behind design decisions
2. Learn to think like a system architect
3. Feel confident discussing trade-offs
4. Apply these patterns in real interviews
5. Think "This was totally worth it!"
""",
        )

    def _get_answer_structure(self) -> Dict[str, str]:
        return {
            "Direct Answer": "Direct Answer",
            "System Architecture Overview": "System Architecture Overview",
            "Requirements Analysis": "Requirements Analysis",
            "Component Design": "Component Design",
            "Data Storage": "Data Storage",
            "Scalability": "Scalability",
            "Reliability": "Reliability",
            "Security Considerations": "Security Considerations",
            "Interview Tips": "Interview Tips",
        }
