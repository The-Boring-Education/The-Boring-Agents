"""Tech answer generator for technology-specific interview questions."""

from typing import Dict, Optional, List
from langchain_core.prompts import PromptTemplate

from src.agents.interview.generators.base_generator import BaseAnswerGenerator


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
    
    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for tech answer generation."""
        technology = self.technology or "General Tech"
        indian_context = self._get_indian_context(technology)
        
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
            template=f"""
You are a Senior Tech Interviewer and Expert Software Engineer with 10+ years of experience in {technology} and the Indian tech industry.

Create a comprehensive, interview-ready answer for this {technology} question:

**Question**: {{question}}
**Topic**: {{topic}}
**Technology**: {technology}
**Difficulty**: {{difficulty}}
**Frequency**: {{frequency}}
**Priority**: {{priority}}
**Company Types**: {{company_types}}

**ANSWER REQUIREMENTS:**

##### 🎯 Direct Answer

Give the most direct, crisp answer first (2-3 lines). What an interviewer wants to hear immediately.

##### 💡 Concept Explanation

- Explain the core concept clearly
- Use simple language that a fresher can understand
- Add {technology}-specific context and terminology

##### 🔧 Practical Implementation

- Provide clean, production-ready code examples
- Include best practices for {technology}
- Show multiple approaches when applicable
- Add proper error handling and edge cases

##### 🌍 Real-World Applications

- Indian company examples (Flipkart, Zomato, Paytm, etc.)
- Industry use cases specific to {technology}
- Performance considerations and optimization

##### ⚠️ Common Pitfalls & Best Practices

- What NOT to do (common mistakes)
- {technology}-specific anti-patterns
- Security considerations
- Performance gotchas

##### 🚀 Advanced Concepts

- Latest {technology} features and updates
- Enterprise-level considerations
- Scalability patterns
- Integration with other technologies

##### 🎤 Interview Tips

- How to approach this question in an interview
- What interviewers are really testing
- Follow-up questions to expect
- Confidence-building talking points

## 🎨 FORMATTING REQUIREMENTS

- Use emojis for section headers
- Include code blocks with proper syntax highlighting for {technology}
- Add Indian context where relevant ({indian_context})
- Make it engaging but professional
- Include memory tricks or mnemonics where helpful

## 🔍 TECHNOLOGY-SPECIFIC REQUIREMENTS

For {technology}:
- Include latest best practices and patterns
- Cover framework/library-specific features
- Add ecosystem-related questions (tools, packages, etc.)
- Include deployment and DevOps considerations if relevant
- Mention version-specific differences when important

## 📈 DIFFICULTY ADAPTATION

**Easy Questions**: Focus on fundamentals, basic syntax, core concepts
**Medium Questions**: Include practical examples, design patterns, trade-offs
**Hard Questions**: Cover advanced topics, performance optimization, architecture

## 🇮🇳 INDIAN TECH CONTEXT

- Use examples from Indian startups and companies
- Include relevant Indian tech scenarios
- Consider cost-effectiveness and resource constraints
- Add cultural context where appropriate

Write the answer in a way that helps the candidate:
1. **Understand** the concept deeply
2. **Implement** it practically 
3. **Explain** it confidently in interviews
4. **Remember** it easily

Make it comprehensive yet concise, technical yet accessible.
"""
        )
    
    def _get_answer_structure(self) -> Dict[str, str]:
        """Get the expected answer structure for tech questions."""
        return {
            "Direct Answer": "Direct Answer",
            "Concept Explanation": "Concept Explanation",
            "Practical Implementation": "Practical Implementation",
            "Real-World Applications": "Real-World Applications",
            "Common Pitfalls": "Common Pitfalls",
            "Interview Tips": "Interview Tips"
        }
    
    def _get_indian_context(self, technology: str) -> str:
        """Get Indian tech industry context for the technology."""
        contexts = {
            "Python": "Python is widely used in Indian fintech companies like Paytm and Razorpay for backend development and data analytics.",
            "Java": "Java remains the backbone of many Indian enterprises and banking systems, with extensive use in companies like Infosys and TCS.",
            "JavaScript": "JavaScript powers the frontend of major Indian platforms like Flipkart, Myntra, and BigBasket.",
            "React": "React is the preferred choice for Indian startups like Zomato and Swiggy for building responsive user interfaces.",
            "React.js": "React.js is extensively used by Indian e-commerce giants for creating dynamic and interactive user experiences.",
            "Node.js": "Node.js is popular among Indian startups for building scalable backend services, especially in companies like Ola and PhonePe.",
            "DevOps": "Indian IT services companies are rapidly adopting DevOps practices to accelerate delivery for global clients.",
            "Docker": "Docker containerization is becoming standard in Indian cloud-native companies for deployment efficiency."
        }
        return contexts.get(technology, f"{technology} is gaining significant adoption in the Indian tech ecosystem.")
    
    def generate_answer(
        self,
        question: str,
        topic: str,
        difficulty: str = "Medium",
        frequency: str = "Asked Sometimes",
        priority: str = "Medium",
        company_types: Optional[List[str]] = None,
        technology: Optional[str] = None
    ) -> str:
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
            MDX-formatted answer string
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

