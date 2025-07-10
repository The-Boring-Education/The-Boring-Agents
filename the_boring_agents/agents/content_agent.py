"""Content generation agent for Shiksha tech courses."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

from ..core.base_agent import BaseAgent


class ContentAgent(BaseAgent):
    """Agent for generating tech course content including video suggestions and text content."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for content generation."""
        
        course_outline_template = PromptTemplate(
            input_variables=["topic", "level", "duration"],
            template="""
            Create a comprehensive course outline for a {level} level course on {topic}.
            The course should be designed for {duration} duration.
            
            Please structure your response as follows:
            1. Course Title
            2. Course Description (2-3 sentences)
            3. Learning Objectives (3-5 bullet points)
            4. Course Modules (5-8 modules with titles and brief descriptions)
            5. Prerequisites
            6. Target Audience
            
            Make the content engaging and practical with real-world applications.
            """
        )
        
        video_suggestions_template = PromptTemplate(
            input_variables=["topic", "module_title"],
            template="""
            Suggest 5-7 high-quality YouTube videos or video content ideas for the module "{module_title}" 
            in a course about {topic}.
            
            For each suggestion, provide:
            1. Video Title/Topic
            2. Key concepts it should cover
            3. Estimated duration
            4. Why it's valuable for learners
            5. Suggested search keywords for finding similar content
            
            Focus on practical, hands-on content that includes real examples and projects.
            """
        )
        
        text_content_template = PromptTemplate(
            input_variables=["topic", "module_title", "subtopic"],
            template="""
            Create detailed text content for the subtopic "{subtopic}" within the module "{module_title}" 
            of a {topic} course.
            
            Include:
            1. Clear explanation of the concept
            2. 3-5 practical tips and tricks
            3. Common pitfalls to avoid
            4. Real-world examples
            5. Best practices
            6. Quick reference/cheat sheet section
            7. Practice exercises or challenges
            
            Write in an engaging, conversational tone that makes complex concepts easy to understand.
            Use code examples where appropriate.
            """
        )
        
        tricks_and_tips_template = PromptTemplate(
            input_variables=["topic", "experience_level"],
            template="""
            Generate 10 valuable tricks and tips for {experience_level} developers working with {topic}.
            
            For each tip, provide:
            1. The trick/tip title
            2. Detailed explanation
            3. Code example (if applicable)
            4. When to use it
            5. Common mistakes to avoid
            
            Focus on practical, actionable advice that can immediately improve their skills.
            Include both fundamental concepts and advanced techniques.
            """
        )
        
        return {
            "course_outline": course_outline_template,
            "video_suggestions": video_suggestions_template,
            "text_content": text_content_template,
            "tricks_and_tips": tricks_and_tips_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on the specified type.
        
        Args:
            content_type: Type of content to generate (course_outline, video_suggestions, 
                         text_content, tricks_and_tips)
            **kwargs: Parameters specific to the content type
            
        Returns:
            Generated content with metadata
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
                "word_count": len(generated_text.split())
            }
        }
        
        return result
    
    def create_course_outline(self, topic: str, level: str = "intermediate", 
                            duration: str = "4 weeks") -> Dict[str, Any]:
        """Create a complete course outline.
        
        Args:
            topic: The course topic
            level: Difficulty level (beginner, intermediate, advanced)
            duration: Course duration
            
        Returns:
            Course outline with structured content
        """
        return self.generate_content(
            "course_outline",
            topic=topic,
            level=level,
            duration=duration
        )
    
    def suggest_videos(self, topic: str, module_title: str) -> Dict[str, Any]:
        """Suggest videos for a specific module.
        
        Args:
            topic: The course topic
            module_title: Title of the specific module
            
        Returns:
            Video suggestions with details
        """
        return self.generate_content(
            "video_suggestions",
            topic=topic,
            module_title=module_title
        )
    
    def create_text_content(self, topic: str, module_title: str, 
                          subtopic: str) -> Dict[str, Any]:
        """Create detailed text content for a subtopic.
        
        Args:
            topic: The course topic
            module_title: Title of the module
            subtopic: Specific subtopic to cover
            
        Returns:
            Detailed text content
        """
        return self.generate_content(
            "text_content",
            topic=topic,
            module_title=module_title,
            subtopic=subtopic
        )
    
    def generate_tricks_and_tips(self, topic: str, 
                               experience_level: str = "intermediate") -> Dict[str, Any]:
        """Generate practical tricks and tips.
        
        Args:
            topic: The technology/topic
            experience_level: Target experience level
            
        Returns:
            List of tricks and tips
        """
        return self.generate_content(
            "tricks_and_tips",
            topic=topic,
            experience_level=experience_level
        )
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()