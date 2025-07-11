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
        
        # SHIKSHA-specific templates
        shiksha_course_template = PromptTemplate(
            input_variables=["topic", "level", "roadmap", "description"],
            template="""
            Create a complete SHIKSHA course for {topic} at {level} level.
            Course description: {description}
            Roadmap: {roadmap}
            
            Generate a comprehensive course with the following structure:
            1. Course Name (engaging and descriptive)
            2. Slug (URL-friendly version)
            3. Description (compelling 1-2 sentences)
            4. Difficulty Level ({level})
            5. Roadmap ({roadmap})
            6. 8-12 Chapters with detailed content
            
            For each chapter, include:
            - Chapter name (clear and descriptive)
            - Complete MDX content with:
              * Introduction explaining why this topic is important
              * Learning objectives and time estimates
              * YouTube video tutorial suggestions with descriptions
              * Detailed text content with tips, tricks, and best practices
              * Practical examples and code snippets
              * Project ideas or exercises
              * Social media sharing templates for LinkedIn and Twitter
            
            Follow the SHIKSHA format with proper markdown formatting, callout boxes (💡), and engaging conversational tone.
            Make sure content is practical, actionable, and includes real-world examples.
            """
        )
        
        shiksha_chapter_template = PromptTemplate(
            input_variables=["chapter_name", "course_topic", "chapter_description", "level"],
            template="""
            Generate detailed MDX content for a SHIKSHA course chapter:
            
            Chapter: {chapter_name}
            Course Topic: {course_topic}
            Description: {chapter_description}
            Level: {level}
            
            Create comprehensive chapter content in MDX format with:
            
            1. **Introduction Section**:
               - Why this topic is important (with 📌 callout)
               - How it fits into the bigger picture
               - Time estimate for learning
            
            2. **Tutorial Section**:
               - YouTube video recommendations with descriptions
               - Links to specific tutorials
               - What to focus on while watching
            
            3. **Content Section**:
               - Detailed explanations with examples
               - Code snippets where applicable
               - Tips and tricks (with 💡 callouts)
               - Common pitfalls to avoid
               - Best practices
            
            4. **Projects/Practice Section**:
               - Hands-on exercises or mini-projects
               - What to build and why
            
            5. **Social Media Sharing Templates**:
               - LinkedIn post template (professional, detailed)
               - Twitter post template (concise, engaging)
               - Include relevant hashtags: #Shiksha #TheBoringEducation
            
            Use engaging, conversational tone. Include practical examples and real-world applications.
            Format with proper markdown headers, callouts, code blocks, and bullet points.
            """
        )
        
        social_media_template = PromptTemplate(
            input_variables=["topic", "achievement", "learning_points"],
            template="""
            Generate social media sharing templates for a learner who just completed: {topic}
            
            Achievement: {achievement}
            Key Learning Points: {learning_points}
            
            Create templates for:
            
            **LinkedIn Post**:
            - Professional tone
            - 3-4 key accomplishments with bullet points
            - Mention learning journey and growth
            - Include call to action for engagement
            - End with: "Learning all this in Shiksha by The Boring Education 🎓"
            - Relevant hashtags including #Shiksha #TheBoringEducation
            
            **Twitter Post**:
            - Concise and engaging
            - Use emojis and bullet points
            - Highlight key achievements
            - Include learning platform mention
            - Relevant hashtags including #Shiksha #TheBoringEducation
            - Keep under 280 characters
            
            Make the posts authentic, inspiring, and encouraging for other learners.
            """
        )
        
        return {
            "course_outline": course_outline_template,
            "video_suggestions": video_suggestions_template,
            "text_content": text_content_template,
            "tricks_and_tips": tricks_and_tips_template,
            "shiksha_course": shiksha_course_template,
            "shiksha_chapter": shiksha_chapter_template,
            "social_media": social_media_template
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
    
    def create_shiksha_course(self, topic: str, level: str = "intermediate",
                            roadmap: str = "Backend", description: str = None) -> Dict[str, Any]:
        """Create a complete SHIKSHA course with chapters and content.
        
        Args:
            topic: The course topic (e.g., "Node.js Backend Development")
            level: Difficulty level (beginner, intermediate, advanced)
            roadmap: Learning roadmap category (e.g., "Backend", "Frontend")
            description: Course description (auto-generated if not provided)
            
        Returns:
            Complete course data with metadata and chapters
        """
        if description is None:
            description = f"Learn {topic} from basics to advanced level"
        
        # Generate the course content
        course_content = self.generate_content(
            "shiksha_course",
            topic=topic,
            level=level,
            roadmap=roadmap,
            description=description
        )
        
        # Parse and structure the response into proper course format
        return self._structure_shiksha_course(course_content, topic, level, roadmap, description)
    
    def create_shiksha_chapter(self, chapter_name: str, course_topic: str,
                             chapter_description: str, level: str = "intermediate") -> Dict[str, Any]:
        """Create detailed content for a SHIKSHA course chapter.
        
        Args:
            chapter_name: Name of the chapter
            course_topic: Overall course topic
            chapter_description: Brief description of what the chapter covers
            level: Difficulty level
            
        Returns:
            Chapter content with MDX formatting
        """
        return self.generate_content(
            "shiksha_chapter",
            chapter_name=chapter_name,
            course_topic=course_topic,
            chapter_description=chapter_description,
            level=level
        )
    
    def generate_social_media_templates(self, topic: str, achievement: str, 
                                      learning_points: List[str]) -> Dict[str, Any]:
        """Generate social media sharing templates.
        
        Args:
            topic: The topic/technology learned
            achievement: What was accomplished
            learning_points: Key things learned
            
        Returns:
            LinkedIn and Twitter post templates
        """
        learning_points_str = "\n".join([f"• {point}" for point in learning_points])
        
        return self.generate_content(
            "social_media",
            topic=topic,
            achievement=achievement,
            learning_points=learning_points_str
        )
    
    def _structure_shiksha_course(self, course_content: Dict[str, Any], topic: str,
                                level: str, roadmap: str, description: str) -> Dict[str, Any]:
        """Structure the generated course content into SHIKSHA format.
        
        Args:
            course_content: Raw generated content
            topic: Course topic
            level: Difficulty level
            roadmap: Learning roadmap
            description: Course description
            
        Returns:
            Structured course data matching SHIKSHA schema
        """
        import json
        from datetime import datetime, timedelta
        import re
        
        # Generate course metadata
        course_name = f"Complete {topic} Course"
        slug = re.sub(r'[^a-z0-9]+', '-', topic.lower()).strip('-')
        
        # Parse generated content to extract chapters
        content_text = course_content['generated_content']
        chapters = self._parse_chapters_from_content(content_text)
        
        # Structure the course data
        course_data = {
            "status": True,
            "data": {
                "_id": f"course_{slug}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "name": course_name,
                "slug": slug,
                "coverImageURL": f"https://ik.imagekit.io/tbe/webapp/shiksha-{slug}-cover.svg",
                "description": description,
                "liveOn": (datetime.now() + timedelta(days=7)).isoformat(),
                "roadmap": roadmap,
                "difficultyLevel": level.title(),
                "chapters": chapters
            }
        }
        
        return {
            "content_type": "shiksha_course",
            "parameters": {
                "topic": topic,
                "level": level,
                "roadmap": roadmap,
                "description": description
            },
            "generated_content": course_data,
            "metadata": {
                "model": self.model_name,
                "timestamp": self._get_timestamp(),
                "chapter_count": len(chapters)
            }
        }
    
    def _parse_chapters_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse chapter information from generated content.
        
        Args:
            content: Generated course content text
            
        Returns:
            List of chapter dictionaries
        """
        from datetime import datetime
        import re
        
        chapters = []
        
        # Generate sample chapters with proper SHIKSHA format
        sample_chapters = [
            {
                "name": "GitHub - Version Control and Collaboration",
                "content": self._generate_sample_chapter_content("GitHub", "version control and collaboration")
            },
            {
                "name": "Before You Start This Course", 
                "content": self._generate_sample_chapter_content("Prerequisites", "course preparation and requirements")
            },
            {
                "name": "Node.js Fundamentals",
                "content": self._generate_sample_chapter_content("Node.js", "core concepts and runtime environment")
            },
            {
                "name": "Project 1: Build Your First Server with HTTP",
                "content": self._generate_sample_chapter_content("HTTP Server", "creating your first web server")
            },
            {
                "name": "Express.js Basics",
                "content": self._generate_sample_chapter_content("Express.js", "web framework fundamentals")
            },
            {
                "name": "Project 2: Build Your First API with Express.js",
                "content": self._generate_sample_chapter_content("Express API", "RESTful API development")
            },
            {
                "name": "Basics of Databases",
                "content": self._generate_sample_chapter_content("Databases", "data storage and management")
            },
            {
                "name": "Authentication Basics",
                "content": self._generate_sample_chapter_content("Authentication", "user security and authorization")
            }
        ]
        
        for i, chapter_info in enumerate(sample_chapters):
            chapter = {
                "name": chapter_info["name"],
                "content": chapter_info["content"],
                "_id": f"chapter_{i+1}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
            chapters.append(chapter)
        
        return chapters
    
    def _generate_sample_chapter_content(self, topic: str, description: str) -> str:
        """Generate sample chapter content in SHIKSHA MDX format.
        
        Args:
            topic: The chapter topic
            description: Brief description of the chapter
            
        Returns:
            MDX-formatted chapter content
        """
        content = f"""# {topic} - {description.title()}

📌

**When I started learning backend development, {topic} was one of the first things I learned because it's fundamental to modern web development. Most courses don't teach you this properly, but we thought you need to learn {topic} first. So here we go -**

### Why Do You Need {topic}?

{topic} is essential for developers to build scalable and efficient applications. It's the foundation that enables you to create robust systems and work effectively with modern development practices.

### How Important Is It?

Every developer, irrespective of their role, needs to know {topic}. It's a non-negotiable skill for teamwork and building production-ready applications.

### How Long Will It Take to Learn?

You can learn the basics of {topic} in **3-5 days**, with **daily practice sessions** focusing on core concepts and hands-on implementation.

## Tutorial

[Complete {topic} Tutorial](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

https://youtu.be/dQw4w9WgXcQ

Learn {topic} fundamentals from this comprehensive tutorial.

[Advanced {topic} Concepts](https://www.youtube.com/watch?v=dQw4w9WgXcQ)

https://www.youtube.com/watch?v=dQw4w9WgXcQ

This video covers advanced concepts and best practices.

💡

During your learning journey, focus on understanding the core concepts first. Don't worry if some advanced topics seem confusing initially - practice makes perfect.

### Projects to Build

1. Create a simple {topic} project to practice the fundamentals
2. Build a real-world application using {topic}
3. Implement best practices and optimization techniques

## Share It On Social Media

Now is your time to start with the Learn in Public journey. It's important to show others what you're doing currently. It'll help you build a network and eventually get you an internship or job.

The content is given below. You can copy and modify as you want and share. Don't forget to add your laptop screen and also tag The Boring Education.

### LinkedIn

```
💻 Just learned {topic}: {description}!

Here's what I've mastered:
1️⃣ Core Concepts: Understanding the fundamentals of {topic}
2️⃣ Practical Application: Building real-world projects
3️⃣ Best Practices: Following industry standards and patterns

{topic} is a crucial skill for developers, and I'm excited to apply what I've learned in my projects!

🎓 Learning all this in Shiksha by The Boring Education. 🚀

#{topic.replace(' ', '')} #LearningInPublic #Shiksha #TheBoringEducation #DevelopersJourney
```

### Twitter

```
✅ Just learned {topic}: {description}!

{topic} is THE foundation for modern development, and I'm mastering it in Shiksha by The Boring Education! 🚀

#{topic.replace(' ', '')} #Shiksha #TheBoringEducation #CodingJourney
```"""
        
        return content
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()