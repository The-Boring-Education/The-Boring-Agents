"""Interview preparation agent for generating question sheets."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

from ..core.base_agent import BaseAgent


class InterviewAgent(BaseAgent):
    """Agent for generating interview preparation content in sheet format."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for interview content generation."""
        
        question_sheet_template = PromptTemplate(
            input_variables=["technology", "experience_level", "question_count"],
            template="""
            Create a comprehensive interview question sheet for {technology} targeting {experience_level} level candidates.
            Generate {question_count} questions covering different aspects and difficulty levels.
            
            For each question, provide:
            1. Question text
            2. Detailed answer/explanation
            3. Difficulty level (1-5)
            4. Key concepts tested
            5. Follow-up questions (if applicable)
            6. Code example (if relevant)
            
            Cover these areas:
            - Fundamentals and core concepts
            - Practical implementation
            - Problem-solving scenarios
            - Best practices
            - Advanced concepts
            - Real-world applications
            
            Format as a structured sheet that's easy to review and practice with.
            """
        )
        
        coding_challenges_template = PromptTemplate(
            input_variables=["technology", "difficulty", "challenge_count"],
            template="""
            Create {challenge_count} coding challenges for {technology} at {difficulty} difficulty level.
            
            For each challenge, provide:
            1. Problem statement
            2. Input/Output examples
            3. Constraints
            4. Expected time complexity
            5. Expected space complexity
            6. Sample solution with explanation
            7. Alternative approaches
            8. Edge cases to consider
            
            Make the challenges practical and relevant to real-world scenarios.
            Include problems that test different skills like algorithms, data structures, and system design.
            """
        )
        
        behavioral_questions_template = PromptTemplate(
            input_variables=["role_type", "experience_level"],
            template="""
            Generate behavioral interview questions for a {role_type} position targeting {experience_level} candidates.
            
            Create 15-20 questions covering:
            1. Leadership and teamwork
            2. Problem-solving and decision-making
            3. Communication and collaboration
            4. Adaptability and learning
            5. Project management
            6. Conflict resolution
            7. Innovation and creativity
            
            For each question, provide:
            - The question text
            - What the interviewer is looking for
            - STAR method framework for answering
            - Sample answer structure
            - Red flags to avoid
            """
        )
        
        system_design_template = PromptTemplate(
            input_variables=["system_type", "complexity_level"],
            template="""
            Create system design interview questions for {system_type} systems at {complexity_level} complexity.
            
            Generate 5-7 comprehensive system design questions including:
            1. Problem statement
            2. Requirements (functional and non-functional)
            3. Scale expectations (users, data, requests/sec)
            4. Key components to discuss
            5. Database design considerations
            6. API design
            7. Scalability challenges
            8. Sample architecture diagram description
            9. Technology stack recommendations
            10. Trade-offs to discuss
            
            Focus on real-world systems that candidates might encounter in the industry.
            """
        )
        
        return {
            "question_sheet": question_sheet_template,
            "coding_challenges": coding_challenges_template,
            "behavioral_questions": behavioral_questions_template,
            "system_design": system_design_template
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
    
    def create_question_sheet(self, technology: str, experience_level: str = "intermediate",
                            question_count: int = 25) -> Dict[str, Any]:
        """Create a comprehensive question sheet for a technology.
        
        Args:
            technology: The technology/framework to focus on
            experience_level: Target experience level
            question_count: Number of questions to generate
            
        Returns:
            Complete question sheet with answers
        """
        return self.generate_content(
            "question_sheet",
            technology=technology,
            experience_level=experience_level,
            question_count=question_count
        )
    
    def create_coding_challenges(self, technology: str, difficulty: str = "medium",
                               challenge_count: int = 10) -> Dict[str, Any]:
        """Create coding challenges for interview preparation.
        
        Args:
            technology: The technology/language
            difficulty: Challenge difficulty (easy, medium, hard)
            challenge_count: Number of challenges to generate
            
        Returns:
            Coding challenges with solutions
        """
        return self.generate_content(
            "coding_challenges",
            technology=technology,
            difficulty=difficulty,
            challenge_count=challenge_count
        )
    
    def create_behavioral_questions(self, role_type: str = "Software Engineer",
                                  experience_level: str = "mid-level") -> Dict[str, Any]:
        """Create behavioral interview questions.
        
        Args:
            role_type: Type of role (Software Engineer, Tech Lead, etc.)
            experience_level: Target experience level
            
        Returns:
            Behavioral questions with answer guidance
        """
        return self.generate_content(
            "behavioral_questions",
            role_type=role_type,
            experience_level=experience_level
        )
    
    def create_system_design_questions(self, system_type: str = "web applications",
                                     complexity_level: str = "medium") -> Dict[str, Any]:
        """Create system design interview questions.
        
        Args:
            system_type: Type of systems to focus on
            complexity_level: Complexity level (low, medium, high)
            
        Returns:
            System design questions with guidance
        """
        return self.generate_content(
            "system_design",
            system_type=system_type,
            complexity_level=complexity_level
        )
    
    def create_complete_interview_prep(self, technology: str, 
                                     experience_level: str = "intermediate") -> Dict[str, Any]:
        """Create a complete interview preparation package.
        
        Args:
            technology: Primary technology to focus on
            experience_level: Target experience level
            
        Returns:
            Complete interview prep package
        """
        # Generate all types of content
        question_sheet = self.create_question_sheet(technology, experience_level)
        coding_challenges = self.create_coding_challenges(technology)
        behavioral_questions = self.create_behavioral_questions("Software Engineer", experience_level)
        system_design = self.create_system_design_questions()
        
        return {
            "technology": technology,
            "experience_level": experience_level,
            "components": {
                "technical_questions": question_sheet,
                "coding_challenges": coding_challenges,
                "behavioral_questions": behavioral_questions,
                "system_design": system_design
            },
            "metadata": {
                "created_at": self._get_timestamp(),
                "total_prep_time": "15-20 hours",
                "recommended_study_plan": self._create_study_plan()
            }
        }
    
    def _estimate_question_count(self, content: str) -> int:
        """Estimate number of questions in generated content."""
        # Simple heuristic: count question marks and numbered items
        question_marks = content.count('?')
        numbered_items = len([line for line in content.split('\n') if line.strip().startswith(('1.', '2.', '3.'))])
        return max(question_marks, numbered_items)
    
    def _estimate_prep_time(self, content: str) -> str:
        """Estimate preparation time for the content."""
        word_count = len(content.split())
        if word_count < 1000:
            return "1-2 hours"
        elif word_count < 3000:
            return "3-5 hours"
        else:
            return "6-8 hours"
    
    def _create_study_plan(self) -> List[str]:
        """Create a recommended study plan."""
        return [
            "Week 1: Review technical questions and core concepts",
            "Week 2: Practice coding challenges and algorithms",
            "Week 3: Prepare behavioral stories using STAR method",
            "Week 4: Practice system design and mock interviews"
        ]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()