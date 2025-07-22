"""Interview preparation agent for generating question sheets."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import random

from ...core.base_agent import BaseAgent
from ...utils.validation import InterviewQuestionValidator


class InterviewAgent(BaseAgent):
    """Agent for generating interview preparation content in sheet format."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for interview content generation."""
        
        question_sheet_template = PromptTemplate(
            input_variables=["topic"],
            template="""
            You are a senior tech interviewer with 20+ years of experience who has conducted 300+ interviews. 
            You have deep knowledge of the Indian tech industry and understand what companies actually ask in interviews.
            
            Create a comprehensive interview question sheet for {topic}. Generate 30-50 high-quality questions that cover:
            
            1. **Core Fundamentals** - Basic concepts, syntax, and principles
            2. **Practical Implementation** - Real-world scenarios and problem-solving
            3. **Advanced Concepts** - Complex topics and edge cases
            4. **Best Practices** - Industry standards and optimization
            5. **System Design** - Architecture and scalability considerations
            
            For each question, provide:
            - A clear, concise question title
            - The actual question text
            - A comprehensive answer with:
              * Quick answer summary
              * Detailed explanation with code examples
              * Good vs bad code examples
              * Why this concept matters
              * Different ways interviewers ask this
              * Related concepts to revise
              * Memory tricks and tips
              * Interview pro tips
              * Practice problems
              * Companies that ask this
            
            Format each answer in markdown with proper sections and emojis for readability.
            
            Think like an experienced interviewer who knows exactly what companies ask and how to evaluate candidates effectively.
            Focus on questions that actually come up in Indian tech interviews, not just theoretical concepts.
            """
        )
        
        return {
            "question_sheet": question_sheet_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate interview content based on the specified type.
        
        Args:
            content_type: Type of content to generate
            **kwargs: Parameters specific to the content type
            
        Returns:
            Generated interview content with metadata
        """
        if content_type not in self.prompt_templates:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Generate the prompt
        prompt = self._format_prompt(content_type, **kwargs)
        
        # Generate content
        generated_text = self._generate_with_prompt(prompt)
        
        # Structure the response
        result = {
            "content_type": content_type,
            "parameters": kwargs,
            "generated_content": generated_text,
            "metadata": {
                "model": self.model_name,
                "timestamp": self._get_timestamp(),
                "question_count": self._estimate_question_count(generated_text),
                "estimated_prep_time": self._estimate_prep_time(generated_text)
            }
        }
        
        return result
    
    def create_question_sheet(self, topic: str) -> Dict[str, Any]:
        """Create a comprehensive question sheet for a technology topic.
        
        Args:
            topic: The technology/topic to focus on (e.g., "JavaScript", "React", "Python")
            
        Returns:
            Complete question sheet with structured questions and answers
        """
        result = self.generate_content("question_sheet", topic=topic)
        
        # Parse the generated content into structured format
        structured_questions = self._parse_questions_from_content(result['generated_content'])
        
        # Determine roadmap based on topic
        roadmap = self._determine_roadmap(topic)
        
        # Create sheet data
        sheet_data = {
            "name": f"{topic} Interview Questions",
            "description": f"Comprehensive interview preparation for {topic} with expert-curated questions",
            "roadmap": roadmap,
            "questions": structured_questions
        }
        
        # Validate the sheet data
        validation_result = InterviewQuestionValidator.validate_sheet_data(sheet_data)
        
        if not validation_result["is_valid"]:
            self.logger.error(f"Validation failed: {validation_result['errors']}")
            raise ValueError(f"Sheet validation failed: {validation_result['errors']}")
        
        if validation_result["warnings"]:
            self.logger.warning(f"Validation warnings: {validation_result['warnings']}")
        
        return {
            "topic": topic,
            "roadmap": roadmap,
            "questions": validation_result["data"]["questions"],
            "metadata": {
                "total_questions": len(validation_result["data"]["questions"]),
                "created_at": self._get_timestamp(),
                "roadmap": roadmap,
                "validation_warnings": validation_result["warnings"]
            }
        }
    
    def _parse_questions_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse the generated content into structured question format."""
        questions = []
        
        # Try multiple parsing strategies
        questions = self._parse_questions_strategy_1(content)
        
        if not questions:
            questions = self._parse_questions_strategy_2(content)
        
        if not questions:
            questions = self._parse_questions_strategy_3(content)
        
        # If still no questions, create intelligent fallback
        if not questions:
            questions = self._create_intelligent_fallback(content)
        
        return questions
    
    def _parse_questions_strategy_1(self, content: str) -> List[Dict[str, Any]]:
        """Parse questions using ## headers strategy."""
        questions = []
        
        # Split content by question markers (## headers)
        sections = content.split('##')
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            if len(lines) < 2:
                continue
            
            # Extract title (first line after ##)
            title_line = lines[0].strip()
            if not title_line or title_line.startswith('#'):
                continue
            
            # Find the question text and answer
            question_text = ""
            answer_text = ""
            in_answer = False
            
            for line in lines[1:]:
                line = line.strip()
                
                # Check for answer section markers
                if any(marker in line for marker in ['🎯', '📖', '💻', '❌', '✅', '🤔', '🎭', '🔗', '😄', '💡', '💼', '🧠', '🏢']):
                    in_answer = True
                    answer_text += line + '\n'
                    continue
                
                if in_answer:
                    answer_text += line + '\n'
                else:
                    # If we haven't found answer markers yet, this is question text
                    if line and not line.startswith('---'):
                        question_text += line + '\n'
            
            # If we have both question and answer, create the question
            if question_text.strip() and answer_text.strip():
                # Use AI to intelligently determine frequency, company types, and priority
                frequency = self._ai_determine_frequency(title_line, question_text, answer_text)
                company_types = self._ai_determine_company_types(title_line, question_text, answer_text)
                priority = self._ai_determine_priority(title_line, question_text, answer_text)
                
                questions.append({
                    "title": title_line,
                    "question": question_text.strip(),
                    "answer": answer_text.strip(),
                    "frequency": frequency,
                    "companyTypes": company_types,
                    "priority": priority
                })
        
        return questions
    
    def _parse_questions_strategy_2(self, content: str) -> List[Dict[str, Any]]:
        """Parse questions using **Question:** markers strategy."""
        questions = []
        
        # Look for "**Question:**" patterns
        question_blocks = content.split('**Question:**')
        
        for i, block in enumerate(question_blocks[1:], 1):  # Skip first empty block
            lines = block.split('\n')
            
            # Extract question text (everything until **Answer:** or next section)
            question_text = ""
            answer_text = ""
            in_answer = False
            
            for line in lines:
                line = line.strip()
                
                if '**Answer:**' in line:
                    in_answer = True
                    answer_text += line + '\n'
                    continue
                
                if in_answer:
                    answer_text += line + '\n'
                else:
                    if line and not line.startswith('**'):
                        question_text += line + '\n'
            
            if question_text.strip() and answer_text.strip():
                # Generate a title from the question
                title = f"Question {i}: {question_text[:50].strip()}..."
                
                # Use AI to intelligently determine frequency, company types, and priority
                frequency = self._ai_determine_frequency(title, question_text, answer_text)
                company_types = self._ai_determine_company_types(title, question_text, answer_text)
                priority = self._ai_determine_priority(title, question_text, answer_text)
                
                questions.append({
                    "title": title,
                    "question": question_text.strip(),
                    "answer": answer_text.strip(),
                    "frequency": frequency,
                    "companyTypes": company_types,
                    "priority": priority
                })
        
        return questions
    
    def _parse_questions_strategy_3(self, content: str) -> List[Dict[str, Any]]:
        """Parse questions using numbered list strategy."""
        questions = []
        
        # Look for numbered questions (1., 2., etc.)
        lines = content.split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            
            # Check for numbered questions
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                if current_question:
                    questions.append(current_question)
                
                # Start new question
                title = line
                current_question = {
                    "title": title,
                    "question": "",
                    "answer": "",
                    "frequency": "Asked Frequently",
                    "companyTypes": ["MidSize", "MNC"],
                    "priority": "Medium"
                }
            elif current_question:
                # Add content to current question
                if not current_question["question"]:
                    current_question["question"] = line
                else:
                    current_question["answer"] += line + '\n'
        
        # Add the last question
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _create_intelligent_fallback(self, content: str) -> List[Dict[str, Any]]:
        """Create intelligent fallback questions from content."""
        questions = []
        
        # Extract key topics from content
        topics = self._extract_topics_from_content(content)
        
        for i, topic in enumerate(topics[:5], 1):  # Limit to 5 questions
            # Create a question about this topic
            question_text = f"What is {topic} and how is it used in JavaScript?"
            
            # Use AI to determine the characteristics
            frequency = self._ai_determine_frequency(f"Question {i}: {topic}", question_text, content)
            company_types = self._ai_determine_company_types(f"Question {i}: {topic}", question_text, content)
            priority = self._ai_determine_priority(f"Question {i}: {topic}", question_text, content)
            
            questions.append({
                "title": f"Question {i}: {topic}",
                "question": question_text,
                "answer": content[:300] + "..." if len(content) > 300 else content,
                "frequency": frequency,
                "companyTypes": company_types,
                "priority": priority
            })
        
        return questions
    
    def _extract_topics_from_content(self, content: str) -> List[str]:
        """Extract key topics from content for fallback questions."""
        # Common JavaScript topics
        js_topics = [
            "variables", "functions", "objects", "arrays", "closures", 
            "prototypes", "hoisting", "callbacks", "promises", "async/await",
            "DOM manipulation", "event handling", "scope", "this keyword",
            "arrow functions", "destructuring", "spread operator", "modules"
        ]
        
        # Find topics mentioned in content
        found_topics = []
        content_lower = content.lower()
        
        for topic in js_topics:
            if topic in content_lower:
                found_topics.append(topic)
        
        # If no topics found, return some defaults
        if not found_topics:
            found_topics = ["variables", "functions", "objects"]
        
        return found_topics
    
    def _ai_determine_frequency(self, title: str, question: str, answer: str) -> str:
        """Use AI to intelligently determine how frequently this question is asked."""
        
        frequency_prompt = f"""
        You are an expert interviewer with 20+ years of experience who has conducted 300+ interviews at top Indian tech companies.
        
        Analyze this interview question and determine how frequently it's asked in real interviews:
        
        **Question Title:** {title}
        **Question Text:** {question}
        **Answer Content:** {answer[:500]}...
        
        Based on your extensive interview experience, classify this question as:
        
        - "Most Asked" - Questions that appear in 80%+ of interviews for this topic
        - "Asked Frequently" - Questions that appear in 40-80% of interviews for this topic  
        - "Asked Sometimes" - Questions that appear in 10-40% of interviews for this topic
        
        Consider:
        1. **Fundamental vs Advanced**: Basic concepts are asked more frequently
        2. **Practical vs Theoretical**: Hands-on questions are more common
        3. **Industry Relevance**: Questions about real-world scenarios are asked more
        4. **Difficulty Level**: Entry-level questions are asked more than senior-level
        5. **Company Size**: Different companies focus on different question types
        
        Return ONLY the classification: "Most Asked", "Asked Frequently", or "Asked Sometimes"
        """
        
        try:
            response = self._generate_with_prompt(frequency_prompt)
            # Clean the response to get just the classification
            response = response.strip().lower()
            
            if "most asked" in response:
                return "Most Asked"
            elif "asked sometimes" in response:
                return "Asked Sometimes"
            else:
                return "Asked Frequently"  # Default fallback
                
        except Exception as e:
            self.logger.error(f"Error determining frequency: {str(e)}")
            return "Asked Frequently"  # Safe fallback
    
    def _ai_determine_company_types(self, title: str, question: str, answer: str) -> List[str]:
        """Use AI to intelligently determine which company types ask this question."""
        
        company_types_prompt = f"""
        You are an expert interviewer with 20+ years of experience who has conducted 300+ interviews at different types of companies.
        
        Analyze this interview question and determine which company types typically ask it:
        
        **Question Title:** {title}
        **Question Text:** {question}
        **Answer Content:** {answer[:500]}...
        
        Based on your experience, classify which company types ask this question:
        
        **Company Types:**
        - "Startup" - Fast-paced, practical, hands-on questions (Flipkart, Swiggy, Ola, Razorpay)
        - "MidSize" - Balanced, established practices (Freshworks, Zoho, InMobi, Paytm)
        - "MNC" - Enterprise, formal, large-scale (TCS, Infosys, Wipro, Accenture)
        - "FAANG" - Advanced, algorithmic, system design (Google, Meta, Amazon, Microsoft)
        
        **Consider:**
        1. **Question Complexity**: Basic questions → Startup/MidSize, Advanced → MNC/FAANG
        2. **Practical Focus**: Hands-on coding → Startup, Theory → MNC/FAANG
        3. **Industry Focus**: Real-world problems → Startup/MidSize, Academic → FAANG
        4. **Experience Level**: Entry-level → Startup/MidSize, Senior → MNC/FAANG
        5. **Company Culture**: Fast-paced → Startup, Structured → MNC
        
        Return ONLY the company types as a JSON array: ["Startup", "MidSize", "MNC", "FAANG"]
        Choose 1-3 most relevant types. NEVER return an empty array.
        """
        
        try:
            response = self._generate_with_prompt(company_types_prompt)
            
            # Parse the response to extract company types
            response = response.strip().lower()
            
            company_types = []
            
            # Check for each company type in the response
            if "startup" in response:
                company_types.append("Startup")
            if "midsize" in response or "mid-size" in response or "mid size" in response:
                company_types.append("MidSize")
            if "mnc" in response or "multinational" in response or "enterprise" in response:
                company_types.append("MNC")
            if "faang" in response or "google" in response or "meta" in response or "amazon" in response:
                company_types.append("FAANG")
            
            # If no types detected, use intelligent fallback
            if not company_types:
                # Analyze question complexity for fallback
                text = (title + ' ' + question).lower()
                if any(word in text for word in ['basic', 'fundamental', 'syntax', 'variable', 'function']):
                    company_types = ["Startup", "MidSize"]
                elif any(word in text for word in ['advanced', 'complex', 'algorithm', 'system design']):
                    company_types = ["MNC", "FAANG"]
                else:
                    company_types = ["MidSize", "MNC"]
            
            return company_types
                
        except Exception as e:
            self.logger.error(f"Error determining company types: {str(e)}")
            return ["MidSize", "MNC"]  # Safe fallback
    
    def _ai_determine_priority(self, title: str, question: str, answer: str) -> str:
        """Use AI to intelligently determine the priority level of this question."""
        
        priority_prompt = f"""
        You are an expert interviewer with 20+ years of experience who has conducted 300+ interviews.
        
        Analyze this interview question and determine its priority level for interview preparation:
        
        **Question Title:** {title}
        **Question Text:** {question}
        **Answer Content:** {answer[:500]}...
        
        Based on your experience, classify this question's priority as:
        
        - "High" - Essential concepts that candidates MUST know to pass interviews
        - "Medium" - Important concepts that are commonly asked but not critical
        - "Low" - Nice-to-know concepts that are rarely asked or advanced topics
        
        **Consider:**
        1. **Fundamental Knowledge**: Core concepts are High priority
        2. **Interview Frequency**: Frequently asked questions are High/Medium priority
        3. **Career Impact**: Questions that affect hiring decisions are High priority
        4. **Experience Level**: Entry-level questions are High priority, Senior-level are Medium/Low
        5. **Industry Standards**: Standard practices are High priority, advanced topics are Medium/Low
        
        Return ONLY the priority: "High", "Medium", or "Low"
        """
        
        try:
            response = self._generate_with_prompt(priority_prompt)
            # Clean the response to get just the priority
            response = response.strip().lower()
            
            if "high" in response:
                return "High"
            elif "low" in response:
                return "Low"
            else:
                return "Medium"  # Default fallback
                
        except Exception as e:
            self.logger.error(f"Error determining priority: {str(e)}")
            return "Medium"  # Safe fallback
    
    def _determine_roadmap(self, topic: str) -> str:
        """Determine the roadmap category based on the topic."""
        topic_lower = topic.lower()
        
        # Frontend technologies
        frontend_techs = [
            'javascript', 'react', 'vue', 'angular', 'html', 'css',
            'typescript', 'svelte', 'nextjs', 'nuxt', 'frontend',
            'ui', 'ux', 'web', 'browser', 'dom'
        ]
        
        # Backend technologies
        backend_techs = [
            'python', 'java', 'nodejs', 'node.js', 'express', 'django', 'flask',
            'spring', 'php', 'ruby', 'go', 'rust', 'backend', 'api',
            'server', 'database', 'sql', 'nosql', 'mongodb', 'mysql'
        ]
        
        # Fullstack technologies
        fullstack_techs = [
            'mern', 'mean', 'fullstack', 'full stack', 'full-stack',
            'web development', 'full stack development'
        ]
        
        # General tech topics
        general_techs = [
            'dsa', 'data structures', 'algorithms', 'system design',
            'computer science', 'programming', 'coding', 'software',
            'development', 'engineering'
        ]
        
        if any(tech in topic_lower for tech in frontend_techs):
            return 'Frontend'
        elif any(tech in topic_lower for tech in backend_techs):
            return 'Backend'
        elif any(tech in topic_lower for tech in fullstack_techs):
            return 'Fullstack'
        else:
            return 'Tech'  # Default for general topics
    
    def _estimate_question_count(self, content: str) -> int:
        """Estimate number of questions in generated content."""
        # Count markdown headers that likely indicate questions
        question_headers = content.count('## ')
        return max(question_headers, 30)  # Minimum 30 questions
    
    def _estimate_prep_time(self, content: str) -> str:
        """Estimate preparation time for the content."""
        word_count = len(content.split())
        if word_count < 5000:
            return "2-3 hours"
        elif word_count < 10000:
            return "4-6 hours"
        else:
            return "6-8 hours"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def validate_sheet_for_publication(self, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate if sheet data can be published to database.
        
        Args:
            sheet_data: Sheet data to validate
            
        Returns:
            Publication readiness status
        """
        return InterviewQuestionValidator.can_publish_to_db(sheet_data)
    
    def ensure_proper_data_format(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ensure all questions have proper data format.
        
        Args:
            questions: List of questions to validate
            
        Returns:
            List of validated questions
        """
        validated_questions = []
        
        for question in questions:
            validation_result = InterviewQuestionValidator.validate_question_data(question)
            if validation_result["is_valid"]:
                validated_questions.append(validation_result["data"])
            else:
                self.logger.error(f"Question validation failed: {validation_result['errors']}")
                # Create a fallback question with proper format
                fallback_question = {
                    "title": question.get("title", "Sample Question"),
                    "question": question.get("question", "What are the key concepts?"),
                    "answer": question.get("answer", "Sample answer content"),
                    "frequency": "Asked Frequently",
                    "companyTypes": ["MidSize", "MNC"],
                    "priority": "Medium"
                }
                validated_questions.append(fallback_question)
        
        return validated_questions