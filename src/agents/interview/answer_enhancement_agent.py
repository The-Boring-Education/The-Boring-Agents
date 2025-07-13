"""Answer Enhancement Agent for creating world-class interview answers with Indian context and humor."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class AnswerEnhancementAgent(BaseAgent):
    """Agent for creating world-class interview answers with Indian context, humor, and expert insights."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for answer enhancement."""
        
        world_class_answer_template = PromptTemplate(
            input_variables=["question", "existing_answer", "sheet_name", "research_insights"],
            template="""
            You are India's TOP tech instructor and interviewer with 500+ interviews at companies like:
            - FAANG (Google, Meta, Amazon, Apple, Netflix)
            - Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
            - Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
            - MNCs (Microsoft, Oracle, SAP, IBM)
            
            **Interview Question:** {question}
            **Sheet Topic:** {sheet_name}
            **Existing Answer (if any):** {existing_answer}
            **Research Context:** {research_insights}
            
            Create a WORLD-CLASS answer that will help Indian students ACE their interviews and justify the ₹49 they're paying.
            
            #### 🎯 Quick Answer
            
            
            Give a concise, confident answer they can say in the first 30 seconds.
            
            
            #### 📚 Introduction
            
            
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
            
            
            #### 💻 Code Example
            
            
            Provide a clear, working code example with comments explaining each part.
            
            
            #### ❌ Bad Code Example
            
            
            Show a common mistake or anti-pattern and explain what NOT to do.
            
            
            #### ✅ Good Code Example
            
            
            Show the best practice and proper implementation.
            
            
            #### 🤔 Why This Concept Matters
            
            
            Real-world importance, industry relevance, and why it matters for your career.
            
            
            #### 🎭 Different Ways Interviewers Ask This
            
            
            1. [First variation of how this question might be framed]
            2. [Second variation of how this question might be framed]
            3. [Third variation of how this question might be framed]
            
            
            #### 😄 How will you remember it?
            
            
            Create a funny, memorable analogy using Indian context (e.g., Mumbai local trains, masala dabba, street food stall).
            
            
            #### 💡 Tip
            
            
            Share one practical, actionable tip that will make a real difference for this concept.
            
            
            #### 💼 Interview Pro Tips
            
            
            **What interviewers want to hear:**
            
            1. Key buzzwords and concepts
            2. Trade-offs and considerations  
            3. When to use vs. when not to use
            
            **Red flags to avoid:**
            
            1. Common misconceptions
            2. Things you shouldn't say in interviews
            3. Mistakes freshers typically make
            
            
            #### 🧠 Practice Problems
            
            
            1. [First problem to solve for practice with brief description]
            2. [Second problem to solve for practice with brief description]
            
            
            #### 🤖 Ask AI these questions
            
            
            1. [First deeper or related problem the student can ask an AI]
            2. [Second deeper or related problem the student can ask an AI]
            
            
            #### 🏢 Companies That Ask This
            
            
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
        
        enhanced_answer_template = PromptTemplate(
            input_variables=["question", "existing_answer", "sheet_name", "research_insights"],
            template="""
            You are India's TOP tech instructor and interviewer with 500+ interviews at companies like:
            - FAANG (Google, Meta, Amazon, Apple, Netflix)
            - Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
            - Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
            - MNCs (Microsoft, Oracle, SAP, IBM)
            
            **Interview Question:** {question}
            **Sheet Topic:** {sheet_name}
            **Existing Answer (if any):** {existing_answer}
            **Research Context:** {research_insights}
            
            Create a WORLD-CLASS answer with this EXACT structure and formatting:
            
            #### 🎯 Quick Answer
            
            [Concise, confident answer they can say immediately]
            
            
            #### 📖 Introduction
            
            [What this concept is, why it matters, and the problem it solves]
            
            
            #### 💻 Code Example
            
            ```javascript
            // Clear, working code example
            // With comments explaining each part
            ```
            
            
            #### ❌ Bad Code Example
            
            ```javascript
            // Common mistakes and anti-patterns
            // What NOT to do
            ```
            
            
            #### ✅ Good Code Example
            
            ```javascript
            // Best practices and proper implementation
            // What TO do
            ```
            
            
            #### 🤔 Why This Concept Matters
            
            [Real-world importance, industry relevance, and why it matters for your career]
            
            
            #### 🎭 Different Ways Interviewers Ask This
            
            1. [First variation of how this question might be framed]
            2. [Second variation of how this question might be framed]
            3. [Third variation of how this question might be framed]
            
            
            #### 😄 How will you remember it?
            
            [Funny Indian analogy to remember this concept - make it memorable and relatable]
            
            
            #### 💡 Tip
            
            [Share ONE specific, actionable tip that will make a real difference - be very practical and specific]
            
            
            #### 💼 Interview Pro Tips
            
            **What interviewers want to hear:**
            1. [First key point they want to hear]
            2. [Second key point they want to hear]
            3. [Third key point they want to hear]
            
            **Red flags to avoid:**
            1. [First thing to avoid saying]
            2. [Second thing to avoid saying]
            3. [Third thing to avoid saying]
            
            
            #### 🧠 Practice Problems
            
            1. [First problem description - be specific and actionable]
            2. [Second problem description - be specific and actionable]
            3. [Third problem description - be specific and actionable]
            
            
            #### 🤖 Ask AI these questions
            
            1. [First deeper or related problem]
            2. [Second deeper or related problem]
            
            
            #### 🏢 Companies That Ask This
            
            **Definitely:** [List 3-4 companies that definitely ask this]
            
            **Sometimes:** [List 3-4 companies that sometimes ask this]
            
            **Rarely:** [List 2-3 companies that rarely ask this]
            
            
            ## CRITICAL FORMATTING REQUIREMENTS:
            
            1. **Spacing**: Always add TWO blank lines after each section heading and before the next section
            2. **Headings**: Use EXACTLY four hashtags (####) for all section headings
            3. **Lists**: For numbered lists, use "1.", "2.", "3." format with proper numbering
            4. **Consistency**: Every section should follow the exact spacing pattern shown above
            5. **Code Blocks**: Always include proper code examples with explanatory comments
            6. **Structure**: Follow the exact order and naming of sections as specified
            
            Make this answer so engaging that students:
            1. Actually enjoy reading it
            2. Remember concepts through humor and analogies
            3. Feel confident and prepared for interviews
            4. Want to share with friends
            5. Think "This ₹49 was totally worth it!"
            
            Remember: Quality over quantity. Each section should be substantial and valuable.
            """
        )
        
        quality_improvement_template = PromptTemplate(
            input_variables=["answer", "suggestions", "question", "difficulty"],
            template="""
            You're reviewing an interview answer that needs improvement based on feedback.
            
            **Original Answer:** {answer}
            **Question:** {question}
            **Improvement Suggestions:** {suggestions}
            **Difficulty Level:** {difficulty}
            
            Apply the feedback to make this answer even better:
            
            1. **Address each suggestion specifically**
            2. **Maintain the engaging, Indian context style**
            3. **Keep all the humor and analogies**
            4. **Ensure technical accuracy**
            5. **Make it more comprehensive if needed**
            
            Return the improved answer that addresses all the feedback while maintaining the world-class quality.
            """
        )
        
        humor_injection_template = PromptTemplate(
            input_variables=["technical_content", "indian_context"],
            template="""
            Take this technical content and add appropriate humor and Indian context analogies.
            
            **Technical Content:** {technical_content}
            **Indian Context:** {indian_context}
            
            Add humor through:
            1. **Relatable analogies** (traffic, food, family, festivals)
            2. **Situational comedy** (office scenarios, college memories)
            3. **Cultural references** (Bollywood, cricket, regional quirks)
            4. **Self-deprecating tech humor** (debugging at 3 AM, production issues)
            
            Keep it:
            - Professional but fun
            - Inclusive and respectful
            - Actually helpful for memory
            - Appropriate for interview context
            
            Return the content with humor naturally woven in.
            """
        )
        
        return {
            "world_class_answer": world_class_answer_template,
            "enhanced_answer": enhanced_answer_template,
            "quality_improvement": quality_improvement_template,
            "humor_injection": humor_injection_template
        }
    
    def create_world_class_answer(self, question: str, existing_answer: str = "",
                                sheet_name: str = "", research_insights: Optional[Dict[str, Any]] = None) -> str:
        """Create a world-class interview answer with Indian context and humor.
        
        Args:
            question: The interview question
            existing_answer: Existing answer to improve upon
            sheet_name: Name of the interview sheet/topic
            research_insights: Research insights for context
            
        Returns:
            World-class interview answer
        """
        insights_dict = research_insights if research_insights is not None else {}
        insights_text = self._format_research_insights(insights_dict)
        
        result = self.generate_content(
            "enhanced_answer",
            question=question,
            existing_answer=existing_answer or "No existing answer provided.",
            sheet_name=sheet_name,
            research_insights=insights_text
        )
        
        return result["generated_content"]
    
    def apply_quality_improvements(self, answer: str, suggestions: List[str],
                                 question: str = "", difficulty: str = "Medium") -> str:
        """Apply quality improvements to an existing answer.
        
        Args:
            answer: Original answer
            suggestions: List of improvement suggestions
            question: The original question
            difficulty: Difficulty level
            
        Returns:
            Improved answer
        """
        suggestions_text = "\n".join([f"- {suggestion}" for suggestion in suggestions])
        
        result = self.generate_content(
            "quality_improvement",
            answer=answer,
            suggestions=suggestions_text,
            question=question,
            difficulty=difficulty
        )
        
        return result["generated_content"]
    
    def add_humor_and_context(self, technical_content: str, 
                            indian_context: str = "General Indian tech industry") -> str:
        """Add humor and Indian context to technical content.
        
        Args:
            technical_content: Technical content to enhance
            indian_context: Specific Indian context to use
            
        Returns:
            Enhanced content with humor and context
        """
        result = self.generate_content(
            "humor_injection",
            technical_content=technical_content,
            indian_context=indian_context
        )
        
        return result["generated_content"]
    
    def create_comprehensive_answer_suite(self, question: str, topic: str) -> Dict[str, str]:
        """Create a comprehensive suite of answer components.
        
        Args:
            question: Interview question
            topic: Topic/subject area
            
        Returns:
            Dictionary with different answer components
        """
        # Create the main world-class answer
        main_answer = self.create_world_class_answer(question, "", topic)
        
        # Extract technical parts for additional processing
        technical_parts = self._extract_technical_content(main_answer)
        
        # Create additional components
        components = {
            "main_answer": main_answer,
            "quick_summary": self._create_quick_summary(main_answer),
            "memory_tricks": self._extract_memory_tricks(main_answer),
            "interview_tips": self._extract_interview_tips(main_answer),
            "practice_scenarios": self._extract_practice_scenarios(main_answer)
        }
        
        return components
    
    def _format_research_insights(self, insights: Dict[str, Any]) -> str:
        """Format research insights for use in prompts."""
        if not insights:
            return "General tech industry insights for Indian market"
        
        formatted = []
        
        if "market_trends" in insights:
            trends = insights["market_trends"]
            if isinstance(trends, dict) and "key_insights" in trends:
                formatted.append("Market Trends:")
                for insight in trends["key_insights"][:3]:
                    formatted.append(f"- {insight}")
        
        if "key_recommendations" in insights:
            formatted.append("Key Recommendations:")
            for rec in insights["key_recommendations"][:3]:
                formatted.append(f"- {rec}")
        
        if "company_focus" in insights:
            formatted.append(f"Company Focus: {insights['company_focus']}")
        
        return "\n".join(formatted) if formatted else "Indian tech industry context"
    
    def _extract_technical_content(self, answer: str) -> str:
        """Extract technical content from an answer."""
        # Simple extraction - look for technical sections
        lines = answer.split('\n')
        technical_lines = []
        
        in_technical_section = False
        for line in lines:
            if "Technical Deep Dive" in line or "Implementation" in line:
                in_technical_section = True
            elif line.startswith("### ") and in_technical_section:
                in_technical_section = False
            
            if in_technical_section:
                technical_lines.append(line)
        
        return "\n".join(technical_lines)
    
    def _create_quick_summary(self, answer: str) -> str:
        """Create a quick summary from the main answer."""
        lines = answer.split('\n')
        summary_lines = []
        
        in_quick_section = False
        for line in lines:
            if "Quick Answer" in line:
                in_quick_section = True
            elif line.startswith("### ") and in_quick_section:
                in_quick_section = False
            
            if in_quick_section and line.strip() and not line.startswith("###"):
                summary_lines.append(line.strip())
        
        return "\n".join(summary_lines[:3])  # First 3 lines of quick answer
    
    def _extract_memory_tricks(self, answer: str) -> str:
        """Extract memory tricks from the answer."""
        lines = answer.split('\n')
        trick_lines = []
        
        in_memory_section = False
        for line in lines:
            if "Memory Trick" in line:
                in_memory_section = True
            elif line.startswith("### ") and in_memory_section:
                in_memory_section = False
            
            if in_memory_section and line.strip() and not line.startswith("###"):
                trick_lines.append(line.strip())
        
        return "\n".join(trick_lines)
    
    def _extract_interview_tips(self, answer: str) -> str:
        """Extract interview tips from the answer."""
        lines = answer.split('\n')
        tip_lines = []
        
        in_tips_section = False
        for line in lines:
            if "Interview Pro Tips" in line:
                in_tips_section = True
            elif line.startswith("### ") and in_tips_section:
                in_tips_section = False
            
            if in_tips_section and line.strip() and not line.startswith("###"):
                tip_lines.append(line.strip())
        
        return "\n".join(tip_lines)
    
    def _extract_practice_scenarios(self, answer: str) -> str:
        """Extract practice scenarios from the answer."""
        lines = answer.split('\n')
        scenario_lines = []
        
        in_practice_section = False
        for line in lines:
            if "Practice Scenarios" in line:
                in_practice_section = True
            elif line.startswith("### ") and in_practice_section:
                in_practice_section = False
            
            if in_practice_section and line.strip() and not line.startswith("###"):
                scenario_lines.append(line.strip())
        
        return "\n".join(scenario_lines)
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate enhanced answer content based on the content type."""
        if content_type not in self.prompt_templates:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Format the prompt
        prompt = self._format_prompt(content_type, **kwargs)
        
        # Generate content
        generated_content = self._generate_with_prompt(prompt)
        
        return {
            "generated_content": generated_content,
            "content_type": content_type,
            "parameters": kwargs
        }