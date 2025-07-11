"""Quality Assurance Agent for reviewing and refining course content."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import json
import re

from ..core.base_agent import BaseAgent


class QualityAssuranceAgent(BaseAgent):
    """Agent for reviewing and ensuring quality of course content."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for quality assurance."""
        
        course_review_template = PromptTemplate(
            input_variables=["course_data", "course_name", "difficulty_level"],
            template="""
            You are a senior course manager at The Boring Education reviewing a Shiksha course.
            
            Course: {course_name}
            Difficulty Level: {difficulty_level}
            
            Review the following course data and provide feedback:
            
            {course_data}
            
            Evaluate the course on:
            
            1. **Structure & Flow**
               - Logical progression of chapters
               - Appropriate difficulty progression
               - Complete coverage of the topic
            
            2. **Content Quality**
               - Engaging and clear explanations
               - Practical, hands-on approach
               - Real-world relevance
            
            3. **Learning Experience**
               - Clear learning objectives
               - Appropriate time estimates
               - Effective video curation
            
            4. **Technical Accuracy**
               - Correct technical information
               - Up-to-date content
               - Proper code examples
            
            5. **Engagement & Motivation**
               - Inspiring content
               - Clear value proposition
               - Social sharing elements
            
            Provide specific recommendations for improvement.
            Return a structured review with scores (1-10) for each category.
            """
        )
        
        chapter_review_template = PromptTemplate(
            input_variables=["chapter_content", "chapter_name", "course_name", "difficulty_level"],
            template="""
            Review the following chapter content for quality and completeness:
            
            Chapter: {chapter_name}
            Course: {course_name}
            Difficulty: {difficulty_level}
            
            Content:
            {chapter_content}
            
            Evaluate:
            
            1. **Content Completeness**
               - All required sections present
               - Clear explanations
               - Proper MDX formatting
            
            2. **Video Curation**
               - Recent, high-quality videos
               - Good coverage of topics
               - Appropriate for difficulty level
            
            3. **Practical Elements**
               - Hands-on projects
               - Practice problems
               - Real-world applications
            
            4. **Engagement**
               - Motivational elements
               - Social sharing templates
               - Clear learning path
            
            5. **Technical Quality**
               - Accurate information
               - Proper code examples
               - Clear instructions
            
            Provide specific feedback and suggestions for improvement.
            """
        )
        
        content_refinement_template = PromptTemplate(
            input_variables=["content", "feedback", "chapter_name", "difficulty_level"],
            template="""
            Refine the following content based on the provided feedback:
            
            Chapter: {chapter_name}
            Difficulty: {difficulty_level}
            Feedback: {feedback}
            
            Original Content:
            {content}
            
            Improve the content by:
            1. Addressing feedback points
            2. Enhancing clarity and engagement
            3. Ensuring proper MDX formatting
            4. Adding missing elements
            5. Improving flow and structure
            
            Return the refined content in proper MDX format.
            """
        )
        
        final_validation_template = PromptTemplate(
            input_variables=["course_json", "course_name"],
            template="""
            Perform final validation of the complete course JSON for "{course_name}":
            
            {course_json}
            
            Validate:
            
            1. **JSON Structure**
               - Correct schema format
               - All required fields present
               - Valid data types
            
            2. **Content Quality**
               - All chapters have content
               - Proper MDX formatting
               - Complete metadata
            
            3. **Technical Requirements**
               - Valid IDs and timestamps
               - Proper URLs and slugs
               - Correct field names
            
            4. **Shiksha Compatibility**
               - Follows platform requirements
               - Proper chapter structure
               - Valid content format
            
            Return validation results and any issues found.
            """
        )
        
        return {
            "course_review": course_review_template,
            "chapter_review": chapter_review_template,
            "content_refinement": content_refinement_template,
            "final_validation": final_validation_template
        }
    
    def review_course_structure(self, course_data: Dict[str, Any], course_name: str, 
                              difficulty_level: str) -> Dict[str, Any]:
        """Review the overall course structure and provide feedback.
        
        Args:
            course_data: Complete course data
            course_name: Name of the course
            difficulty_level: Difficulty level
            
        Returns:
            Review results with scores and recommendations
        """
        # Convert course data to readable format
        course_text = self._format_course_for_review(course_data)
        
        result = self.generate_content(
            "course_review",
            course_data=course_text,
            course_name=course_name,
            difficulty_level=difficulty_level
        )
        
        return self._parse_review_results(result["generated_content"])
    
    def review_chapter_content(self, chapter_content: str, chapter_name: str, 
                             course_name: str, difficulty_level: str) -> Dict[str, Any]:
        """Review individual chapter content.
        
        Args:
            chapter_content: Chapter content in MDX format
            chapter_name: Name of the chapter
            course_name: Name of the course
            difficulty_level: Difficulty level
            
        Returns:
            Chapter review results
        """
        result = self.generate_content(
            "chapter_review",
            chapter_content=chapter_content,
            chapter_name=chapter_name,
            course_name=course_name,
            difficulty_level=difficulty_level
        )
        
        return self._parse_chapter_review(result["generated_content"])
    
    def refine_content(self, content: str, feedback: str, chapter_name: str, 
                      difficulty_level: str) -> str:
        """Refine content based on feedback.
        
        Args:
            content: Original content
            feedback: Review feedback
            chapter_name: Name of the chapter
            difficulty_level: Difficulty level
            
        Returns:
            Refined content
        """
        result = self.generate_content(
            "content_refinement",
            content=content,
            feedback=feedback,
            chapter_name=chapter_name,
            difficulty_level=difficulty_level
        )
        
        return result["generated_content"]
    
    def validate_final_course(self, course_json: Dict[str, Any], course_name: str) -> Dict[str, Any]:
        """Perform final validation of the complete course.
        
        Args:
            course_json: Complete course JSON
            course_name: Name of the course
            
        Returns:
            Validation results
        """
        # Convert to JSON string for review
        course_json_str = json.dumps(course_json, indent=2)
        
        result = self.generate_content(
            "final_validation",
            course_json=course_json_str,
            course_name=course_name
        )
        
        return self._parse_validation_results(result["generated_content"])
    
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
    
    def _format_course_for_review(self, course_data: Dict[str, Any]) -> str:
        """Format course data for review."""
        formatted = []
        
        # Course metadata
        data = course_data.get("data", {})
        formatted.append(f"Course Name: {data.get('name', 'N/A')}")
        formatted.append(f"Description: {data.get('description', 'N/A')}")
        formatted.append(f"Difficulty: {data.get('difficultyLevel', 'N/A')}")
        formatted.append(f"Roadmap: {data.get('roadmap', 'N/A')}")
        formatted.append(f"Meta Content: {data.get('meta', 'N/A')}")
        formatted.append("")
        
        # Chapters
        chapters = data.get("chapters", [])
        formatted.append(f"Total Chapters: {len(chapters)}")
        formatted.append("")
        
        for i, chapter in enumerate(chapters, 1):
            formatted.append(f"Chapter {i}: {chapter.get('name', 'N/A')}")
            content = chapter.get('content', '')
            # Truncate content for review
            if len(content) > 500:
                content = content[:500] + "..."
            formatted.append(f"Content Preview: {content}")
            formatted.append("")
        
        return "\n".join(formatted)
    
    def _parse_review_results(self, content: str) -> Dict[str, Any]:
        """Parse course review results."""
        review = {
            "scores": {},
            "recommendations": [],
            "overall_score": 0
        }
        
        # Extract scores
        score_pattern = r'(\w+):\s*(\d+)/10'
        scores = re.findall(score_pattern, content)
        for category, score in scores:
            review["scores"][category.lower()] = int(score)
        
        # Extract recommendations
        rec_pattern = r'(?:Recommendation|Suggestion):\s*(.+)'
        recommendations = re.findall(rec_pattern, content, re.IGNORECASE)
        review["recommendations"] = recommendations
        
        # Calculate overall score
        if review["scores"]:
            review["overall_score"] = sum(review["scores"].values()) / len(review["scores"])
        
        return review
    
    def _parse_chapter_review(self, content: str) -> Dict[str, Any]:
        """Parse chapter review results."""
        review = {
            "scores": {},
            "feedback": [],
            "improvements": []
        }
        
        # Extract feedback points
        feedback_pattern = r'(?:Feedback|Issue):\s*(.+)'
        feedback = re.findall(feedback_pattern, content, re.IGNORECASE)
        review["feedback"] = feedback
        
        # Extract improvement suggestions
        improvement_pattern = r'(?:Improvement|Suggestion):\s*(.+)'
        improvements = re.findall(improvement_pattern, content, re.IGNORECASE)
        review["improvements"] = improvements
        
        return review
    
    def _parse_validation_results(self, content: str) -> Dict[str, Any]:
        """Parse validation results."""
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check for validation issues
        if "error" in content.lower() or "invalid" in content.lower():
            validation["is_valid"] = False
        
        # Extract issues
        issue_pattern = r'(?:Issue|Error):\s*(.+)'
        issues = re.findall(issue_pattern, content, re.IGNORECASE)
        validation["issues"] = issues
        
        # Extract warnings
        warning_pattern = r'(?:Warning|Note):\s*(.+)'
        warnings = re.findall(warning_pattern, content, re.IGNORECASE)
        validation["warnings"] = warnings
        
        return validation 