"""Exercise Creator Agent for generating hands-on exercises and projects."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent


class ExerciseCreatorAgent(BaseAgent):
    """Agent for creating hands-on exercises, projects, and coding challenges."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for exercise creation."""
        
        hands_on_exercises_template = PromptTemplate(
            input_variables=["topic", "difficulty_level", "learning_objectives", "indian_context"],
            template="""
            Create hands-on exercises for {topic} that will make Indian students fall in love with coding.
            
            Difficulty Level: {difficulty_level}
            Learning Objectives: {learning_objectives}
            Indian Context: {indian_context}
            
            Design 5-7 progressive exercises:
            
            1. **Warm-up Exercise (Super Easy)**
               - Something they can complete in 10-15 minutes
               - Builds confidence and motivation
               - Uses familiar Indian scenarios
            
            2. **Skill Building Exercises (Easy to Medium)**
               - 2-3 exercises that build core skills
               - Each takes 20-30 minutes
               - Clear step-by-step instructions
               - Indian context examples
            
            3. **Real-world Application (Medium)**
               - Solve a problem that Indian companies face
               - Use Indian apps/websites as inspiration
               - Takes 45-60 minutes to complete
            
            4. **Challenge Exercise (Medium to Hard)**
               - Push their thinking and creativity
               - Multiple solutions possible
               - Encourages experimentation
            
            5. **Portfolio Project (Hard)**
               - Something they can showcase to employers
               - Relevant to Indian job market
               - Takes 2-3 hours but worth it
            
            For each exercise, provide:
            - **Problem Statement** (in story format with Indian context)
            - **Learning Goals** (what skills they'll practice)
            - **Step-by-step Hints** (not full solutions, just guidance)
            - **Expected Output** (what success looks like)
            - **Extension Ideas** (for advanced learners)
            - **Real-world Connection** (how this applies to jobs in India)
            
            Make exercises fun, relevant, and progressively challenging!
            """
        )
        
        coding_projects_template = PromptTemplate(
            input_variables=["topic", "difficulty_level", "target_skills", "time_commitment"],
            template="""
            Design a coding project for {topic} that Indian students will be excited to build.
            
            Difficulty Level: {difficulty_level}
            Target Skills: {target_skills}
            Time Commitment: {time_commitment}
            
            Project Structure:
            
            1. **Project Overview**
               - Compelling project name and description
               - Real-world problem it solves (Indian context)
               - Why this project will impress Indian recruiters
               - Technologies and skills involved
            
            2. **Indian Theme Integration**
               - Use Indian festivals, food, travel, or business scenarios
               - Reference popular Indian apps for inspiration
               - Include cultural elements that students relate to
               - Make it relevant to Indian market needs
            
            3. **Learning Journey**
               - Phase 1: Basic setup and foundation (25% of time)
               - Phase 2: Core functionality (50% of time)
               - Phase 3: Polish and advanced features (25% of time)
               - Clear milestones and celebration points
            
            4. **Technical Implementation**
               - Detailed requirements and user stories
               - Database schema (if applicable)
               - API endpoints and functionality
               - Frontend/UI considerations
               - Testing strategy
            
            5. **Career Connection**
               - How to present this in portfolio
               - Interview talking points
               - Skills this demonstrates to employers
               - Possible extensions for different job roles
            
            6. **Deployment and Sharing**
               - How to deploy and showcase
               - Creating demo videos or presentations
               - Sharing on LinkedIn and GitHub
               - Building personal brand around the project
            
            Make it practical, career-focused, and genuinely interesting to build!
            """
        )
        
        interview_preparation_template = PromptTemplate(
            input_variables=["topic", "difficulty_level", "company_context"],
            template="""
            Create interview-style coding problems for {topic} that prepare students for Indian company interviews.
            
            Difficulty Level: {difficulty_level}
            Company Context: {company_context}
            
            Design 4-5 interview questions:
            
            1. **Warm-up Question (Easy)**
               - Something to break the ice
               - Tests basic understanding
               - 5-10 minutes to solve
               - Based on Indian scenarios
            
            2. **Technical Knowledge Questions (Medium)**
               - 2-3 questions testing core concepts
               - Mix of theoretical and practical
               - 15-20 minutes each
               - Include edge cases and optimizations
            
            3. **Problem-solving Challenge (Hard)**
               - Open-ended problem requiring creativity
               - Multiple approaches possible
               - 30-45 minutes to solve
               - Tests algorithmic thinking
            
            For each question, provide:
            
            **Question Format:**
            - **Scenario Setup** (Indian business context)
            - **Problem Statement** (clear and specific)
            - **Input/Output Examples** (with explanations)
            - **Constraints and Requirements**
            
            **For Instructors:**
            - **Expected Solution Approach**
            - **Key Concepts Being Tested**
            - **Common Mistakes to Watch For**
            - **Follow-up Questions for Deeper Discussion**
            - **Difficulty Variations** (easier/harder versions)
            
            **Indian Company Focus:**
            - Problems similar to what Flipkart, Paytm, Ola might ask
            - Scenarios relevant to Indian business challenges
            - Cultural context that Indian students understand
            
            Make questions challenging but fair, with clear learning value!
            """
        )
        
        practical_assignments_template = PromptTemplate(
            input_variables=["topic", "learning_objectives", "assessment_criteria", "collaboration_level"],
            template="""
            Create practical assignments for {topic} that students will actually want to complete.
            
            Learning Objectives: {learning_objectives}
            Assessment Criteria: {assessment_criteria}
            Collaboration Level: {collaboration_level}
            
            Assignment Design:
            
            1. **Assignment Overview**
               - Engaging title and description
               - Clear learning outcomes
               - Time investment required
               - Prerequisites and setup
            
            2. **Real-world Relevance**
               - Problem statement based on Indian business needs
               - Use cases from Indian startups or established companies
               - Skills that directly transfer to job requirements
               - Career impact and portfolio value
            
            3. **Progressive Structure**
               - **Starter Tasks** (build confidence)
               - **Core Assignment** (main learning objectives)
               - **Stretch Goals** (for advanced learners)
               - **Bonus Challenges** (creativity and innovation)
            
            4. **Indian Context Integration**
               - Data sets using Indian cities, festivals, or businesses
               - Scenarios familiar to Indian students
               - Cultural references that enhance engagement
               - Local market examples and case studies
            
            5. **Collaboration Elements**
               - Individual vs. group work balance
               - Peer review and feedback opportunities
               - Code review simulation (like real companies)
               - Knowledge sharing components
            
            6. **Assessment and Feedback**
               - Clear rubric and success criteria
               - Self-assessment checkpoints
               - Peer evaluation opportunities
               - Portfolio presentation guidelines
            
            7. **Submission and Showcase**
               - Professional presentation format
               - Demo day or showcase opportunity
               - LinkedIn posting templates
               - GitHub repository best practices
            
            Make assignments meaningful, engaging, and career-relevant!
            """
        )
        
        return {
            "hands_on_exercises": hands_on_exercises_template,
            "coding_projects": coding_projects_template,
            "interview_preparation": interview_preparation_template,
            "practical_assignments": practical_assignments_template
        }
    
    def create_hands_on_exercises(self, topic: str, difficulty_level: str, 
                                learning_objectives: List[str],
                                indian_context: str = "") -> str:
        """Create hands-on exercises for a topic.
        
        Args:
            topic: Topic to create exercises for
            difficulty_level: Target difficulty level
            learning_objectives: List of learning objectives
            indian_context: Indian context for the exercises
            
        Returns:
            Hands-on exercises content
        """
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives])
        context = indian_context or "Indian tech industry and student life"
        
        result = self.generate_content(
            "hands_on_exercises",
            topic=topic,
            difficulty_level=difficulty_level,
            learning_objectives=objectives_text,
            indian_context=context
        )
        
        return result["generated_content"]
    
    def design_coding_project(self, topic: str, difficulty_level: str,
                            target_skills: List[str], time_commitment: str = "") -> str:
        """Design a comprehensive coding project.
        
        Args:
            topic: Topic for the project
            difficulty_level: Target difficulty level
            target_skills: Skills to be practiced
            time_commitment: Expected time commitment
            
        Returns:
            Coding project design
        """
        skills_text = ", ".join(target_skills)
        time_info = time_commitment or "2-3 hours over 1 week"
        
        result = self.generate_content(
            "coding_projects",
            topic=topic,
            difficulty_level=difficulty_level,
            target_skills=skills_text,
            time_commitment=time_info
        )
        
        return result["generated_content"]
    
    def create_interview_problems(self, topic: str, difficulty_level: str,
                                company_context: str = "") -> str:
        """Create interview-style coding problems.
        
        Args:
            topic: Topic for interview problems
            difficulty_level: Target difficulty level
            company_context: Context of target companies
            
        Returns:
            Interview problems content
        """
        context = company_context or "Indian tech companies (startups and MNCs)"
        
        result = self.generate_content(
            "interview_preparation",
            topic=topic,
            difficulty_level=difficulty_level,
            company_context=context
        )
        
        return result["generated_content"]
    
    def design_practical_assignment(self, topic: str, learning_objectives: List[str],
                                  assessment_criteria: str = "",
                                  collaboration_level: str = "") -> str:
        """Design a practical assignment.
        
        Args:
            topic: Topic for the assignment
            learning_objectives: Learning objectives to achieve
            assessment_criteria: How assignment will be assessed
            collaboration_level: Level of collaboration expected
            
        Returns:
            Practical assignment design
        """
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives])
        criteria = assessment_criteria or "Technical correctness, code quality, creativity, presentation"
        collaboration = collaboration_level or "Individual work with peer review"
        
        result = self.generate_content(
            "practical_assignments",
            topic=topic,
            learning_objectives=objectives_text,
            assessment_criteria=criteria,
            collaboration_level=collaboration
        )
        
        return result["generated_content"]
    
    def create_comprehensive_exercise_suite(self, chapter_name: str, topic: str,
                                          difficulty_level: str, learning_objectives: List[str],
                                          time_budget: str = "") -> Dict[str, str]:
        """Create a comprehensive suite of exercises for a chapter.
        
        Args:
            chapter_name: Name of the chapter
            topic: Main topic
            difficulty_level: Target difficulty level
            learning_objectives: Learning objectives
            time_budget: Available time for exercises
            
        Returns:
            Dictionary with different types of exercises
        """
        exercises = {}
        
        # Create hands-on exercises
        exercises["hands_on_exercises"] = self.create_hands_on_exercises(
            topic, difficulty_level, learning_objectives,
            f"Chapter on {chapter_name}"
        )
        
        # Design a coding project
        exercises["coding_project"] = self.design_coding_project(
            topic, difficulty_level, learning_objectives,
            time_budget or "3-4 hours over 1 week"
        )
        
        # Create interview problems
        exercises["interview_problems"] = self.create_interview_problems(
            topic, difficulty_level
        )
        
        # Design practical assignment
        exercises["practical_assignment"] = self.design_practical_assignment(
            topic, learning_objectives
        )
        
        return exercises
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate exercise content based on the content type."""
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