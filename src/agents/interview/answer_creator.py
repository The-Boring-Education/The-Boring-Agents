"""Answer Creator Agent - Generates world-class interview answers with Indian context and humor."""

from typing import Dict, Any, Optional
from langchain.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class AnswerCreator(BaseAgent):
    """Agent for creating world-class interview answers with Indian context, humor, and expert insights."""
    
    def __init__(self, **kwargs):
        """Initialize with higher temperature for creativity and better results."""
        super().__init__(temperature=0.8, **kwargs)  # Higher temperature for creativity
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for answer generation."""
        
        world_class_answer_template = PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
            template="""
You are India's TOP tech instructor and interviewer with 500+ interviews at companies like:
- FAANG (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**Interview Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

Create a WORLD-CLASS answer that will help Indian students ACE their interviews and justify the ₹49 they're paying.

##### 🎯 Quick Answer

Give a concise, confident answer they can say in the first 30 seconds.

##### 📚 Introduction

**What is it?**
- Clear definition in simple terms
- Why it exists and what problem it solves

**Real-world Context (Indian Examples):**
- How Swiggy uses this for delivery tracking
- How PhonePe implements this for payments
- How Flipkart scales this during Big Billion Days
- How Zomato handles this for restaurant listings

**Technical Deep Dive:**
- Implementation details with code examples
- Best practices and common patterns
- Performance considerations

##### 💻 Code Example

Provide a clear, working code example with comments explaining each part.

##### ❌ Bad Code Example

Show a common mistake or anti-pattern and explain what NOT to do.

##### ✅ Good Code Example

Show the best practice and proper implementation.

##### 🤔 Why This Concept Matters

Real-world importance, industry relevance, and why it matters for your career.

##### 🎭 Different Ways Interviewers Ask This

1. [First variation of how this question might be framed]
2. [Second variation of how this question might be framed]
3. [Third variation of how this question might be framed]

##### 😄 How will you remember it?

Create a funny, memorable analogy using Indian context (e.g., Mumbai local trains, masala dabba, street food stall).

##### 💡 Tip

Share one practical, actionable tip that will make a real difference for this concept.

##### 💼 Interview Pro Tips

**What interviewers want to hear:**

1. Key buzzwords and concepts
2. Trade-offs and considerations  
3. When to use vs. when not to use

**Red flags to avoid:**

1. Common misconceptions
2. Things you shouldn't say in interviews
3. Mistakes freshers typically make

##### 🧠 Practice Problems

1. [First problem to solve for practice with brief description]
2. [Second problem to solve for practice with brief description]

##### 🤖 Ask AI these questions

1. [First deeper or related problem the student can ask an AI]
2. [Second deeper or related problem the student can ask an AI]

##### 🏢 Companies That Ask This

**Definitely:** [List 3-4 companies that definitely ask this]

**Sometimes:** [List 3-4 companies that sometimes ask this]

**Rarely:** [List 2-3 companies that rarely ask this]

## Writing Style:
- Write like you're mentoring your younger sibling
- Use conversational Hindi-English (but stay professional)
- Add emojis for better engagement
- Include specific numbers, metrics, examples
- Be confident but humble
- Make them feel "I got this!" after reading

Make this answer so good that students will:
1. Understand the concept deeply
2. Remember it with your analogies
3. Feel confident in interviews
4. Want to share it with friends
5. Think "This ₹49 was totally worth it!"
"""
        )
        
        return {
            "generate_answer": world_class_answer_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "generate_answer":
            return self.generate_answer(
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
                       frequency: str = "Medium", priority: str = "Medium", 
                       company_types: list = None) -> str:
        """Generate a world-class answer for an interview question."""
        if company_types is None:
            company_types = ["Startup", "MNC"]
        
        self.logger.info(f"Generating answer for: {question[:50]}...")
        
        # Generate the answer
        prompt = self._format_prompt("generate_answer",
                                   question=question,
                                   topic=topic,
                                   difficulty=difficulty,
                                   frequency=frequency,
                                   priority=priority,
                                   company_types=", ".join(company_types))
        
        answer = self._generate_with_prompt(prompt)
        
        # Apply quality improvements
        answer = self._apply_quality_improvements(answer, question, difficulty)
        
        self.logger.info(f"Answer generated successfully")
        return answer
    
    def _apply_quality_improvements(self, answer: str, question: str, difficulty: str) -> str:
        """Apply quality improvements to the answer."""
        # Add humor and context if missing
        if "😄" not in answer and "How will you remember it?" not in answer:
            answer = self._add_humor_and_context(answer, question)
        
        # Ensure proper formatting
        answer = self._ensure_proper_formatting(answer)
        
        # Add performance considerations for advanced questions
        if difficulty in ["Hard", "Advanced"]:
            answer = self._add_performance_considerations(answer)
        
        return answer
    
    def _add_humor_and_context(self, answer: str, question: str) -> str:
        """Add humor and Indian context to the answer."""
        humor_prompt = f"""
Add a funny, memorable analogy using Indian context to this answer:

Question: {question}
Answer: {answer}

Add a section like this:
##### 😄 How will you remember it?

[Create a funny analogy using Indian context like Mumbai local trains, masala dabba, street food stall, etc.]

Make it memorable and relatable to Indian students.
"""
        
        humor_section = self._generate_with_prompt(humor_prompt)
        
        # Insert humor section before the Interview Pro Tips section
        if "##### 💼 Interview Pro Tips" in answer:
            parts = answer.split("##### 💼 Interview Pro Tips")
            return parts[0] + humor_section + "\n\n##### 💼 Interview Pro Tips" + parts[1]
        else:
            return answer + "\n\n" + humor_section
    
    def _ensure_proper_formatting(self, answer: str) -> str:
        """Ensure proper markdown formatting."""
        # Fix headers
        answer = answer.replace("###", "#####")
        
        # Ensure proper spacing
        answer = answer.replace("\n\n\n", "\n\n")
        
        # Fix code blocks
        if "```" not in answer and "Code Example" in answer:
            # Add code block formatting
            lines = answer.split('\n')
            formatted_lines = []
            in_code_section = False
            
            for line in lines:
                if "Code Example" in line:
                    in_code_section = True
                    formatted_lines.append(line)
                    formatted_lines.append("```python")
                elif in_code_section and line.strip() and not line.startswith('#####'):
                    if "```" not in line:
                        formatted_lines.append(line)
                    else:
                        in_code_section = False
                        formatted_lines.append(line)
                else:
                    if in_code_section:
                        formatted_lines.append("```")
                        in_code_section = False
                    formatted_lines.append(line)
            
            answer = '\n'.join(formatted_lines)
        
        return answer
    
    def _add_performance_considerations(self, answer: str) -> str:
        """Add performance considerations for advanced questions."""
        if "Performance" not in answer and "Complexity" not in answer:
            performance_section = """
##### ⚡ Performance Considerations

- **Time Complexity:** [Analyze the time complexity]
- **Space Complexity:** [Analyze the space complexity]
- **Optimization Opportunities:** [Discuss potential optimizations]
- **Trade-offs:** [Discuss trade-offs between different approaches]

"""
            
            # Insert before Interview Pro Tips
            if "##### 💼 Interview Pro Tips" in answer:
                parts = answer.split("##### 💼 Interview Pro Tips")
                return parts[0] + performance_section + "##### 💼 Interview Pro Tips" + parts[1]
            else:
                return answer + performance_section
        
        return answer 