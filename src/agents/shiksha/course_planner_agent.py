"""Course Planning Agent for creating comprehensive course structures."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate
import json
import re

from src.core.base_agent import BaseAgent


class CoursePlannerAgent(BaseAgent):
    """Agent for planning and structuring tech courses."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for course planning."""
        
        course_structure_template = PromptTemplate(
            input_variables=["course_name", "description", "difficulty_level", "roadmap"],
            template="""
            You are an expert curriculum designer for The Boring Education's Shiksha platform.
            
            Create a comprehensive course structure for: "{course_name}"
            Description: {description}
            Difficulty Level: {difficulty_level}
            Roadmap: {roadmap}
            
            Design a course with 15-20 chapters that follows this structure:
            
            1. **Foundation Chapters (3-4 chapters)**
               - Prerequisites and setup
               - Basic concepts and terminology
               - Environment setup
            
            2. **Core Concepts (8-10 chapters)**
               - Main topics and skills
               - Practical implementations
               - Real-world applications
            
            3. **Advanced Topics (3-4 chapters)**
               - Complex concepts
               - Best practices
               - Industry standards
            
            4. **Projects & Practice (2-3 chapters)**
               - Hands-on projects
               - Real-world scenarios
               - Portfolio building
            
            For each chapter, provide:
            - Chapter name (clear, descriptive)
            - Learning objectives (3-5 points)
            - Estimated time to complete
            - Prerequisites (if any)
            - Key skills covered
            
            Focus on:
            - Practical, hands-on learning
            - Real-world applications
            - Industry-relevant skills
            - Progressive difficulty
            - Project-based learning
            
            Return a structured JSON with course metadata and detailed chapter plan.
            """
        )
        
        chapter_breakdown_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "chapter_number", "total_chapters", "difficulty_level"],
            template="""
            Create a detailed breakdown for chapter "{chapter_name}" in the "{course_name}" course.
            This is chapter {chapter_number} of {total_chapters} for {difficulty_level} level learners.
            
            Provide:
            1. **Learning Objectives** (3-5 specific goals)
            2. **Key Concepts** (main topics to cover)
            3. **Prerequisites** (what learners should know)
            4. **Estimated Time** (realistic time commitment)
            5. **Practical Applications** (real-world use cases)
            6. **Common Challenges** (what learners might struggle with)
            7. **Success Metrics** (how to know they've learned it)
            
            Make it practical and actionable for learners.
            """
        )
        
        return {
            "course_structure": course_structure_template,
            "chapter_breakdown": chapter_breakdown_template
        }
    
    def create_course_structure(self, course_name: str, description: str, 
                              difficulty_level: str, roadmap: str) -> Dict[str, Any]:
        """Create a comprehensive course structure.
        
        Args:
            course_name: Name of the course
            description: Course description
            difficulty_level: Beginner, Intermediate, or Advanced
            roadmap: Backend, Frontend, Full Stack, etc.
            
        Returns:
            Structured course plan with metadata and chapters
        """
        result = self.generate_content(
            "course_structure",
            course_name=course_name,
            description=description,
            difficulty_level=difficulty_level,
            roadmap=roadmap
        )
        
        # Parse the structured response
        return self._parse_course_structure(result["generated_content"])
    
    def create_chapter_breakdown(self, chapter_name: str, course_name: str, 
                               chapter_number: int, total_chapters: int, 
                               difficulty_level: str) -> Dict[str, Any]:
        """Create detailed breakdown for a specific chapter.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            chapter_number: Chapter number
            total_chapters: Total number of chapters
            difficulty_level: Difficulty level
            
        Returns:
            Detailed chapter breakdown
        """
        result = self.generate_content(
            "chapter_breakdown",
            chapter_name=chapter_name,
            course_name=course_name,
            chapter_number=chapter_number,
            total_chapters=total_chapters,
            difficulty_level=difficulty_level
        )
        
        return self._parse_chapter_breakdown(result["generated_content"])
    
    def _parse_course_structure(self, content: str) -> Dict[str, Any]:
        """Parse the generated course structure content."""
        # Try to extract JSON if present
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # Fallback: create structured response from text
        return self._extract_structure_from_text(content)
    
    def _parse_chapter_breakdown(self, content: str) -> Dict[str, Any]:
        """Parse chapter breakdown content."""
        # Extract structured information from text
        breakdown = {}
        
        # Extract learning objectives
        objectives_match = re.search(r'Learning Objectives?:(.*?)(?=\n\n|\n[A-Z]|$)', content, re.DOTALL | re.IGNORECASE)
        if objectives_match:
            breakdown["learning_objectives"] = [obj.strip() for obj in objectives_match.group(1).split('\n') if obj.strip()]
        
        # Extract key concepts
        concepts_match = re.search(r'Key Concepts?:(.*?)(?=\n\n|\n[A-Z]|$)', content, re.DOTALL | re.IGNORECASE)
        if concepts_match:
            breakdown["key_concepts"] = [concept.strip() for concept in concepts_match.group(1).split('\n') if concept.strip()]
        
        # Extract estimated time
        time_match = re.search(r'Estimated Time?:(.*?)(?=\n\n|\n[A-Z]|$)', content, re.IGNORECASE)
        if time_match:
            breakdown["estimated_time"] = time_match.group(1).strip()
        
        # Extract prerequisites
        prereq_match = re.search(r'Prerequisites?:(.*?)(?=\n\n|\n[A-Z]|$)', content, re.DOTALL | re.IGNORECASE)
        if prereq_match:
            breakdown["prerequisites"] = [prereq.strip() for prereq in prereq_match.group(1).split('\n') if prereq.strip()]
        
        return breakdown
    
    def _extract_structure_from_text(self, content: str) -> Dict[str, Any]:
        """Extract course structure from text content."""
        structure = {
            "metadata": {},
            "chapters": []
        }
        
        # Extract course metadata
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "Course Name:" in line or "Title:" in line:
                structure["metadata"]["name"] = line.split(":", 1)[1].strip()
            elif "Description:" in line:
                structure["metadata"]["description"] = line.split(":", 1)[1].strip()
            elif "Difficulty:" in line:
                structure["metadata"]["difficulty"] = line.split(":", 1)[1].strip()
            elif "Roadmap:" in line:
                structure["metadata"]["roadmap"] = line.split(":", 1)[1].strip()
            elif "Chapter" in line and ("." in line or ":" in line):
                # Extract chapter information
                chapter_info = self._extract_chapter_info(line)
                if chapter_info:
                    structure["chapters"].append(chapter_info)
        
        return structure
    
    def _extract_chapter_info(self, line: str) -> Dict[str, Any]:
        """Extract chapter information from a line."""
        # Look for patterns like "Chapter 1: Introduction" or "1. Introduction"
        chapter_match = re.search(r'(?:Chapter\s+)?(\d+)[:.]\s*(.+)', line)
        if chapter_match:
            return {
                "number": int(chapter_match.group(1)),
                "name": chapter_match.group(2).strip(),
                "learning_objectives": [],
                "estimated_time": "",
                "prerequisites": []
            }
        return None
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on the content type.
        
        Args:
            content_type: Type of content to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated content as a dictionary
        """
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