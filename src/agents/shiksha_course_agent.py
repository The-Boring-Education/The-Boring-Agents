"""Shiksha Course Generation Agent for creating complete tech courses."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import json
import os
from datetime import datetime, timedelta

from ..core.base_agent import BaseAgent


class ShikshaCourseAgent(BaseAgent):
    """Agent for generating complete Shiksha tech courses with all components."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for Shiksha course generation."""
        
        # Course Planning Template
        course_planning_template = PromptTemplate(
            input_variables=["course_name", "description", "difficulty_level", "roadmap"],
            template="""
            You are a highly skilled tech course creator for The Boring Education's Shiksha platform.
            
            Create a comprehensive course plan for: "{course_name}"
            Description: {description}
            Difficulty Level: {difficulty_level}
            Roadmap: {roadmap}
            
            Generate a detailed course structure with:
            1. Course metadata (name, slug, description, difficulty, roadmap)
            2. Meta content (introduction explaining the course)
            3. Chapter breakdown (15-20 chapters covering the complete topic)
            
            For each chapter, provide:
            - Chapter name (clear, descriptive)
            - Learning objectives
            - Estimated time to complete
            - Prerequisites (if any)
            
            Focus on practical, hands-on learning with real-world projects.
            Structure should follow a logical progression from basics to advanced concepts.
            Include foundational chapters first, then core concepts, then advanced topics.
            
            Return the response as a structured JSON with course metadata and chapter plan.
            """
        )
        
        # Chapter Content Template
        chapter_content_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "chapter_number", "total_chapters", "difficulty_level"],
            template="""
            You are creating chapter content for "{chapter_name}" in the "{course_name}" course.
            This is chapter {chapter_number} of {total_chapters} for {difficulty_level} level learners.
            
            Create comprehensive MDX content that includes:
            
            1. **Chapter Introduction** - Why this topic is important and what learners will gain
            
            2. **Why Do You Need This?** - Explain the real-world importance and applications
            
            3. **How Important Is It?** - Industry relevance and career impact
            
            4. **How Long Will It Take?** - Realistic time estimates for learning
            
            5. **Tutorial Section** - Curate 3-5 high-quality YouTube videos:
               - Focus on recent videos (not older than 2 years)
               - Videos with good view counts (10K+ views)
               - Practical, hands-on content
               - Include video titles, URLs, and brief descriptions
               - Add helpful notes about what each video covers
            
            6. **Projects to Build** - 1-2 practical projects related to the chapter
            
            7. **Share It On Social Media** - LinkedIn and Twitter templates for learners to share their progress
            
            8. **Tips and Best Practices** - Practical advice and common pitfalls to avoid
            
            9. **Practice Problems** - 3-5 hands-on exercises or challenges
            
            Write in an engaging, conversational tone that makes complex concepts easy to understand.
            Use code examples where appropriate.
            Include motivational elements and real-world context.
            
            Format the content in proper MDX with headers, code blocks, and structured sections.
            """
        )
        
        # YouTube Video Curation Template
        video_curation_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "difficulty_level"],
            template="""
            Curate 3-5 high-quality YouTube videos for "{chapter_name}" in the "{course_name}" course.
            Target audience: {difficulty_level} level learners.
            
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
            """
        )
        
        # Social Media Templates Template
        social_media_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "learning_points"],
            template="""
            Create social media sharing templates for learners who completed "{chapter_name}" in the "{course_name}" course.
            
            Learning points covered: {learning_points}
            
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
        
        # Course Metadata Template
        course_metadata_template = PromptTemplate(
            input_variables=["course_name", "description", "difficulty_level", "roadmap"],
            template="""
            Generate course metadata for "{course_name}" following The Boring Education's Shiksha format.
            
            Description: {description}
            Difficulty Level: {difficulty_level}
            Roadmap: {roadmap}
            
            Create:
            1. Course name (engaging and descriptive)
            2. Slug (URL-friendly version)
            3. Cover image description
            4. Detailed description (2-3 sentences)
            5. Live date (future date)
            6. Difficulty level
            7. Roadmap category
            8. Meta content (introduction text)
            
            Follow the exact JSON structure used in Shiksha courses.
            Make the content engaging and professional.
            """
        )
        
        return {
            "course_planning": course_planning_template,
            "chapter_content": chapter_content_template,
            "video_curation": video_curation_template,
            "social_media": social_media_template,
            "course_metadata": course_metadata_template
        }
    
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
    
    def generate_complete_course(self, course_name: str, description: str, 
                               difficulty_level: str = "Beginner", 
                               roadmap: str = "Backend") -> Dict[str, Any]:
        """Generate a complete Shiksha course with all components.
        
        Args:
            course_name: Name of the course
            description: Course description
            difficulty_level: Beginner, Intermediate, or Advanced
            roadmap: Backend, Frontend, Full Stack, etc.
            
        Returns:
            Complete course JSON following Shiksha schema
        """
        self.logger.info(f"Starting course generation for: {course_name}")
        
        # Step 1: Generate course plan and metadata
        course_plan = self._generate_course_plan(course_name, description, difficulty_level, roadmap)
        
        # Step 2: Generate meta content
        meta_content = self._generate_meta_content(course_name, description, difficulty_level, roadmap)
        
        # Step 3: Generate chapters
        chapters = self._generate_chapters(course_plan, course_name, difficulty_level)
        
        # Step 4: Create final course structure
        course_data = self._create_course_structure(course_name, description, difficulty_level, 
                                                  roadmap, meta_content, chapters)
        
        return course_data
    
    def _generate_course_plan(self, course_name: str, description: str, 
                            difficulty_level: str, roadmap: str) -> Dict[str, Any]:
        """Generate the course plan and structure."""
        result = self.generate_content(
            "course_planning",
            course_name=course_name,
            description=description,
            difficulty_level=difficulty_level,
            roadmap=roadmap
        )
        
        # Parse the generated content to extract course plan
        # This would need to be enhanced to properly parse structured content
        return {
            "metadata": self._extract_metadata(result["generated_content"]),
            "chapters": self._extract_chapter_plan(result["generated_content"])
        }
    
    def _generate_meta_content(self, course_name: str, description: str, 
                             difficulty_level: str, roadmap: str) -> str:
        """Generate the meta content (introduction) for the course."""
        result = self.generate_content(
            "course_metadata",
            course_name=course_name,
            description=description,
            difficulty_level=difficulty_level,
            roadmap=roadmap
        )
        
        return result["generated_content"]
    
    def _generate_chapters(self, course_plan: Dict[str, Any], course_name: str, 
                          difficulty_level: str) -> List[Dict[str, Any]]:
        """Generate all chapters for the course."""
        chapters = []
        total_chapters = len(course_plan.get("chapters", []))
        
        for i, chapter_info in enumerate(course_plan.get("chapters", []), 1):
            self.logger.info(f"Generating chapter {i}/{total_chapters}: {chapter_info.get('name', 'Unknown')}")
            
            chapter_content = self._generate_single_chapter(
                chapter_info.get("name", f"Chapter {i}"),
                course_name,
                i,
                total_chapters,
                difficulty_level
            )
            
            chapters.append({
                "name": chapter_info.get("name", f"Chapter {i}"),
                "content": chapter_content,
                "_id": self._generate_chapter_id(),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            })
        
        return chapters
    
    def _generate_single_chapter(self, chapter_name: str, course_name: str, 
                               chapter_number: int, total_chapters: int, 
                               difficulty_level: str) -> str:
        """Generate content for a single chapter."""
        result = self.generate_content(
            "chapter_content",
            chapter_name=chapter_name,
            course_name=course_name,
            chapter_number=chapter_number,
            total_chapters=total_chapters,
            difficulty_level=difficulty_level
        )
        
        return result["generated_content"]
    
    def _create_course_structure(self, course_name: str, description: str, 
                               difficulty_level: str, roadmap: str, 
                               meta_content: str, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the final course structure following Shiksha schema."""
        
        # Generate slug from course name
        slug = self._generate_slug(course_name)
        
        # Generate cover image URL
        cover_image_url = self._generate_cover_image_url(course_name)
        
        # Set live date (1 month from now)
        live_date = (datetime.now() + timedelta(days=30)).isoformat()
        
        return {
            "status": True,
            "data": {
                "_id": self._generate_course_id(),
                "name": course_name,
                "slug": slug,
                "coverImageURL": cover_image_url,
                "description": description,
                "liveOn": live_date,
                "roadmap": roadmap,
                "difficultyLevel": difficulty_level,
                "chapters": chapters,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "__v": 0,
                "meta": meta_content,
                "isPremium": True,
                "price": 1,
                "features": [],
                "isEnrolled": False
            }
        }
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from generated content."""
        # This is a simplified extraction - in practice, you'd want more robust parsing
        return {
            "name": "Extracted from content",
            "slug": "extracted-slug",
            "description": "Extracted description"
        }
    
    def _extract_chapter_plan(self, content: str) -> List[Dict[str, Any]]:
        """Extract chapter plan from generated content."""
        # This is a simplified extraction - in practice, you'd want more robust parsing
        return [
            {"name": f"Chapter {i}", "description": f"Chapter {i} description"}
            for i in range(1, 16)  # Default 15 chapters
        ]
    
    def _generate_slug(self, course_name: str) -> str:
        """Generate URL-friendly slug from course name."""
        return course_name.lower().replace(" ", "-").replace("&", "and")
    
    def _generate_cover_image_url(self, course_name: str) -> str:
        """Generate cover image URL."""
        slug = self._generate_slug(course_name)
        return f"https://ik.imagekit.io/tbe/webapp/shiksha-{slug}-cover.svg"
    
    def _generate_course_id(self) -> str:
        """Generate a unique course ID."""
        import uuid
        return str(uuid.uuid4()).replace("-", "")[:24]
    
    def _generate_chapter_id(self) -> str:
        """Generate a unique chapter ID."""
        import uuid
        return str(uuid.uuid4()).replace("-", "")[:24]
    
    def save_course(self, course_data: Dict[str, Any], filename: str = None) -> str:
        """Save the generated course to a JSON file.
        
        Args:
            course_data: The complete course data
            filename: Optional filename (without extension)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            course_name = course_data.get("data", {}).get("name", "course")
            filename = f"shiksha_course_{self._generate_slug(course_name)}"
        
        filepath = os.path.join(self.config.output_dir, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Course saved to {filepath}")
        return filepath 