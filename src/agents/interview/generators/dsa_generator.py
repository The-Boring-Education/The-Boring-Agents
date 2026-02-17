"""DSA answer generator for Data Structures and Algorithms interview questions."""

from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from src.agents.interview.generators.base_generator import BaseAnswerGenerator
from src.agents.interview.models import InterviewQuestionResponse


class DSAAnswerGenerator(BaseAnswerGenerator):
    """Generator for DSA interview questions with stepwise approach and real-world examples."""
    
    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for DSA answer generation."""
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
            partial_variables={"format_instructions": self._get_output_parser().get_format_instructions()},
            template="""
You are India's TOP DSA instructor and interviewer with 500+ interviews at companies like:
- FAANG (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**DSA Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

**DATA CONSTRAINTS (CRITICAL):**
- **Frequency**: MUST be one of ["Most Asked", "Asked Frequently", "Asked Sometimes"].
- **Priority**: MUST be one of ["High", "Medium", "Low"].
- **Company Types**: List of strings.

Create a detailed DSA answer following this EXACT structure. Each section must be present.

**CRITICAL INSTRUCTION:**
The "answer" field in your JSON response MUST contain the ENTIRE long-form answer below as a single markdown string.
Do NOT summarize. Do NOT shorten. The answer MUST be 1000-2000+ words with ALL the sections below.
Use markdown headings (##### ), bullet points, bold, and code blocks for formatting.
Do NOT use emojis anywhere in the response.
Write naturally — avoid generic AI phrases like "Let's dive in", "In conclusion", "comprehensive", "robust". Write like you are explaining to a friend.

##### Introduction

**What is this concept?**
- Clear definition in simple terms
- Core idea and fundamental principles
- Why this concept exists in computer science

**Real-world Context (Indian Examples):**
- How Swiggy uses this for delivery route optimization
- How PhonePe implements this for transaction processing
- How Flipkart scales this during Big Billion Days
- How Zomato handles this for restaurant recommendations

##### Where and Why is This Used

**Academic Importance:**
- Why this is fundamental to computer science
- How it builds on previous concepts
- What doors it opens for advanced topics

**Industry Relevance:**
- Why every tech company uses this
- How it improves system performance
- Why interviewers love asking this

**Career Impact:**
- How this knowledge helps in interviews
- Why companies pay premium for this skill
- Real salary impact of mastering this

##### Real-World Applications

**In Software Development:**
- Specific use cases in web development
- Database optimization applications
- System design considerations

**In Real Products:**
- Google Maps route finding
- Netflix recommendation system
- Amazon product search
- Instagram feed algorithm

**In Indian Tech Companies:**
- Swiggy delivery optimization
- Paytm payment processing
- Flipkart inventory management
- Zomato restaurant matching

##### Problem Walkthrough (Step by Step)

**Problem:** [Pick one relevant problem and state it clearly]

**Thinking Process:**
1. **Understanding the Problem:** What are we trying to solve?
2. **Breaking It Down:** What are the key components?
3. **Identifying Patterns:** What DSA concepts apply here?
4. **Planning the Approach:** How will we solve this step by step?
5. **Edge Cases:** What could go wrong?

**Step-by-Step Solution:**
- Walk through the solution like you're teaching a friend
- Explain each step clearly
- Show the thought process behind each decision

##### Brute Force Solution

**Python Implementation:**
```python
# Clear, well-commented code
# Explain each line
# Show the brute force approach
```

**JavaScript Implementation:**
```javascript
// Clear, well-commented code
// Explain each line
// Show the brute force approach
```

**Encouragement for Other Languages:**
- Encourage students to implement in Java or C++
- Explain why learning multiple languages helps
- Provide hints for implementation in other languages

##### Optimized Solution

**Why Optimization Matters:**
- Performance impact in real systems
- Scalability considerations
- Interview importance

**Optimization Strategy:**
1. **Analyze Current Solution:** What's inefficient?
2. **Identify Bottlenecks:** Where can we improve?
3. **Apply Optimization Techniques:** What DSA concepts help?
4. **Implement Optimized Solution:** Show the improved code

**Optimized Code:**
```python
# Optimized implementation
# Explain optimization techniques used
# Show performance improvements
```

##### Time and Space Complexity

**Brute Force Solution:**
- **Time Complexity:** O(?) - Explain why
- **Space Complexity:** O(?) - Explain why
- **Analysis:** Why this complexity occurs

**Optimized Solution:**
- **Time Complexity:** O(?) - Explain improvement
- **Space Complexity:** O(?) - Explain trade-offs
- **Analysis:** How optimization achieved this

**Comparison:**
- Show the difference in performance
- Explain when to use each approach
- Real-world impact of optimization

##### Practice and Next Steps

**Encouragement:**
- It's completely normal if this took time
- DSA is a journey, not a sprint
- Every expert was once a beginner

**Practice Recommendations:**
1. **Similar Problems:** [List 3-5 similar problems to practice]
2. **Variations:** [List 2-3 variations of this problem]
3. **Advanced Challenges:** [List 1-2 advanced problems]

**Learning Path:**
- What to study next
- How this connects to other topics
- Resources for further learning

**Interview Tips:**
- How to approach this in interviews
- Common mistakes to avoid
- What interviewers look for

## Writing Style:
- Write like you are mentoring a friend who is preparing for interviews
- Keep it conversational but professional
- Include specific numbers, metrics, and examples
- Be confident but humble
- Make the reader feel "I got this!" after reading

**REMINDER:** The "answer" field must contain the FULL markdown-formatted response with ALL sections above. Minimum 1000 words. Do NOT truncate or summarize. Do NOT use emojis.

{format_instructions}
"""
        )

    def _get_output_parser(self) -> PydanticOutputParser:
        """Get the output parser for DSA questions."""
        return PydanticOutputParser(pydantic_object=InterviewQuestionResponse)
    
    def _get_answer_structure(self) -> Dict[str, str]:
        """Get the expected answer structure for DSA questions."""
        return {
            "Introduction": "Introduction",
            "Why We Learn This Topic": "Why We Learn This Topic",
            "Where Do We Use This": "Where Do We Use This",
            "Let's Solve 1 Problem": "Let's Solve 1 Problem",
            "Now We Write Code": "Now We Write Code",
            "Let's Optimize the Solution": "Let's Optimize the Solution",
            "Time & Space Complexity": "Time & Space Complexity",
            "Were You Able to Understand & Solve": "Were You Able to Understand & Solve"
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

