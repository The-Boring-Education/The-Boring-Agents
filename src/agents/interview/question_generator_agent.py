"""Question Generator Agent for creating and identifying missing interview questions."""

from typing import Dict, Any, List, Optional
from ...core.base_agent import BaseAgent


class QuestionGeneratorAgent(BaseAgent):
    """Agent for generating new interview questions and identifying gaps."""
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Return empty dict since we'll use direct prompts."""
        return {}
    
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        """Generate question content."""
        return {"generated_content": "Question generated"}
    
    def identify_missing_questions(self, sheet_name: str, existing_questions: List[Dict[str, Any]], 
                                 research_insights: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
        """Identify questions missing from a sheet.
        
        Args:
            sheet_name: Name of the interview sheet
            existing_questions: List of existing questions
            research_insights: Research insights for context
            
        Returns:
            List of missing questions to add
        """
        existing_q_text = [q.get('question', '') for q in existing_questions]
        existing_summary = "\n".join([f"- {q}" for q in existing_q_text[:10]])
        
        gap_analysis_prompt = f"""
        You are a world-class interview expert analyzing gaps in "{sheet_name}" interview sheet.
        
        **Existing Questions (sample):**
        {existing_summary}
        
        **Total Existing Questions:** {len(existing_questions)}
        
        Identify 5-10 MISSING questions that should be added to make this a complete, world-class interview sheet:
        
        **Criteria for Missing Questions:**
        1. **Commonly Asked:** Questions frequently asked by top Indian companies
        2. **Fundamental Gaps:** Basic concepts not covered
        3. **Advanced Concepts:** Higher-level topics missing
        4. **Practical Application:** Real-world scenario questions
        5. **Latest Trends:** Current industry trends not covered
        
        **For each missing question, provide:**
        - **Question:** The actual question text
        - **Reason:** Why this is important to add
        - **Difficulty:** Easy/Medium/Hard
        - **Category:** Type of question (Technical/Conceptual/Practical)
        
        Focus on questions that will genuinely improve the sheet's value for ₹49.
        """
        
        try:
            response = self._generate_with_prompt(gap_analysis_prompt)
            return self._parse_missing_questions(response)
        except Exception as e:
            self.logger.error(f"Error identifying missing questions: {str(e)}")
            return []
    
    def generate_comprehensive_questions(self, sheet_name: str, description: str,
                                       research_insights: Optional[Dict[str, Any]] = None,
                                       target_count: int = 50) -> List[Dict[str, str]]:
        """Generate a comprehensive set of questions for a new sheet.
        
        Args:
            sheet_name: Name of the sheet
            description: Description of what to cover
            research_insights: Research insights
            target_count: Target number of questions
            
        Returns:
            List of generated questions
        """
        question_prompt = f"""
        Create {target_count} world-class interview questions for "{sheet_name}".
        
        **Description:** {description}
        **Target:** Indian tech companies (startups to FAANG)
        
        **Question Distribution:**
        - 30% Easy (Freshers, basic concepts)
        - 50% Medium (Mid-level, implementation)
        - 20% Hard (Senior, system design, optimization)
        
        **Categories to Cover:**
        1. **Fundamentals (20%):** Core concepts and definitions
        2. **Implementation (25%):** How to build/code something
        3. **Problem Solving (20%):** Debugging, optimization
        4. **System Design (15%):** Architecture, scaling
        5. **Practical Scenarios (10%):** Real-world applications
        6. **Best Practices (10%):** Industry standards, patterns
        
        **For each question, provide:**
        - **Question:** Clear, specific question text
        - **Difficulty:** Easy/Medium/Hard
        - **Category:** One of the categories above
        - **Context:** Why this question matters
        
        Make questions that Indian students will find valuable and relevant.
        """
        
        try:
            response = self._generate_with_prompt(question_prompt)
            return self._parse_generated_questions(response, target_count)
        except Exception as e:
            self.logger.error(f"Error generating questions: {str(e)}")
            return self._fallback_questions(sheet_name, target_count)
    
    def generate_trending_questions(self, topic: str, count: int = 10) -> List[Dict[str, str]]:
        """Generate trending questions based on current market trends.
        
        Args:
            topic: Topic to generate questions for
            count: Number of questions to generate
            
        Returns:
            List of trending questions
        """
        trending_prompt = f"""
        Generate {count} trending interview questions for {topic} based on:
        
        **Current Indian Tech Trends:**
        - Remote work challenges
        - Cloud-first architecture
        - AI/ML integration
        - Mobile-first approach
        - Security concerns
        - Performance optimization
        
        **Companies Asking These:**
        - Indian unicorns (Flipkart, Paytm, Ola)
        - FAANG companies
        - Fast-growing startups
        
        Make questions that reflect 2024-2025 industry needs and are actually being asked in interviews.
        """
        
        try:
            response = self._generate_with_prompt(trending_prompt)
            return self._parse_trending_questions_response(response)
        except Exception as e:
            self.logger.error(f"Error generating trending questions: {str(e)}")
            return []
    
    def _parse_missing_questions(self, response: str) -> List[Dict[str, str]]:
        """Parse missing questions from AI response."""
        questions = []
        lines = response.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('**Question:**') or 'Question:' in line:
                if current_question:
                    questions.append(current_question)
                current_question = {'question': line.split(':', 1)[1].strip()}
            elif 'Reason:' in line:
                current_question['reason'] = line.split(':', 1)[1].strip()
            elif 'Difficulty:' in line:
                current_question['difficulty'] = line.split(':', 1)[1].strip()
            elif 'Category:' in line:
                current_question['category'] = line.split(':', 1)[1].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions[:10]  # Limit to 10 questions
    
    def _parse_generated_questions(self, response: str, target_count: int) -> List[Dict[str, str]]:
        """Parse generated questions from AI response."""
        questions = []
        lines = response.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if ('Question:' in line or line.startswith(('1.', '2.', '3.', '4.', '5.'))):
                if current_question:
                    questions.append(current_question)
                    
                # Extract question text
                if ':' in line:
                    q_text = line.split(':', 1)[1].strip()
                else:
                    q_text = line
                current_question = {'question': q_text, 'difficulty': 'Medium', 'category': 'Technical'}
                
            elif 'Difficulty:' in line:
                difficulty = line.split(':', 1)[1].strip()
                if difficulty in ['Easy', 'Medium', 'Hard']:
                    current_question['difficulty'] = difficulty
            elif 'Category:' in line:
                current_question['category'] = line.split(':', 1)[1].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions[:target_count]
    
    def _parse_trending_questions_response(self, response: str) -> List[Dict[str, str]]:
        """Parse trending questions response."""
        questions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                questions.append({
                    'question': line,
                    'difficulty': 'Medium',
                    'category': 'Trending',
                    'trend_score': 9
                })
        
        return questions
    
    def _fallback_questions(self, sheet_name: str, count: int) -> List[Dict[str, str]]:
        """Generate fallback questions if AI generation fails."""
        topic_lower = sheet_name.lower()
        
        fallback_questions = [
            f"What is {sheet_name} and why is it important?",
            f"Explain the key concepts of {sheet_name}",
            f"How would you implement {sheet_name} in a real project?",
            f"What are the best practices for {sheet_name}?",
            f"How does {sheet_name} compare to alternatives?",
            f"What are common challenges with {sheet_name}?",
            f"How would you optimize {sheet_name} for performance?",
            f"Explain {sheet_name} with a real-world example",
            f"What are the latest trends in {sheet_name}?",
            f"How would you debug issues with {sheet_name}?"
        ]
        
        questions = []
        for i, q in enumerate(fallback_questions[:count]):
            questions.append({
                'question': q,
                'difficulty': 'Medium' if i % 3 != 0 else 'Easy',
                'category': 'General'
            })
        
        return questions