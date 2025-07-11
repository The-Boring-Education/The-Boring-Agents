"""Content Creator Agent for generating chapter content in MDX format."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import re

from ..core.base_agent import BaseAgent


class ContentCreatorAgent(BaseAgent):
    """Agent for creating detailed chapter content in MDX format."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for content creation."""
        
        chapter_content_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "chapter_number", "total_chapters", 
                           "difficulty_level", "learning_objectives", "key_concepts"],
            template="""
            You are creating comprehensive chapter content for "{chapter_name}" in the "{course_name}" course.
            This is chapter {chapter_number} of {total_chapters} for {difficulty_level} level learners.
            
            Learning Objectives: {learning_objectives}
            Key Concepts: {key_concepts}
            
            Create engaging MDX content that includes:
            
            # {chapter_name}
            
            ### Why Do You Need This?
            Explain the real-world importance and applications of this topic.
            
            ### How Important Is It?
            Industry relevance and career impact.
            
            ### How Long Will It Take?
            Realistic time estimates for learning.
            
            ## Tutorial
            
            Curate 3-5 high-quality YouTube videos:
            - Recent videos (not older than 2 years)
            - Videos with good view counts (10K+ views)
            - Practical, hands-on content
            - Include video titles, URLs, and brief descriptions
            - Add helpful notes about what each video covers
            
            Format each video as:
            **[Video Title](URL)**
            Brief description of what this video covers and why it's valuable.
            
            ## Projects to Build
            1-2 practical projects related to this chapter.
            
            ## Share It On Social Media
            
            ### LinkedIn
            ```
            [Professional LinkedIn post template]
            ```
            
            ### Twitter
            ```
            [Concise Twitter post template]
            ```
            
            ## Tips and Best Practices
            Practical advice and common pitfalls to avoid.
            
            ## Practice Problems
            3-5 hands-on exercises or challenges.
            
            Write in an engaging, conversational tone that makes complex concepts easy to understand.
            Use code examples where appropriate.
            Include motivational elements and real-world context.
            Format properly in MDX with headers, code blocks, and structured sections.
            """
        )
        
        video_curation_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "difficulty_level", "key_concepts"],
            template="""
            Curate 3-5 high-quality YouTube videos for "{chapter_name}" in the "{course_name}" course.
            Target audience: {difficulty_level} level learners.
            Key concepts to cover: {key_concepts}
            
            For each video, provide:
            1. Video Title
            2. Channel Name
            3. URL
            4. Duration
            5. Key concepts covered
            6. Why this video is valuable
            7. Prerequisites (if any)
            
            Selection criteria:
            - Recent videos (not older than 2 years)
            - Good view count (10K+ views preferred)
            - Clear, well-structured content
            - Practical, hands-on approach
            - Good audio/video quality
            - English language content
            
            Focus on videos that complement each other and provide comprehensive coverage.
            Return the videos in a structured format suitable for MDX content.
            """
        )
        
        social_media_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "learning_points", "difficulty_level"],
            template="""
            Create social media sharing templates for learners who completed "{chapter_name}" in the "{course_name}" course.
            
            Learning points covered: {learning_points}
            Difficulty level: {difficulty_level}
            
            Create templates for:
            
            1. **LinkedIn Post** (professional tone):
               - Engaging opening
               - Key learnings (3-5 bullet points)
               - Career impact
               - Call to action
               - Relevant hashtags
            
            2. **Twitter Post** (concise, engaging):
               - Short, punchy content
               - Key achievements
               - Learning journey focus
               - Relevant hashtags
            
            Make the content motivational and shareable.
            Include hashtags like #Shiksha #TheBoringEducation #LearningInPublic
            """
        )
        
        practice_problems_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "difficulty_level", "key_concepts"],
            template="""
            Create 3-5 practice problems for "{chapter_name}" in the "{course_name}" course.
            Target audience: {difficulty_level} level learners.
            Key concepts: {key_concepts}
            
            For each problem, provide:
            1. Problem statement
            2. Learning objectives
            3. Difficulty level (Easy/Medium/Hard)
            4. Expected solution approach
            5. Additional challenges (bonus tasks)
            
            Make problems:
            - Practical and real-world relevant
            - Progressive in difficulty
            - Hands-on and interactive
            - Suitable for the target difficulty level
            """
        )
        
        return {
            "chapter_content": chapter_content_template,
            "video_curation": video_curation_template,
            "social_media": social_media_template,
            "practice_problems": practice_problems_template
        }
    
    def create_chapter_content(self, chapter_name: str, course_name: str, 
                             chapter_number: int, total_chapters: int, 
                             difficulty_level: str, learning_objectives: List[str] = None,
                             key_concepts: List[str] = None) -> str:
        """Create comprehensive chapter content in MDX format.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            chapter_number: Chapter number
            total_chapters: Total number of chapters
            difficulty_level: Difficulty level
            learning_objectives: List of learning objectives
            key_concepts: List of key concepts
            
        Returns:
            MDX formatted chapter content
        """
        # Format learning objectives and key concepts
        objectives_text = "\n".join([f"- {obj}" for obj in (learning_objectives or [])])
        concepts_text = "\n".join([f"- {concept}" for concept in (key_concepts or [])])
        
        result = self.generate_content(
            "chapter_content",
            chapter_name=chapter_name,
            course_name=course_name,
            chapter_number=chapter_number,
            total_chapters=total_chapters,
            difficulty_level=difficulty_level,
            learning_objectives=objectives_text,
            key_concepts=concepts_text
        )
        
        return result["generated_content"]
    
    def curate_videos(self, chapter_name: str, course_name: str, 
                     difficulty_level: str, key_concepts: List[str] = None) -> str:
        """Curate YouTube videos for a chapter.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            difficulty_level: Difficulty level
            key_concepts: Key concepts to cover
            
        Returns:
            Curated video content in MDX format
        """
        concepts_text = "\n".join([f"- {concept}" for concept in (key_concepts or [])])
        
        result = self.generate_content(
            "video_curation",
            chapter_name=chapter_name,
            course_name=course_name,
            difficulty_level=difficulty_level,
            key_concepts=concepts_text
        )
        
        return result["generated_content"]
    
    def create_social_media_templates(self, chapter_name: str, course_name: str,
                                    learning_points: List[str], difficulty_level: str) -> str:
        """Create social media sharing templates.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            learning_points: List of learning points
            difficulty_level: Difficulty level
            
        Returns:
            Social media templates in MDX format
        """
        points_text = "\n".join([f"- {point}" for point in learning_points])
        
        result = self.generate_content(
            "social_media",
            chapter_name=chapter_name,
            course_name=course_name,
            learning_points=points_text,
            difficulty_level=difficulty_level
        )
        
        return result["generated_content"]
    
    def create_practice_problems(self, chapter_name: str, course_name: str,
                               difficulty_level: str, key_concepts: List[str] = None) -> str:
        """Create practice problems for a chapter.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            difficulty_level: Difficulty level
            key_concepts: Key concepts to practice
            
        Returns:
            Practice problems in MDX format
        """
        concepts_text = "\n".join([f"- {concept}" for concept in (key_concepts or [])])
        
        result = self.generate_content(
            "practice_problems",
            chapter_name=chapter_name,
            course_name=course_name,
            difficulty_level=difficulty_level,
            key_concepts=concepts_text
        )
        
        return result["generated_content"]
    
    def enhance_content_with_videos(self, content: str, videos_content: str) -> str:
        """Enhance chapter content with curated videos.
        
        Args:
            content: Original chapter content
            videos_content: Curated video content
            
        Returns:
            Enhanced content with videos integrated
        """
        # Find the Tutorial section and replace it with video content
        tutorial_pattern = r'(## Tutorial\n\n).*?(?=\n##|\n###|\Z)'
        replacement = '## Tutorial\n\n' + videos_content
        
        enhanced_content = re.sub(tutorial_pattern, replacement, content, flags=re.DOTALL)
        return enhanced_content
    
    def enhance_content_with_social_media(self, content: str, social_media_content: str) -> str:
        """Enhance chapter content with social media templates.
        
        Args:
            content: Original chapter content
            social_media_content: Social media templates
            
        Returns:
            Enhanced content with social media templates integrated
        """
        # Find the Share It On Social Media section and replace it
        social_pattern = r'(## Share It On Social Media\n\n).*?(?=\n##|\n###|\Z)'
        replacement = '## Share It On Social Media\n\n' + social_media_content
        
        enhanced_content = re.sub(social_pattern, replacement, content, flags=re.DOTALL)
        return enhanced_content
    
    def enhance_content_with_practice_problems(self, content: str, practice_content: str) -> str:
        """Enhance chapter content with practice problems.
        
        Args:
            content: Original chapter content
            practice_content: Practice problems content
            
        Returns:
            Enhanced content with practice problems integrated
        """
        # Find the Practice Problems section and replace it
        practice_pattern = r'(## Practice Problems\n\n).*?(?=\n##|\n###|\Z)'
        replacement = '## Practice Problems\n\n' + practice_content
        
        enhanced_content = re.sub(practice_pattern, replacement, content, flags=re.DOTALL)
        return enhanced_content
    
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