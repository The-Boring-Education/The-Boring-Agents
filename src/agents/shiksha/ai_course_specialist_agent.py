"""
Specialized AI Course Agent for creating world-class AI, ML, and Data Analysis courses.
This agent enhances the existing Shiksha system with domain-specific expertise.
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime

from ...core.base_agent import BaseAgent


class AICourseSpecialistAgent(BaseAgent):
    """Specialized agent for creating high-quality AI, ML, and Data Analysis courses."""
    
    def __init__(self, **kwargs):
        """Initialize the AI course specialist agent."""
        super().__init__(**kwargs)
        self.specialty_domains = {
            "AI": "Artificial Intelligence",
            "Machine Learning": "Machine Learning",
            "Data Analysis": "Data Analysis and Science",
            "Deep Learning": "Deep Learning",
            "Computer Vision": "Computer Vision",
            "Natural Language Processing": "Natural Language Processing"
        }
        self.logger.info("AI Course Specialist Agent initialized")
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Get specialized prompt templates for AI/ML/Data courses."""
        return {
            "ai_course_structure": """
                Create a comprehensive course structure for {course_name} in the {domain} field.
                
                Course Requirements:
                - Target Audience: {difficulty_level} learners in India
                - Domain: {domain}
                - Focus: Practical, industry-ready skills with theoretical foundation
                
                Design a course with 6-8 chapters that includes:
                
                1. **Foundation Building**
                   - Mathematical prerequisites (Linear Algebra, Statistics, Calculus)
                   - Programming fundamentals (Python/R ecosystem)
                   - Domain-specific theory and concepts
                
                2. **Hands-on Implementation**
                   - Real-world projects with Indian context
                   - Industry-standard tools and libraries
                   - Code walkthroughs and debugging sessions
                
                3. **Advanced Applications**
                   - Cutting-edge techniques and algorithms
                   - Case studies from Indian companies (Flipkart, Zomato, etc.)
                   - Research paper discussions
                
                4. **Industry Preparation**
                   - Portfolio projects that impress recruiters
                   - Interview preparation for {domain} roles
                   - Freelancing and career guidance
                
                Each chapter should have:
                - Clear learning objectives
                - 3-4 practical mini-projects
                - 5-8 assignments of varying difficulty
                - Curated resources and research papers
                - Industry expert insights
                
                Make it engaging for Indian learners with local examples and cultural context.
            """,
            
            "ai_project_generator": """
                Generate {project_count} innovative mini-projects for a {domain} course chapter on "{chapter_topic}".
                
                Requirements:
                - Difficulty: {difficulty_level}
                - Each project should take 2-4 hours to complete
                - Use real Indian datasets when possible
                - Include both technical and business impact
                
                For each project provide:
                1. **Project Title**: Catchy and descriptive
                2. **Business Context**: Real-world problem it solves
                3. **Dataset Description**: What data they'll work with
                4. **Technical Skills**: What they'll learn/apply
                5. **Expected Outcomes**: What they'll build/discover
                6. **Extension Ideas**: How to make it more advanced
                7. **Indian Context**: Why it matters in India
                
                Examples of good contexts:
                - E-commerce recommendation for Flipkart-style platform
                - Agriculture yield prediction for Indian farmers
                - Traffic pattern analysis for Indian cities
                - Sentiment analysis of Indian regional languages
                - Stock market prediction for NSE/BSE
                
                Make projects progressively more complex and interconnected.
            """,
            
            "ai_assignment_creator": """
                Create {assignment_count} diverse assignments for {domain} chapter: "{chapter_topic}".
                
                Assignment Types Needed:
                1. **Coding Challenges** (40%): Hands-on implementation
                2. **Conceptual Questions** (30%): Deep understanding
                3. **Case Study Analysis** (20%): Real-world application  
                4. **Research Tasks** (10%): Latest trends and papers
                
                Difficulty Distribution:
                - Easy: 30% (build confidence)
                - Medium: 50% (core learning)
                - Hard: 20% (stretch goals)
                
                For each assignment provide:
                - **Title**: Clear and specific
                - **Type**: Coding/Conceptual/Case Study/Research
                - **Difficulty**: Easy/Medium/Hard
                - **Time Estimate**: Realistic completion time
                - **Learning Objectives**: What skills it develops
                - **Instructions**: Step-by-step guidance
                - **Hints**: For when students get stuck
                - **Expected Output**: What success looks like
                - **Rubric**: How it will be evaluated
                
                Include assignments that:
                - Use popular Python libraries (pandas, scikit-learn, TensorFlow, etc.)
                - Reference Indian companies and datasets
                - Prepare students for technical interviews
                - Build portfolio-worthy projects
            """,
            
            "ai_resource_curator": """
                Curate high-quality learning resources for {domain} chapter: "{chapter_topic}".
                
                Resource Categories:
                1. **Video Content**: YouTube tutorials and courses
                2. **Reading Material**: Articles, blogs, and documentation
                3. **Interactive Learning**: Coding platforms and simulations
                4. **Research Papers**: Foundational and cutting-edge papers
                5. **Tools & Libraries**: Essential software and frameworks
                6. **Indian Content**: Local creators and perspectives
                
                For each resource provide:
                - **Title**: Resource name
                - **Type**: Video/Article/Paper/Tool/Course
                - **URL**: Direct link (use placeholder for real links)
                - **Duration/Length**: Time investment required
                - **Difficulty**: Beginner/Intermediate/Advanced
                - **Why Recommended**: What makes it valuable
                - **Indian Relevance**: Connection to Indian context
                
                Prioritize:
                - Free and accessible content
                - Content by Indian creators when available
                - Practical, hands-on resources
                - Resources that complement the course content
                - Latest and up-to-date materials
                
                Include at least 2-3 resources by Indian creators or about Indian use cases.
            """,
            
            "ai_tips_generator": """
                Generate practical tips and tricks for mastering {domain}, specifically for {chapter_topic}.
                
                Create tips in these categories:
                
                1. **Learning Strategies** (5 tips)
                   - How to approach complex concepts
                   - Best practices for skill development
                   - Common pitfalls and how to avoid them
                
                2. **Technical Implementation** (7 tips)
                   - Code optimization and best practices
                   - Debugging techniques
                   - Tool usage and shortcuts
                   - Performance optimization
                
                3. **Career Insights** (3 tips)
                   - What Indian employers look for
                   - Building an impressive portfolio
                   - Interview preparation strategies
                
                4. **Industry Context** (5 tips)
                   - Current trends in Indian market
                   - Success stories and case studies
                   - Networking and community building
                
                Format each tip as:
                **Tip Title**: Brief catchy title
                **Context**: When/why this matters
                **Action**: Specific steps to implement
                **Example**: Real-world illustration
                **Indian Context**: Local relevance
                
                Make tips actionable, specific, and culturally relevant for Indian learners.
            """
        }
    
    def generate_content(self, content_type: str, **kwargs) -> dict:
        """Generate specialized AI/ML/Data Analysis content."""
        try:
            if content_type == "course_structure":
                return self._generate_ai_course_structure(**kwargs)
            elif content_type == "projects":
                return self._generate_ai_projects(**kwargs)
            elif content_type == "assignments":
                return self._generate_ai_assignments(**kwargs)
            elif content_type == "resources":
                return self._curate_ai_resources(**kwargs)
            elif content_type == "tips":
                return self._generate_ai_tips(**kwargs)
            else:
                raise ValueError(f"Unknown content type: {content_type}")
                
        except Exception as e:
            self.logger.error(f"Error generating {content_type}: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_ai_course_structure(self, course_name: str, domain: str, 
                                    difficulty_level: str = "Intermediate") -> dict:
        """Generate course structure for AI/ML/Data courses."""
        try:
            prompt = self.prompt_templates["ai_course_structure"].format(
                course_name=course_name,
                domain=domain,
                difficulty_level=difficulty_level
            )
            
            response = self._generate_with_prompt(prompt)
            
            # Parse and structure the response
            course_structure = self._parse_course_structure(response, domain)
            
            return {
                "status": "success",
                "data": course_structure,
                "generated_at": datetime.now().isoformat(),
                "domain": domain,
                "course_name": course_name
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI course structure: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_ai_projects(self, chapter_topic: str, domain: str, 
                            difficulty_level: str = "Intermediate",
                            project_count: int = 3) -> dict:
        """Generate AI/ML mini-projects for a chapter."""
        try:
            prompt = self.prompt_templates["ai_project_generator"].format(
                chapter_topic=chapter_topic,
                domain=domain,
                difficulty_level=difficulty_level,
                project_count=project_count
            )
            
            response = self._generate_with_prompt(prompt)
            projects = self._parse_projects(response)
            
            return {
                "status": "success",
                "data": {
                    "chapter_topic": chapter_topic,
                    "domain": domain,
                    "projects": projects,
                    "project_count": len(projects)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI projects: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_ai_assignments(self, chapter_topic: str, domain: str,
                               assignment_count: int = 8) -> dict:
        """Generate diverse assignments for AI/ML chapters."""
        try:
            prompt = self.prompt_templates["ai_assignment_creator"].format(
                chapter_topic=chapter_topic,
                domain=domain,
                assignment_count=assignment_count
            )
            
            response = self._generate_with_prompt(prompt)
            assignments = self._parse_assignments(response)
            
            return {
                "status": "success",
                "data": {
                    "chapter_topic": chapter_topic,
                    "domain": domain,
                    "assignments": assignments,
                    "assignment_count": len(assignments)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI assignments: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _curate_ai_resources(self, chapter_topic: str, domain: str) -> dict:
        """Curate specialized resources for AI/ML chapters."""
        try:
            prompt = self.prompt_templates["ai_resource_curator"].format(
                chapter_topic=chapter_topic,
                domain=domain
            )
            
            response = self._generate_with_prompt(prompt)
            resources = self._parse_resources(response)
            
            return {
                "status": "success",
                "data": {
                    "chapter_topic": chapter_topic,
                    "domain": domain,
                    "resources": resources,
                    "resource_count": len(resources)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error curating AI resources: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _generate_ai_tips(self, chapter_topic: str, domain: str) -> dict:
        """Generate practical tips for AI/ML learning."""
        try:
            prompt = self.prompt_templates["ai_tips_generator"].format(
                chapter_topic=chapter_topic,
                domain=domain
            )
            
            response = self._generate_with_prompt(prompt)
            tips = self._parse_tips(response)
            
            return {
                "status": "success",
                "data": {
                    "chapter_topic": chapter_topic,
                    "domain": domain,
                    "tips": tips,
                    "tip_count": len(tips)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating AI tips: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _parse_course_structure(self, response: str, domain: str) -> dict:
        """Parse course structure response into structured format."""
        # This would parse the AI response into structured course data
        # For now, return a structured template
        return {
            "course_type": "AI/ML Specialized",
            "domain": domain,
            "total_chapters": 8,
            "estimated_duration": "12-16 weeks",
            "chapters": [
                {
                    "chapter_number": 1,
                    "title": "Foundation and Setup",
                    "topics": ["Python ecosystem", "Mathematical foundations", "Development environment"],
                    "duration_hours": 15
                },
                # Add more chapters based on parsing
            ],
            "ai_enhanced": True,
            "indian_context": True
        }
    
    def _parse_projects(self, response: str) -> List[dict]:
        """Parse projects from AI response."""
        # Parse the response and structure as project objects
        return [
            {
                "title": "Sample AI Project",
                "description": "Project description",
                "difficulty": "Medium",
                "estimated_hours": 3,
                "skills_covered": ["Python", "Machine Learning"],
                "indian_context": True
            }
        ]
    
    def _parse_assignments(self, response: str) -> List[dict]:
        """Parse assignments from AI response."""
        return [
            {
                "title": "Sample Assignment",
                "type": "Coding Challenge",
                "difficulty": "Medium",
                "estimated_time": "2 hours",
                "skills_tested": ["Implementation", "Problem Solving"]
            }
        ]
    
    def _parse_resources(self, response: str) -> List[dict]:
        """Parse resources from AI response."""
        return [
            {
                "title": "Sample Resource",
                "type": "Video",
                "url": "https://example.com",
                "duration": "45 minutes",
                "difficulty": "Beginner",
                "indian_content": True
            }
        ]
    
    def _parse_tips(self, response: str) -> List[dict]:
        """Parse tips from AI response."""
        return [
            {
                "category": "Learning Strategy",
                "title": "Sample Tip",
                "content": "Tip content",
                "indian_context": "Why this matters in India"
            }
        ]
    
    def enhance_existing_course(self, course_data: dict, specialization: str) -> dict:
        """Enhance an existing course with AI/ML specialization."""
        try:
            if specialization not in self.specialty_domains:
                raise ValueError(f"Unsupported specialization: {specialization}")
            
            enhanced_course = course_data.copy()
            
            # Add AI-specific enhancements
            enhanced_course["ai_enhanced"] = True
            enhanced_course["specialization"] = specialization
            enhanced_course["enhancement_date"] = datetime.now().isoformat()
            
            # Enhance each chapter with specialized content
            if "chapters" in enhanced_course:
                for chapter in enhanced_course["chapters"]:
                    self._enhance_chapter_with_ai_content(chapter, specialization)
            
            return {
                "status": "success",
                "data": enhanced_course,
                "message": f"Course enhanced with {specialization} specialization"
            }
            
        except Exception as e:
            self.logger.error(f"Error enhancing course: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _enhance_chapter_with_ai_content(self, chapter: dict, specialization: str):
        """Add AI-specific content to a chapter."""
        chapter_name = chapter.get("name", "Unknown Chapter")
        
        # Add specialized projects
        projects_result = self._generate_ai_projects(
            chapter_topic=chapter_name,
            domain=specialization,
            project_count=3
        )
        
        if projects_result["status"] == "success":
            chapter["ai_projects"] = projects_result["data"]["projects"]
        
        # Add specialized assignments
        assignments_result = self._generate_ai_assignments(
            chapter_topic=chapter_name,
            domain=specialization,
            assignment_count=6
        )
        
        if assignments_result["status"] == "success":
            chapter["ai_assignments"] = assignments_result["data"]["assignments"]
        
        # Add curated resources
        resources_result = self._curate_ai_resources(
            chapter_topic=chapter_name,
            domain=specialization
        )
        
        if resources_result["status"] == "success":
            chapter["ai_resources"] = resources_result["data"]["resources"]
        
        # Add tips and tricks
        tips_result = self._generate_ai_tips(
            chapter_topic=chapter_name,
            domain=specialization
        )
        
        if tips_result["status"] == "success":
            chapter["ai_tips"] = tips_result["data"]["tips"]
        
        chapter["ai_enhanced"] = True
        chapter["specialization"] = specialization
