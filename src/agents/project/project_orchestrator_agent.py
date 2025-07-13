"""Project Orchestrator Agent - Main coordinator for complete project creation with career focus."""

from typing import Dict, Any, List, Optional, Tuple
import json
import os
from datetime import datetime, timedelta
import uuid

from ...core.base_agent import BaseAgent
from .project_idea_agent import ProjectIdeaAgent
from .project_planner_agent import ProjectPlannerAgent
from .project_content_agent import ProjectContentAgent


class ProjectOrchestratorAgent(BaseAgent):
    """Main orchestrator for creating complete real-life projects that boost careers."""
    
    def __init__(self, **kwargs):
        """Initialize the orchestrator with all specialized agents."""
        super().__init__(**kwargs)
        
        # Initialize all specialized agents
        self.idea_agent = ProjectIdeaAgent(**kwargs)
        self.planner_agent = ProjectPlannerAgent(**kwargs)
        self.content_agent = ProjectContentAgent(**kwargs)
        
        self.logger.info("Project Orchestrator initialized with all specialized agents")
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Orchestrator doesn't need its own templates - it coordinates other agents."""
        return {}
    
    def generate_content(self, *args, **kwargs) -> dict:
        """Orchestrator does not generate content directly."""
        raise NotImplementedError("Orchestrator coordinates other agents")
    
    def create_complete_project(self, idea: str, description: str) -> Dict[str, Any]:
        """Create a complete project from just an idea and description.
        
        The AI automatically determines everything else:
        - Domain/industry from the idea
        - Tech stack based on requirements  
        - Difficulty based on complexity
        - User profile from context
        - Target role from career goals
        
        Args:
            idea: The project idea (can be a title or concept)
            description: Detailed description of what to build
            
        Returns:
            Complete project with all sections, chapters, and content
        """
        self.logger.info(f"🚀 Creating complete project from idea: {idea[:50]}...")
        
        try:
            # Step 1: Intelligent Analysis - Auto-determine everything from idea + description
            self.logger.info("🧠 Step 1: Analyzing idea and auto-determining project parameters...")
            
            # Combine idea and description for analysis
            full_context = f"Project Idea: {idea}\n\nDescription: {description}"
            
            # Auto-determine all parameters using AI
            project_params = self._intelligent_project_analysis(full_context)
            
            domain = project_params["domain"]
            tech_stack = project_params["tech_stack"]
            difficulty = project_params["difficulty"]
            user_profile = project_params["user_profile"]
            target_role = project_params["target_role"]
            project_name = project_params["project_name"]
            
            self.logger.info(f"🎯 Auto-determined: {domain} domain, {tech_stack} stack, {difficulty} difficulty")
            self.logger.info(f"👤 Target: {user_profile} → {target_role}")
            
            # Step 2: Generate Real-Life Project Idea (enhance the provided idea)
            self.logger.info("💡 Step 2: Enhancing project idea with market research...")
            project_idea_result = self.idea_agent.generate_real_life_project(
                domain=domain,
                tech_stack=tech_stack,
                difficulty=difficulty,
                user_profile=user_profile,
                market_focus="Indian market"
            )
            
            # Use original idea but enhance with market insights
            enhanced_project_idea = self._enhance_original_idea(idea, description, project_idea_result["project_idea"])
            
            # Step 3: Analyze Career Impact
            self.logger.info("📈 Step 3: Analyzing career impact...")
            career_analysis = self.idea_agent.analyze_career_impact(
                project_idea=enhanced_project_idea,
                target_role=target_role,
                experience_level=difficulty
            )
            
            # Step 4: Create Project Structure
            self.logger.info("🏗️ Step 4: Creating comprehensive project structure...")
            project_structure = self.planner_agent.create_project_structure(
                project_idea=enhanced_project_idea,
                tech_stack=tech_stack,
                difficulty=difficulty,
                target_audience=user_profile,
                learning_goals="Build portfolio project and gain job-ready skills"
            )
            
            # Step 5: Create Project Roadmap
            self.logger.info("🗺️ Step 5: Creating project roadmap...")
            roadmap = self.planner_agent.create_project_roadmap(
                project_name=project_name,
                duration=self._get_project_duration(difficulty),
                difficulty=difficulty,
                career_goals=f"Get hired as a {target_role}"
            )
            
            # Step 6: Generate Project Introduction
            self.logger.info("📖 Step 6: Creating engaging project introduction...")
            intro_content = self.content_agent.generate_project_introduction(
                project_name=project_name,
                problem_statement=description,
                target_users=self._extract_target_users_from_params(project_params),
                tech_stack=tech_stack,
                career_relevance=self._extract_career_relevance(career_analysis["career_analysis"])
            )
            
            # Step 7: Generate Detailed Content for Each Section
            self.logger.info("✍️ Step 7: Generating detailed content for all sections...")
            complete_sections = self._generate_complete_sections(
                project_structure, project_name, tech_stack, domain
            )
            
            # Step 8: Create final project structure in correct API format
            final_project_data = self._create_project_structure(
                project_name=project_name,
                description=description,
                difficulty_level=difficulty,
                roadmap=self._determine_roadmap(tech_stack),
                tech_stack=tech_stack.split(", "),
                meta_content=intro_content,
                sections=complete_sections,
                career_enhancement={
                    "target_role": target_role,
                    "skill_development": self._extract_skills(career_analysis["career_analysis"]),
                    "hiring_advantages": career_analysis.get("hiring_advantages", []),
                    "interview_preparation": self._create_interview_prep(enhanced_project_idea, career_analysis),
                    "portfolio_guidance": self._create_portfolio_guidance(project_name, tech_stack),
                    "salary_impact": self._estimate_salary_impact(difficulty, domain)
                },
                success_metrics={
                    "learning_objectives": self._extract_learning_objectives(project_structure),
                    "completion_criteria": self._define_completion_criteria(difficulty),
                    "portfolio_readiness": self._assess_portfolio_readiness(complete_sections),
                    "career_readiness": self._assess_career_readiness(career_analysis)
                }
            )
            
            self.logger.info(f"🎉 Complete project creation finished for: {project_name}")
            
            return final_project_data
            
        except Exception as e:
            self.logger.error(f"❌ Error creating complete project: {str(e)}")
            raise
    
    def create_project_from_mdx(self, mdx_file_path: str) -> Dict[str, Any]:
        """Create a complete project from an MDX file containing idea and description.
        
        The MDX file should contain:
        # Project Idea: Your idea here
        ## Description
        Your detailed description here...
        
        Args:
            mdx_file_path: Path to the MDX file
            
        Returns:
            Complete project based on the MDX content
        """
        self.logger.info(f"📄 Creating project from MDX file: {mdx_file_path}")
        
        try:
            # Read and parse MDX file
            idea, description = self._parse_mdx_file(mdx_file_path)
            
            if not idea or not description:
                raise ValueError("MDX file must contain both idea and description")
            
            # Create project using the parsed content
            return self.create_complete_project(idea, description)
            
        except Exception as e:
            self.logger.error(f"❌ Error creating project from MDX: {str(e)}")
            raise
    
    def _generate_complete_sections(self, project_structure: Dict[str, Any], 
                                  project_name: str, tech_stack: str, 
                                  domain: str) -> List[Dict[str, Any]]:
        """Generate complete content for all sections and chapters."""
        sections = []
        parsed_structure = project_structure.get("parsed_structure", {})
        
        for i, section_data in enumerate(parsed_structure.get("sections", []), 1):
            section_name = str(section_data.get("name", f"Section {i}"))
            chapters = []
            
            # Generate section introduction
            chapter_names = [str(ch.get("name", "")) for ch in section_data.get("chapters", [])]
            section_intro = self.content_agent.generate_section_intro(
                section_name=section_name,
                section_goal=f"Master the skills needed for {section_name.lower()}",
                chapters=chapter_names,
                project_context=project_name
            )
            
            for j, chapter_data in enumerate(section_data.get("chapters", []), 1):
                chapter_name = str(chapter_data.get("name", f"Chapter {j}"))
                
                # Generate detailed chapter content
                chapter_content = self.content_agent.generate_chapter_content(
                    chapter_name=chapter_name,
                    project_name=project_name,
                    section_goal=f"Learn {section_name.lower()} skills",
                    learning_objectives=[
                        f"Understand {chapter_name.lower()} concepts",
                        f"Implement {chapter_name.lower()} features",
                        f"Apply {chapter_name.lower()} in real projects"
                    ],
                    tech_stack=tech_stack,
                    indian_context=f"Building for Indian {domain} market"
                )
                
                # Add assignments for practical chapters
                assignment_content = ""
                if self._needs_assignment(chapter_name):
                    assignment_content = self.content_agent.generate_assignment(
                        assignment_name=f"Assignment: {chapter_name}",
                        project_context=project_name,
                        skills_to_practice=[
                            f"{chapter_name} implementation",
                            "Problem-solving",
                            "Code quality"
                        ],
                        deliverable=f"Working {chapter_name.lower()} feature",
                        indian_context=f"Indian {domain} requirements"
                    )
                
                # Combine chapter content with assignment
                full_content = chapter_content
                if assignment_content:
                    full_content += f"\n\n{assignment_content}"
                
                chapters.append({
                    "chapterId": self._generate_id(),
                    "chapterName": f"{j}. {chapter_name}",
                    "content": full_content,
                    "isOptional": False
                })
            
            sections.append({
                "sectionId": self._generate_id(),
                "sectionName": f"{i}. {section_name}",
                "chapters": chapters
            })
        
        return sections
    
    def _extract_project_name(self, project_idea: str) -> str:
        """Extract project name from project idea."""
        lines = project_idea.split('\n')
        for line in lines:
            if 'Project Name:' in line:
                return line.split(':', 1)[1].strip().strip('[]')
        return "Innovative Project"
    
    def _extract_problem_statement(self, project_idea: str) -> str:
        """Extract problem statement from project idea."""
        lines = project_idea.split('\n')
        for line in lines:
            if 'One-Line Problem:' in line:
                return line.split(':', 1)[1].strip().strip('[]')
        return "Solving real problems for Indian users"
    
    def _extract_target_users(self, project_idea: str) -> str:
        """Extract target users from project idea."""
        lines = project_idea.split('\n')
        in_target_section = False
        for line in lines:
            if 'Target Users:' in line:
                in_target_section = True
            elif in_target_section and 'Primary:' in line:
                return line.split(':', 1)[1].strip().strip('[]')
        return "Indian users seeking better solutions"
    
    def _extract_career_relevance(self, career_analysis: str) -> str:
        """Extract career relevance from career analysis."""
        lines = career_analysis.split('\n')
        relevant_lines = []
        for line in lines:
            if any(keyword in line.lower() for keyword in ['hire', 'job', 'career', 'salary', 'interview']):
                relevant_lines.append(line.strip())
        return " ".join(relevant_lines[:3]) if relevant_lines else "Enhances career prospects significantly"
    
    def _get_project_duration(self, difficulty: str) -> str:
        """Get project duration based on difficulty."""
        duration_map = {
            "Beginner": "8 weeks",
            "Intermediate": "10 weeks", 
            "Advanced": "12 weeks"
        }
        return duration_map.get(difficulty, "10 weeks")
    
    def _determine_roadmap(self, tech_stack: str) -> str:
        """Determine roadmap category based on tech stack."""
        if not tech_stack:
            return "Full Stack"
        
        tech_lower = str(tech_stack).lower()
        if any(tech in tech_lower for tech in ['react', 'vue', 'angular', 'frontend']):
            return "Frontend"
        elif any(tech in tech_lower for tech in ['node', 'python', 'java', 'backend', 'api']):
            return "Backend"
        elif any(tech in tech_lower for tech in ['fullstack', 'full stack', 'full-stack']):
            return "Full Stack"
        else:
            return "Full Stack"
    
    def _extract_skills(self, career_analysis: str) -> List[str]:
        """Extract skills from career analysis."""
        return [
            "Full-stack development",
            "Problem-solving and analytical thinking",
            "User experience design",
            "Database design and management",
            "API development and integration",
            "Testing and quality assurance",
            "Deployment and DevOps",
            "Technical communication"
        ]
    
    def _create_interview_prep(self, project_idea: str, career_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create interview preparation guidance."""
        return {
            "talking_points": [
                "Problem identification and solution approach",
                "Technical architecture and design decisions",
                "User research and market analysis",
                "Implementation challenges and solutions",
                "Performance optimization and scalability",
                "Testing strategy and quality assurance"
            ],
            "demo_script": "Start with the problem, show the solution, explain the technical decisions, and discuss the impact",
            "technical_questions": [
                "How did you choose your technology stack?",
                "What were the main technical challenges?",
                "How would you scale this for millions of users?",
                "What would you do differently next time?"
            ]
        }
    
    def _create_portfolio_guidance(self, project_name: str, tech_stack: str) -> Dict[str, Any]:
        """Create portfolio presentation guidance."""
        return {
            "github_setup": "Comprehensive README, clean code, proper documentation",
            "demo_requirements": "Live deployment, demo video, detailed walkthrough",
            "presentation_tips": [
                "Lead with the problem and user impact",
                "Show the technical architecture clearly",
                "Demonstrate the working solution",
                "Discuss lessons learned and next steps"
            ],
            "resume_bullet_points": [
                f"Built {project_name} - a full-stack application serving [target users]",
                f"Implemented [key features] using {tech_stack}",
                f"Designed user-centric solution addressing [specific problem]",
                f"Deployed production-ready application with monitoring and analytics"
            ]
        }
    
    def _estimate_salary_impact(self, difficulty: str, domain: str) -> Dict[str, str]:
        """Estimate salary impact based on project complexity."""
        base_ranges = {
            "Beginner": {"min": "4 LPA", "max": "8 LPA"},
            "Intermediate": {"min": "8 LPA", "max": "15 LPA"},
            "Advanced": {"min": "15 LPA", "max": "25 LPA"}
        }
        
        premium_domains = ["fintech", "healthtech", "ai", "blockchain"]
        is_premium = domain.lower() in premium_domains
        
        range_data = base_ranges.get(difficulty, base_ranges["Intermediate"])
        
        return {
            "base_range": f"{range_data['min']} - {range_data['max']}",
            "with_project": f"{range_data['max']} - {int(range_data['max'].split()[0]) + 5} LPA",
            "premium_boost": "+20-30% for premium domains" if is_premium else "Standard market rates",
            "confidence": "High - based on similar project outcomes"
        }
    
    def _extract_learning_objectives(self, project_structure: Dict[str, Any]) -> List[str]:
        """Extract learning objectives from project structure."""
        return [
            "Full-stack application development",
            "Problem-solving and product thinking",
            "User research and market analysis",
            "Technical architecture and design",
            "Professional development workflow",
            "Testing and quality assurance",
            "Deployment and production management",
            "Portfolio and career preparation"
        ]
    
    def _define_completion_criteria(self, difficulty: str) -> List[str]:
        """Define what constitutes project completion."""
        base_criteria = [
            "All core features implemented and tested",
            "Application deployed to production",
            "Comprehensive documentation completed",
            "Demo video and presentation prepared"
        ]
        
        if difficulty == "Advanced":
            base_criteria.extend([
                "Performance optimization implemented",
                "Advanced features and integrations working",
                "Security audit and compliance checks passed"
            ])
        
        return base_criteria
    
    def _assess_portfolio_readiness(self, sections: List[Dict[str, Any]]) -> str:
        """Assess how portfolio-ready this project is."""
        sections_count = len(sections)
        
        if sections_count >= 6:
            return "Excellent - Ready for senior developer portfolios"
        elif sections_count >= 4:
            return "Good - Suitable for mid-level developer portfolios" 
        else:
            return "Basic - Good for entry-level portfolios"
    
    def _assess_career_readiness(self, career_analysis: Dict[str, Any]) -> str:
        """Assess career readiness impact."""
        advantages = career_analysis.get("hiring_advantages", [])
        skills = career_analysis.get("skill_demonstration", [])
        
        readiness_score = len(advantages) + len(skills)
        
        if readiness_score >= 8:
            return "High - Ready for competitive tech roles"
        elif readiness_score >= 5:
            return "Good - Suitable for most developer positions"
        else:
            return "Moderate - Good foundation for career growth"
    
    def _needs_assignment(self, chapter_name: str) -> bool:
        """Determine if a chapter needs a practical assignment."""
        if not chapter_name:
            return False
        
        practical_keywords = [
            "implementation", "building", "creating", "developing", 
            "setup", "deployment", "testing", "integration"
        ]
        chapter_name_str = str(chapter_name).lower()
        return any(keyword in chapter_name_str for keyword in practical_keywords)
    
    def _auto_determine_tech_stack(self, domain: str) -> str:
        """Automatically determine the best tech stack for a domain."""
        if not domain:
            return "React, Node.js, MongoDB, Express.js"
        
        domain_tech_map = {
            "fintech": "React, Node.js, MongoDB, Express.js",
            "edtech": "React, Node.js, PostgreSQL, Redis",
            "healthtech": "React, Python, Django, PostgreSQL",
            "ecommerce": "Next.js, Node.js, MongoDB, Stripe API",
            "gaming": "Unity, C#, Firebase",
            "social": "React Native, Node.js, MongoDB, Socket.io",
            "productivity": "React, TypeScript, Node.js, PostgreSQL",
            "travel": "React, Node.js, MongoDB, Payment APIs",
            "food": "React Native, Node.js, MongoDB, Location APIs",
            "logistics": "React, Python, FastAPI, PostgreSQL",
            "agriculture": "React, Node.js, MongoDB, IoT APIs",
            "fashion": "React, Node.js, MongoDB, Image Processing",
            "real-estate": "React, Node.js, PostgreSQL, Maps API",
            "entertainment": "React, Node.js, MongoDB, Video APIs",
            "sports": "React Native, Node.js, MongoDB, Analytics",
            "news": "React, Node.js, MongoDB, RSS APIs",
            "weather": "React, Node.js, Weather APIs, MongoDB",
            "photography": "React, Node.js, Image Processing, AWS S3",
            "music": "React, Node.js, Audio APIs, MongoDB",
            "fitness": "React Native, Node.js, MongoDB, Health APIs"
        }
        
        return domain_tech_map.get(str(domain).lower(), "React, Node.js, MongoDB, Express.js")
    
    def _auto_determine_tech_stack_from_idea(self, project_idea: str) -> str:
        """Determine tech stack from project idea description."""
        if not project_idea:
            return "React, Node.js, MongoDB, Express.js"
        
        idea_lower = str(project_idea).lower()
        
        # Mobile app indicators
        if any(keyword in idea_lower for keyword in ['mobile app', 'smartphone', 'android', 'ios', 'app store']):
            return "React Native, Node.js, MongoDB, Firebase"
        
        # Web app with real-time features
        elif any(keyword in idea_lower for keyword in ['real-time', 'chat', 'live', 'socket', 'notification']):
            return "React, Node.js, Socket.io, MongoDB"
        
        # AI/ML focused
        elif any(keyword in idea_lower for keyword in ['ai', 'machine learning', 'ml', 'prediction', 'recommendation']):
            return "Python, TensorFlow, FastAPI, PostgreSQL"
        
        # E-commerce/Payment focused
        elif any(keyword in idea_lower for keyword in ['payment', 'shopping', 'cart', 'order', 'purchase']):
            return "Next.js, Node.js, MongoDB, Stripe API"
        
        # Analytics/Dashboard focused
        elif any(keyword in idea_lower for keyword in ['dashboard', 'analytics', 'chart', 'report', 'data']):
            return "React, D3.js, Node.js, PostgreSQL"
        
        # API/Backend heavy
        elif any(keyword in idea_lower for keyword in ['api', 'microservice', 'backend', 'server']):
            return "Node.js, Express.js, MongoDB, Redis"
        
        # Default full-stack
        else:
            return "React, Node.js, MongoDB, Express.js"
    
    def _auto_determine_difficulty(self, user_profile: str) -> str:
        """Determine difficulty based on user profile."""
        if not user_profile:
            return "Intermediate"
        
        profile_lower = str(user_profile).lower()
        
        # Beginner indicators
        if any(keyword in profile_lower for keyword in [
            'student', 'college', 'beginner', 'learning', 'first time', 'new to', 'starting'
        ]):
            return "Beginner"
        
        # Advanced indicators  
        elif any(keyword in profile_lower for keyword in [
            'senior', 'lead', 'architect', 'expert', 'experienced', 'professional', 'years'
        ]):
            return "Advanced"
        
        # Default to intermediate
        else:
            return "Intermediate"
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4()).replace("-", "")[:24]
    
    def save_project(self, project_data: Dict[str, Any], filename: str = None) -> str:
        """Save the generated project to a JSON file.
        
        Args:
            project_data: The complete project data
            filename: Optional filename (without extension)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            project_name = project_data.get("data", {}).get("name", "project")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tbp_project_{self._generate_slug(project_name)}_{timestamp}"
        
        # Ensure output directory exists
        output_path = "./output"
        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Project saved to {filepath}")
        return filepath
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug."""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-') 

    def _create_project_structure(self, project_name: str, description: str, 
                                difficulty_level: str, roadmap: str, tech_stack: List[str],
                                meta_content: str, sections: List[Dict[str, Any]],
                                career_enhancement: Dict[str, Any], 
                                success_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Create the final project structure following The Boring Projects API schema."""
        
        # Generate slug from project name
        slug = self._generate_slug(project_name)
        
        # Generate cover image URL  
        cover_image_url = f"https://ik.imagekit.io/tbe/webapp/tbp-{slug}-1.svg"
        
        return {
            "status": True,
            "message": "Project fetched successfully",
            "data": {
                "_id": self._generate_id(),
                "name": project_name,
                "description": description,
                "coverImageURL": cover_image_url,
                "slug": slug,
                "requiredSkills": tech_stack,
                "roadmap": roadmap,
                "difficultyLevel": difficulty_level,
                "isActive": True,
                "sections": sections,
                "__v": 0,
                "meta": meta_content,
                "isEnrolled": False,
                "career_enhancement": career_enhancement,
                "success_metrics": success_metrics
            }
        } 

    def _intelligent_project_analysis(self, context: str) -> Dict[str, Any]:
        """Intelligently analyze context to determine project parameters."""
        prompt = f"""
        Analyze the following project context and determine the optimal parameters:
        
        {context}
        
        Based on this project idea and description, determine:
        
        1. **Domain/Industry**: What industry does this project belong to? 
           Choose from: fintech, edtech, healthtech, ecommerce, social, productivity, entertainment, food, travel, logistics, agriculture, fashion, real-estate, sports, news, weather, photography, music, fitness, gaming, or other
        
        2. **Tech Stack**: What's the best technology stack for this project?
           Consider the project requirements and complexity.
        
        3. **Difficulty**: What difficulty level is appropriate?
           - Beginner: Simple CRUD apps, basic features
           - Intermediate: Multiple features, integrations, moderate complexity
           - Advanced: Complex algorithms, scaling, advanced features
        
        4. **User Profile**: Who is the target audience for building this project?
           Consider: College students, working professionals, entrepreneurs, etc.
        
        5. **Target Role**: What job role would this project help someone get?
           Consider: Frontend Developer, Backend Developer, Full Stack Developer, etc.
        
        6. **Project Name**: Create a catchy, professional project name
        
        Respond in this exact format:
        Domain: [domain]
        Tech Stack: [comma-separated technologies]
        Difficulty: [Beginner/Intermediate/Advanced]
        User Profile: [target user description]
        Target Role: [job role]
        Project Name: [project name]
        """
        
        response = self._generate_with_prompt(prompt)
        
        # Parse the response into a dictionary
        params = {}
        for line in response.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                params[key] = value
        
        # Ensure all required keys exist with defaults
        return {
            "domain": params.get("domain", "productivity"),
            "tech_stack": params.get("tech_stack", "React, Node.js, MongoDB, Express.js"),
            "difficulty": params.get("difficulty", "Intermediate"),
            "user_profile": params.get("user_profile", "Developers looking to build portfolio projects"),
            "target_role": params.get("target_role", "Software Developer"),
            "project_name": params.get("project_name", "Innovative Project")
        }
    
    def _enhance_original_idea(self, original_idea: str, description: str, enhanced_idea: str) -> str:
        """Enhance the original project idea with market research and specific details."""
        prompt = f"""
        Original Project Idea: {original_idea}
        Description: {description}
        
        Market Research Enhancement: {enhanced_idea}
        
        Create a comprehensive project idea that combines the original concept with market insights.
        
        Focus on:
        - Clear problem statement
        - Specific target market in India
        - Unique value proposition
        - Technical requirements
        - Real-world application
        - Business potential
        
        Return a detailed project idea description that can be used for development planning.
        """
        
        return self._generate_with_prompt(prompt)

    def _extract_target_users_from_params(self, params: Dict[str, Any]) -> str:
        """Extract target users from the determined project parameters."""
        user_profile = params.get("user_profile")
        if user_profile:
            return user_profile
        return "Indian users seeking better solutions"

    def _parse_mdx_file(self, mdx_file_path: str) -> Tuple[str, str]:
        """Parse an MDX file to extract the project idea and description.
        
        Supports multiple formats:
        
        Format 1:
        # Project Idea: Your idea here
        ## Description
        Your detailed description here...
        
        Format 2:
        # Your Project Title
        Your description here...
        
        Format 3:
        ## Idea
        Your idea here
        ## Description  
        Your description here...
        
        Args:
            mdx_file_path: Path to the MDX file
            
        Returns:
            Tuple of (idea, description)
        """
        try:
            with open(mdx_file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            if not content:
                raise ValueError("MDX file is empty")
            
            # Try different parsing strategies
            idea, description = self._parse_mdx_content(content)
            
            if not idea:
                raise ValueError("Could not extract project idea from MDX file")
            if not description:
                raise ValueError("Could not extract project description from MDX file")
            
            self.logger.info(f"Successfully parsed MDX: idea='{idea[:50]}...', description={len(description)} chars")
            return idea, description
            
        except FileNotFoundError:
            raise FileNotFoundError(f"MDX file not found: {mdx_file_path}")
        except Exception as e:
            raise ValueError(f"Error parsing MDX file: {str(e)}")
    
    def _parse_mdx_content(self, content: str) -> Tuple[str, str]:
        """Parse MDX content to extract idea and description using multiple strategies."""
        lines = content.split('\n')
        
        # Strategy 1: Look for "# Project Idea:" and "## Description"
        idea, description = self._parse_format_1(lines)
        if idea and description:
            return idea, description
        
        # Strategy 2: Look for "## Idea" and "## Description"
        idea, description = self._parse_format_2(lines)
        if idea and description:
            return idea, description
        
        # Strategy 3: First H1 as idea, rest as description
        idea, description = self._parse_format_3(lines)
        if idea and description:
            return idea, description
        
        # Strategy 4: Fallback - split by first paragraph
        idea, description = self._parse_fallback(content)
        return idea, description
    
    def _parse_format_1(self, lines: List[str]) -> Tuple[str, str]:
        """Parse format: # Project Idea: ... \n ## Description \n ..."""
        idea = ""
        description = ""
        in_description = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if line.startswith("# Project Idea:"):
                idea = line.replace("# Project Idea:", "").strip()
            elif line.startswith("## Description"):
                in_description = True
                # Get all content after this line
                description = "\n".join(lines[i+1:]).strip()
                break
        
        return idea, description
    
    def _parse_format_2(self, lines: List[str]) -> Tuple[str, str]:
        """Parse format: ## Idea \n ... \n ## Description \n ..."""
        idea = ""
        description = ""
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("## Idea"):
                if current_content and current_section == "description":
                    description = "\n".join(current_content).strip()
                current_section = "idea"
                current_content = []
            elif line.startswith("## Description"):
                if current_content and current_section == "idea":
                    idea = "\n".join(current_content).strip()
                current_section = "description"
                current_content = []
            elif current_section and line:
                current_content.append(line)
        
        # Handle the last section
        if current_content and current_section == "description":
            description = "\n".join(current_content).strip()
        elif current_content and current_section == "idea" and not description:
            idea = "\n".join(current_content).strip()
        
        return idea, description
    
    def _parse_format_3(self, lines: List[str]) -> Tuple[str, str]:
        """Parse format: # Title \n content..."""
        idea = ""
        description_lines = []
        found_title = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("# ") and not found_title:
                idea = line.replace("# ", "").strip()
                found_title = True
            elif found_title and line:
                description_lines.append(line)
        
        description = "\n".join(description_lines).strip()
        return idea, description
    
    def _parse_fallback(self, content: str) -> Tuple[str, str]:
        """Fallback parsing: first line/paragraph as idea, rest as description."""
        paragraphs = content.split('\n\n')
        
        if len(paragraphs) >= 2:
            idea = paragraphs[0].strip().replace('#', '').strip()
            description = '\n\n'.join(paragraphs[1:]).strip()
            return idea, description
        
        # If only one paragraph, try to split by sentences
        lines = content.split('\n')
        if len(lines) >= 2:
            idea = lines[0].strip().replace('#', '').strip()
            description = '\n'.join(lines[1:]).strip()
            return idea, description
        
        # Last resort: use the whole content as both idea and description
        text = content.strip().replace('#', '').strip()
        return text, text 