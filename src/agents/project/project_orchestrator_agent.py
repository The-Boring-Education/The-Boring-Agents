"""Project Orchestrator Agent - Main coordinator for complete project creation with career focus."""

from typing import Dict, Any, List, Optional
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
    
    def create_complete_project(self, domain: str, 
                              user_profile: str = "College student looking for internships",
                              target_role: str = "Software Developer") -> Dict[str, Any]:
        """Create a complete project from idea to deployment with career guidance.
        
        Args:
            domain: Domain/industry for the project (fintech, edtech, healthtech, etc.)
            user_profile: Target user's background and goals
            target_role: Target job role
            
        Returns:
            Complete project with all sections, chapters, and content
        """
        self.logger.info(f"🚀 Starting complete project creation for {domain} domain")
        
        try:
            # Step 1: Automatically determine tech stack and difficulty based on domain
            tech_stack = self._auto_determine_tech_stack(domain)
            difficulty = self._auto_determine_difficulty(user_profile)
            
            self.logger.info(f"🎯 Auto-determined: {tech_stack} stack, {difficulty} difficulty")
            
            # Step 2: Generate Real-Life Project Idea
            self.logger.info("💡 Step 1: Generating real-life project idea...")
            project_idea_result = self.idea_agent.generate_real_life_project(
                domain=domain,
                tech_stack=tech_stack,
                difficulty=difficulty,
                user_profile=user_profile,
                market_focus="Indian market"
            )
            
            project_idea = project_idea_result["project_idea"]
            project_name = self._extract_project_name(project_idea)
            problem_statement = self._extract_problem_statement(project_idea)
            
            # Step 2: Analyze Career Impact
            self.logger.info("📈 Step 2: Analyzing career impact...")
            career_analysis = self.idea_agent.analyze_career_impact(
                project_idea=project_idea,
                target_role=target_role,
                experience_level=difficulty
            )
            
            # Step 3: Create Project Structure
            self.logger.info("🏗️ Step 3: Creating comprehensive project structure...")
            project_structure = self.planner_agent.create_project_structure(
                project_idea=project_idea,
                tech_stack=tech_stack,
                difficulty=difficulty,
                target_audience=user_profile,
                learning_goals="Build portfolio project and gain job-ready skills"
            )
            
            # Step 4: Create Project Roadmap
            self.logger.info("🗺️ Step 4: Creating project roadmap...")
            roadmap = self.planner_agent.create_project_roadmap(
                project_name=project_name,
                duration=self._get_project_duration(difficulty),
                difficulty=difficulty,
                career_goals=f"Get hired as a {target_role}"
            )
            
            # Step 5: Generate Project Introduction
            self.logger.info("📖 Step 5: Creating engaging project introduction...")
            intro_content = self.content_agent.generate_project_introduction(
                project_name=project_name,
                problem_statement=problem_statement,
                target_users=self._extract_target_users(project_idea),
                tech_stack=tech_stack,
                career_relevance=self._extract_career_relevance(career_analysis["career_analysis"])
            )
            
            # Step 6: Generate Detailed Content for Each Section
            self.logger.info("✍️ Step 6: Generating detailed content for all sections...")
            complete_sections = self._generate_complete_sections(
                project_structure, project_name, tech_stack, domain
            )
            
            # Step 7: Create Final Project Schema
            self.logger.info("📋 Step 7: Creating final project schema...")
            project_metadata = {
                "name": project_name,
                "description": problem_statement,
                "tech_stack": tech_stack.split(", "),
                "roadmap": self._determine_roadmap(tech_stack),
                "difficulty": difficulty,
                "domain": domain
            }
            
            final_schema = self.planner_agent.generate_course_schema(
                project_structure["parsed_structure"],
                project_metadata
            )
            
            # Step 8: Create final project structure in correct API format
            final_project_data = self._create_project_structure(
                project_name=project_name,
                description=problem_statement,
                difficulty_level=difficulty,
                roadmap=self._determine_roadmap(tech_stack),
                tech_stack=tech_stack.split(", "),
                meta_content=intro_content,
                sections=complete_sections,
                career_enhancement={
                    "target_role": target_role,
                    "skill_development": self._extract_skills(career_analysis["career_analysis"]),
                    "hiring_advantages": career_analysis.get("hiring_advantages", []),
                    "interview_preparation": self._create_interview_prep(project_idea, career_analysis),
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
    
    def generate_project_from_idea(self, project_idea: str,
                                 user_profile: str = "Indian developers") -> Dict[str, Any]:
        """Create a complete project from a provided project idea.
        
        Args:
            project_idea: Custom project idea provided by user
            user_profile: User profile to determine difficulty
            
        Returns:
            Complete project based on the provided idea
        """
        self.logger.info(f"🎯 Creating project from custom idea: {project_idea[:50]}...")
        
        try:
            # Auto-determine tech stack and difficulty from the project idea
            tech_stack = self._auto_determine_tech_stack_from_idea(project_idea)
            difficulty = self._auto_determine_difficulty(user_profile)
            
            self.logger.info(f"🎯 Auto-determined: {tech_stack} stack, {difficulty} difficulty")
            
            project_name = self._extract_project_name(project_idea)
            problem_statement = self._extract_problem_statement(project_idea)
            
            # Use auto-determined values for project structure
            project_structure = self.planner_agent.create_project_structure(
                project_idea=project_idea,
                tech_stack=tech_stack,
                difficulty=difficulty
            )
            
            # Generate content for the custom idea
            intro_content = self.content_agent.generate_project_introduction(
                project_name=project_name,
                problem_statement=problem_statement,
                target_users="Indian users looking for better solutions",
                tech_stack=tech_stack,
                career_relevance="Demonstrates problem-solving and technical skills"
            )
            
            complete_sections = self._generate_complete_sections(
                project_structure, project_name, tech_stack, "custom"
            )
            
            # Create final project structure
            final_project_data = self._create_project_structure(
                project_name=project_name,
                description=problem_statement,
                difficulty_level=difficulty,
                roadmap=self._determine_roadmap(tech_stack),
                tech_stack=tech_stack.split(", "),
                meta_content=intro_content,
                sections=complete_sections,
                career_enhancement={
                    "target_role": "Software Developer",
                    "skill_development": ["Problem-solving", "Full-stack development", "Project management"],
                    "hiring_advantages": ["Custom solution approach", "Real-world problem solving"],
                    "interview_preparation": self._create_interview_prep(project_idea, {}),
                    "portfolio_guidance": self._create_portfolio_guidance(project_name, tech_stack),
                    "salary_impact": self._estimate_salary_impact(difficulty, "custom")
                },
                success_metrics={
                    "learning_objectives": ["Custom project implementation", "Technical problem solving"],
                    "completion_criteria": self._define_completion_criteria(difficulty),
                    "portfolio_readiness": self._assess_portfolio_readiness(complete_sections),
                    "career_readiness": "Good - demonstrates custom problem-solving abilities"
                }
            )
            
            return final_project_data
            
        except Exception as e:
            self.logger.error(f"❌ Error creating custom project: {str(e)}")
            raise
    
    def _generate_complete_sections(self, project_structure: Dict[str, Any], 
                                  project_name: str, tech_stack: str, 
                                  domain: str) -> List[Dict[str, Any]]:
        """Generate complete content for all sections and chapters."""
        sections = []
        parsed_structure = project_structure.get("parsed_structure", {})
        
        for i, section_data in enumerate(parsed_structure.get("sections", []), 1):
            section_name = section_data.get("name", f"Section {i}")
            chapters = []
            
            # Generate section introduction
            chapter_names = [ch.get("name", "") for ch in section_data.get("chapters", [])]
            section_intro = self.content_agent.generate_section_intro(
                section_name=section_name,
                section_goal=f"Master the skills needed for {section_name.lower()}",
                chapters=chapter_names,
                project_context=project_name
            )
            
            for j, chapter_data in enumerate(section_data.get("chapters", []), 1):
                chapter_name = chapter_data.get("name", f"Chapter {j}")
                
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
        tech_lower = tech_stack.lower()
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
        practical_keywords = [
            "implementation", "building", "creating", "developing", 
            "setup", "deployment", "testing", "integration"
        ]
        return any(keyword in chapter_name.lower() for keyword in practical_keywords)
    
    def _auto_determine_tech_stack(self, domain: str) -> str:
        """Automatically determine the best tech stack for a domain."""
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
        
        return domain_tech_map.get(domain.lower(), "React, Node.js, MongoDB, Express.js")
    
    def _auto_determine_tech_stack_from_idea(self, project_idea: str) -> str:
        """Determine tech stack from project idea description."""
        idea_lower = project_idea.lower()
        
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
        profile_lower = user_profile.lower()
        
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