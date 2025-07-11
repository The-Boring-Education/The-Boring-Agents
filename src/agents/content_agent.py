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
        
        chapter_content_template = PromptTemplate(
            input_variables=["chapter_title", "course_topic", "level"],
            template="""
            Create comprehensive MDX content for a chapter titled "{chapter_title}" in a {level} level course on {course_topic}.
            
            The content should be structured exactly like this format (include all sections):
            
            # {chapter_title}
            
            ### Why Do You Need [This Topic]?
            [2-3 sentences explaining the importance and relevance]
            
            ### How Important Is It?
            [1-2 sentences about industry relevance and career impact]
            
            ### How Long Will It Take to Learn?
            [Specific timeframe with recommended daily practice]
            
            ## Tutorial
            
            💡
            [Important note or tip about learning this topic]
            
            [[Hindi] [Descriptive Video Title]](https://www.youtube.com/watch?v=SAMPLE_ID)
            
            [https://youtu.be/SAMPLE_ID?si=SAMPLE_TRACKING](https://youtu.be/SAMPLE_ID?si=SAMPLE_TRACKING)
            
            [Brief description of what this video teaches]
            
            [Additional YouTube video links with descriptions - 2-3 videos total]
            
            💡
            [Another important learning tip or practical advice]
            
            ### Projects to Build
            
            1. [Specific project description with actionable steps]
            2. [Optional second project]
            
            ## Share It On Social Media
            
            Now is your Time to start with Learn in Public Journey. It's important to show others what you're doing currently. It'll help you build a Network and eventually get you an internship or job.
            
            The content is given below You can copy and modify as you want and share. Don't forget to add Your Laptop Screen and also Tag The Boring Education.
            
            ### LinkedIn
            
            ```
            [Professional LinkedIn post template with specific achievements, hashtags including #Shiksha #TheBoringEducation]
            ```
            
            ### Twitter
            
            ```
            [Concise Twitter post template with achievements and hashtags including #Shiksha #TheBoringEducation]
            ```
            
            Make the content practical, engaging, and focused on real-world applications. Use conversational tone and include specific examples.
            """
        )
        
        complete_course_template = PromptTemplate(
            input_variables=["course_name", "level", "description", "roadmap"],
            template="""
            Generate a comprehensive course curriculum for "{course_name}" - a {level} level course.
            
            Course Description: {description}
            Roadmap: {roadmap}
            
            Provide a JSON response with this exact structure:
            {{
              "name": "{course_name}",
              "description": "{description}",
              "roadmap": "{roadmap}", 
              "difficultyLevel": "{level}",
              "chapters": [
                {{
                  "name": "Chapter Title",
                  "content": "Brief description of what this chapter will contain"
                }}
              ]
            }}
            
            Include 8-12 chapters that cover the complete learning journey from basics to advanced topics.
            Each chapter should represent 1-2 hours of learning content.
            Focus on practical, project-based learning with real-world applications.
            """
        )
        
        return {
            "course_outline": course_outline_template,
            "video_suggestions": video_suggestions_template,
            "text_content": text_content_template,
            "tricks_and_tips": tricks_and_tips_template,
            "chapter_content": chapter_content_template,
            "complete_course": complete_course_template
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
    
    def generate_chapter_content(self, chapter_title: str, course_topic: str, 
                               level: str = "intermediate") -> Dict[str, Any]:
        """Generate complete MDX content for a single chapter.
        
        Args:
            chapter_title: Title of the chapter
            course_topic: The overall course topic
            level: Difficulty level
            
        Returns:
            Complete MDX chapter content
        """
        return self.generate_content(
            "chapter_content",
            chapter_title=chapter_title,
            course_topic=course_topic,
            level=level
        )
    
    def create_complete_course(self, course_name: str, description: str, 
                             roadmap: str, level: str = "intermediate",
                             chapters: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a complete course in the JSON schema format.
        
        Args:
            course_name: Name of the course
            description: Course description
            roadmap: Course roadmap/category
            level: Difficulty level
            chapters: Optional list of chapter titles. If not provided, will be generated
            
        Returns:
            Complete course in JSON schema format
        """
        import uuid
        from datetime import datetime, timezone
        import re
        
        # Generate chapter list if not provided
        if chapters is None:
            curriculum_response = self.generate_content(
                "complete_course",
                course_name=course_name,
                level=level,
                description=description,
                roadmap=roadmap
            )
            
            # Try to extract JSON from the response
            try:
                import json
                # Find JSON in the response
                content = curriculum_response['generated_content']
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_content = content[json_start:json_end]
                    curriculum_data = json.loads(json_content)
                    chapters = [chapter['name'] for chapter in curriculum_data.get('chapters', [])]
                else:
                    # Fallback to default chapters if JSON parsing fails
                    chapters = self._get_default_chapters(course_name, roadmap)
            except (json.JSONDecodeError, KeyError):
                # Fallback to default chapters
                chapters = self._get_default_chapters(course_name, roadmap)
        
        # Generate slug from course name
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', course_name.lower())
        slug = re.sub(r'\s+', '-', slug).strip('-')
        
        # Generate cover image URL (placeholder)
        cover_image_url = f"https://ik.imagekit.io/tbe/webapp/shiksha-{slug}-cover.svg"
        
        # Create course structure
        course_data = {
            "status": True,
            "data": {
                "_id": str(uuid.uuid4()).replace('-', '')[:24],
                "name": course_name,
                "slug": slug,
                "coverImageURL": cover_image_url,
                "description": description,
                "liveOn": datetime.now(timezone.utc).isoformat(),
                "roadmap": roadmap,
                "difficultyLevel": level.title(),
                "chapters": []
            }
        }
        
        # Generate content for each chapter
        for chapter_title in chapters:
            chapter_content_response = self.generate_chapter_content(
                chapter_title, course_name, level
            )
            
            chapter_data = {
                "name": chapter_title,
                "content": chapter_content_response['generated_content'],
                "_id": str(uuid.uuid4()).replace('-', '')[:24],
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "updatedAt": datetime.now(timezone.utc).isoformat()
            }
            
            course_data["data"]["chapters"].append(chapter_data)
        
        # Add metadata about the generation
        course_data["metadata"] = {
            "generated_by": "The Boring Agents",
            "model": self.model_name,
            "generation_timestamp": datetime.now(timezone.utc).isoformat(),
            "total_chapters": len(chapters)
        }
        
        return course_data
    
    def _get_default_chapters(self, course_name: str, roadmap: str) -> List[str]:
        """Get default chapter titles based on course name and roadmap.
        
        Args:
            course_name: Name of the course
            roadmap: Course roadmap/category
            
        Returns:
            List of default chapter titles
        """
        # Default chapters based on roadmap
        if "backend" in roadmap.lower() or "backend" in course_name.lower():
            return [
                "GitHub - Version Control and Collaboration",
                "Before You Start This Course", 
                "Node.js Fundamentals",
                "Project 1: Build Your First Server with HTTP",
                "Express.js Basics",
                "Project 2: Build Your First API with Express.js",
                "Basics of Databases",
                "Project 3: Build API with Express & SQL",
                "Project 4: Build API with Express.js & MongoDB",
                "REST API Design",
                "Middleware in Express.js",
                "Authentication Basics"
            ]
        elif "frontend" in roadmap.lower() or "frontend" in course_name.lower():
            return [
                "HTML Fundamentals",
                "CSS Styling and Layout",
                "JavaScript Basics",
                "DOM Manipulation",
                "React.js Introduction",
                "State Management",
                "API Integration",
                "Project: Build a Complete App"
            ]
        else:
            # Generic tech course chapters
            return [
                "Getting Started",
                "Fundamentals",
                "Core Concepts",
                "Practical Implementation",
                "Advanced Topics",
                "Best Practices",
                "Real-world Projects",
                "Final Project"
            ]
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()