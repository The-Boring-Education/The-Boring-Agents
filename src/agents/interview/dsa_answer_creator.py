"""DSA Answer Creator Agent - Specialized agent for Data Structures and Algorithms interview questions."""

from typing import Dict, Any, Optional
from langchain_core.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class DSAAnswerCreator(BaseAgent):
    """Specialized agent for creating world-class DSA interview answers with structured learning approach."""
    
    def __init__(self, **kwargs):
        """Initialize with higher temperature for creativity and better results."""
        super().__init__(temperature=0.8, **kwargs)  # Higher temperature for creativity
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for DSA answer generation."""
        
        dsa_answer_template = PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
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

Create a WORLD-CLASS DSA answer following this EXACT structure. Each section must be present:

## 1. Introduction

**What is this concept?**
- Clear definition in simple terms
- Core idea and fundamental principles
- Why this concept exists in computer science

**Real-world Context (Indian Examples):**
- How Swiggy uses this for delivery route optimization
- How PhonePe implements this for transaction processing
- How Flipkart scales this during Big Billion Days
- How Zomato handles this for restaurant recommendations

## 2. Why We Learn This Topic

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

## 3. Where Do We Use This?

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

## 4. Let's Solve 1 Problem (Step by Step)

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

## 5. Now We Write Code [BRUTEFORCE]

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

## 6. Let's Optimize the Solution

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

## 7. Time & Space Complexity

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

## 8. Were You Able to Understand & Solve?

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
- Write like you're mentoring your younger sibling
- Use conversational Hindi-English (but stay professional)
- Add emojis for better engagement
- Include specific numbers, metrics, examples
- Be confident but humble
- Make them feel "I got this!" after reading

Make this answer so good that students will:
1. Understand the DSA concept deeply
2. Remember it with your analogies
3. Feel confident in interviews
4. Want to practice more problems
5. Think "This ₹49 was totally worth it!"
"""
        )
        
        return {
            "generate_dsa_answer": dsa_answer_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "generate_dsa_answer":
            return self.generate_dsa_answer(
                question=kwargs.get("question"),
                topic=kwargs.get("topic"),
                difficulty=kwargs.get("difficulty", "Medium"),
                frequency=kwargs.get("frequency", "Medium"),
                priority=kwargs.get("priority", "Medium"),
                company_types=kwargs.get("company_types", ["Startup", "MNC"])
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def generate_answer(self, question: str, topic: str, difficulty: str = "Medium",
                       frequency: str = "Asked Sometimes", priority: str = "Medium", 
                       company_types: list = None) -> str:
        """Generate answer - main interface method for compatibility."""
        return self.generate_dsa_answer(question, topic, difficulty, frequency, priority, company_types)
    
    def generate_dsa_answer(self, question: str, topic: str, difficulty: str = "Medium",
                           frequency: str = "Asked Sometimes", priority: str = "Medium", 
                           company_types: list = None) -> str:
        """Generate a world-class DSA answer following the structured format."""
        if company_types is None:
            company_types = ["Startup", "MNC"]
        
        self.logger.info(f"Generating DSA answer for: {question[:50]}...")
        
        # Generate the answer
        prompt = self._format_prompt("generate_dsa_answer",
                                   question=question,
                                   topic=topic,
                                   difficulty=difficulty,
                                   frequency=frequency,
                                   priority=priority,
                                   company_types=", ".join(company_types))
        
        answer = self._generate_with_prompt(prompt)
        
        # Apply DSA-specific quality improvements
        answer = self._apply_dsa_quality_improvements(answer, question, difficulty)
        
        self.logger.info(f"DSA answer generated successfully")
        return answer
    
    def _apply_dsa_quality_improvements(self, answer: str, question: str, difficulty: str) -> str:
        """Apply DSA-specific quality improvements to the answer."""
        
        # Ensure all 8 sections are present
        required_sections = [
            "## 1. Introduction",
            "## 2. Why We Learn This Topic", 
            "## 3. Where Do We Use This?",
            "## 4. Let's Solve 1 Problem",
            "## 5. Now We Write Code [BRUTEFORCE]",
            "## 6. Let's Optimize the Solution",
            "## 7. Time & Space Complexity",
            "## 8. Were You Able to Understand & Solve?"
        ]
        
        # Check if all sections are present
        missing_sections = []
        for section in required_sections:
            if section not in answer:
                missing_sections.append(section)
        
        if missing_sections:
            # Add missing sections
            answer = self._add_missing_sections(answer, missing_sections, question)
        
        # Ensure proper code formatting
        answer = self._ensure_dsa_code_formatting(answer)
        
        # Add complexity analysis if missing
        if "Time Complexity" not in answer or "Space Complexity" not in answer:
            answer = self._add_complexity_analysis(answer, question)
        
        return answer
    
    def _add_missing_sections(self, answer: str, missing_sections: list, question: str) -> str:
        """Add missing sections to the DSA answer."""
        section_templates = {
            "## 1. Introduction": f"""
## 1. Introduction

**What is this concept?**
This is a fundamental DSA concept that helps us solve {question.lower()}. It's essential for understanding how to efficiently process and organize data.

**Real-world Context (Indian Examples):**
- How Swiggy uses this for delivery route optimization
- How PhonePe implements this for transaction processing
- How Flipkart scales this during Big Billion Days
- How Zomato handles this for restaurant recommendations
""",
            "## 2. Why We Learn This Topic": f"""
## 2. Why We Learn This Topic

**Academic Importance:**
This concept is fundamental to computer science and builds the foundation for advanced algorithms. Understanding this helps you think like a computer scientist.

**Industry Relevance:**
Every tech company uses this concept in their systems. It's crucial for building scalable applications and optimizing performance.

**Career Impact:**
Mastering this concept significantly improves your interview performance and opens doors to better opportunities.
""",
            "## 3. Where Do We Use This?": f"""
## 3. Where Do We Use This?

**In Software Development:**
This concept is used extensively in web development, database optimization, and system design.

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
""",
            "## 4. Let's Solve 1 Problem": f"""
## 4. Let's Solve 1 Problem (Step by Step)

**Problem:** Let's solve a related problem to understand this concept better.

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
""",
            "## 5. Now We Write Code [BRUTEFORCE]": f"""
## 5. Now We Write Code [BRUTEFORCE]

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
""",
            "## 6. Let's Optimize the Solution": f"""
## 6. Let's Optimize the Solution

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
""",
            "## 7. Time & Space Complexity": f"""
## 7. Time & Space Complexity

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
""",
            "## 8. Were You Able to Understand & Solve?": f"""
## 8. Were You Able to Understand & Solve?

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
"""
        }
        
        # Add missing sections at the end
        for section in missing_sections:
            if section in section_templates:
                answer += "\n\n" + section_templates[section]
        
        return answer
    
    def _ensure_dsa_code_formatting(self, answer: str) -> str:
        """Ensure proper code formatting for DSA answers."""
        # Fix code blocks
        answer = answer.replace("```python", "```python\n")
        answer = answer.replace("```javascript", "```javascript\n")
        
        # Ensure proper spacing around code blocks
        answer = answer.replace("\n```", "\n\n```")
        answer = answer.replace("```\n", "```\n\n")
        
        return answer
    
    def _add_complexity_analysis(self, answer: str, question: str) -> str:
        """Add complexity analysis if missing."""
        complexity_section = f"""
## 7. Time & Space Complexity

**Brute Force Solution:**
- **Time Complexity:** O(n²) - We need to check all possible combinations
- **Space Complexity:** O(1) - We only use a constant amount of extra space
- **Analysis:** This occurs because we're using nested loops to check all possibilities

**Optimized Solution:**
- **Time Complexity:** O(n) - We can solve this in a single pass
- **Space Complexity:** O(n) - We need to store some information
- **Analysis:** We optimized by using a hash map to store previously seen elements

**Comparison:**
- The optimized solution is significantly faster for large inputs
- We trade some space for better time complexity
- This optimization is crucial for real-world applications
"""
        
        # Insert before section 8 if it exists
        if "## 8. Were You Able to Understand & Solve?" in answer:
            parts = answer.split("## 8. Were You Able to Understand & Solve?")
            return parts[0] + complexity_section + "\n\n## 8. Were You Able to Understand & Solve?" + parts[1]
        else:
            return answer + complexity_section 