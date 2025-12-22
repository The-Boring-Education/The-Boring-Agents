"""Project ideas generation agent for real-life project suggestions."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent


class ProjectAgent(BaseAgent):
    """Agent for generating real-life project ideas and implementations."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for project generation."""
        
        project_ideas_template = PromptTemplate(
            input_variables=["technology", "difficulty", "project_count", "domain"],
            template="""
            Generate {project_count} real-life project ideas using {technology} at {difficulty} difficulty level
            focusing on the {domain} domain.
            
            For each project, provide:
            1. Project Title
            2. Project Description (2-3 sentences)
            3. Key Features (5-7 main features)
            4. Technologies/Tools Required
            5. Estimated Timeline
            6. Learning Objectives
            7. Real-world Applications
            8. Monetization Potential
            9. Difficulty Breakdown (Frontend/Backend/Database/DevOps)
            10. Target Users
            
            Focus on projects that solve real problems and can be showcased in a portfolio.
            Include both MVP features and advanced features for scaling.
            """
        )
        
        project_architecture_template = PromptTemplate(
            input_variables=["project_title", "technology_stack"],
            template="""
            Create a detailed technical architecture for the project "{project_title}" 
            using the technology stack: {technology_stack}.
            
            Provide:
            1. System Architecture Overview
            2. Component Breakdown
            3. Database Schema Design
            4. API Design and Endpoints
            5. Frontend Architecture
            6. Backend Architecture
            7. Security Considerations
            8. Scalability Plans
            9. Development Phases
            10. Deployment Strategy
            11. Monitoring and Logging
            12. Testing Strategy
            
            Make it detailed enough for a developer to start implementation.
            """
        )
        
        implementation_guide_template = PromptTemplate(
            input_variables=["project_title", "phase", "technology"],
            template="""
            Create a step-by-step implementation guide for {phase} of the project "{project_title}" 
            using {technology}.
            
            Include:
            1. Setup and Prerequisites
            2. File Structure
            3. Core Implementation Steps (with code snippets)
            4. Configuration Details
            5. Testing Approach
            6. Common Issues and Solutions
            7. Best Practices
            8. Code Organization
            9. Performance Considerations
            10. Next Steps
            
            Provide practical, actionable guidance that a developer can follow.
            Include code examples and configuration files where appropriate.
            """
        )
        
        project_roadmap_template = PromptTemplate(
            input_variables=["project_title", "timeline", "team_size"],
            template="""
            Create a comprehensive project roadmap for "{project_title}" with a {timeline} timeline
            for a team of {team_size} developers.
            
            Structure the roadmap with:
            1. Project Phases (with milestones)
            2. Sprint Planning (2-week sprints)
            3. Task Breakdown and Estimation
            4. Resource Allocation
            5. Risk Assessment
            6. Dependencies Management
            7. Testing Phases
            8. Deployment Schedule
            9. Documentation Requirements
            10. Review and Feedback Cycles
            
            Include realistic time estimates and buffer time for unexpected challenges.
            Consider both technical and business requirements.
            """
        )
        
        portfolio_optimization_template = PromptTemplate(
            input_variables=["projects_list", "career_goal", "experience_level"],
            template="""
            Analyze these projects: {projects_list} for a {experience_level} developer
            aiming for {career_goal}.
            
            Provide recommendations for:
            1. Portfolio Optimization Strategy
            2. Skills Gap Analysis
            3. Project Priority Ranking
            4. Additional Projects to Consider
            5. Presentation and Documentation Tips
            6. GitHub Repository Organization
            7. Demo and Showcase Strategy
            8. Technical Blog Post Ideas
            9. Networking and Sharing Opportunities
            10. Interview Talking Points
            
            Focus on maximizing career impact and demonstrating relevant skills.
            """
        )
        
        return {
            "project_ideas": project_ideas_template,
            "project_architecture": project_architecture_template,
            "implementation_guide": implementation_guide_template,
            "project_roadmap": project_roadmap_template,
            "portfolio_optimization": portfolio_optimization_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate project content based on the specified type.
        
        Args:
            content_type: Type of content to generate
            **kwargs: Parameters specific to the content type
            
        Returns:
            Generated project content with metadata
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
                "estimated_reading_time": self._estimate_reading_time(generated_text),
                "complexity_score": self._calculate_complexity_score(kwargs)
            }
        }
        
        return result
    
    def generate_project_ideas(self, technology: str, difficulty: str = "intermediate",
                             project_count: int = 5, domain: str = "web development") -> Dict[str, Any]:
        """Generate project ideas for a specific technology and domain.
        
        Args:
            technology: Primary technology to use
            difficulty: Project difficulty level
            project_count: Number of projects to generate
            domain: Domain/industry focus
            
        Returns:
            List of project ideas with details
        """
        return self.generate_content(
            "project_ideas",
            technology=technology,
            difficulty=difficulty,
            project_count=project_count,
            domain=domain
        )
    
    def create_project_architecture(self, project_title: str, 
                                  technology_stack: str) -> Dict[str, Any]:
        """Create detailed technical architecture for a project.
        
        Args:
            project_title: Name of the project
            technology_stack: Technologies to be used
            
        Returns:
            Comprehensive technical architecture
        """
        return self.generate_content(
            "project_architecture",
            project_title=project_title,
            technology_stack=technology_stack
        )
    
    def create_implementation_guide(self, project_title: str, phase: str,
                                  technology: str) -> Dict[str, Any]:
        """Create step-by-step implementation guide.
        
        Args:
            project_title: Name of the project
            phase: Implementation phase (setup, backend, frontend, deployment, etc.)
            technology: Primary technology for this phase
            
        Returns:
            Detailed implementation guide
        """
        return self.generate_content(
            "implementation_guide",
            project_title=project_title,
            phase=phase,
            technology=technology
        )
    
    def create_project_roadmap(self, project_title: str, timeline: str = "3 months",
                             team_size: int = 1) -> Dict[str, Any]:
        """Create comprehensive project roadmap.
        
        Args:
            project_title: Name of the project
            timeline: Project timeline
            team_size: Number of team members
            
        Returns:
            Detailed project roadmap
        """
        return self.generate_content(
            "project_roadmap",
            project_title=project_title,
            timeline=timeline,
            team_size=team_size
        )
    
    def optimize_portfolio(self, projects_list: List[str], career_goal: str,
                         experience_level: str = "intermediate") -> Dict[str, Any]:
        """Optimize project portfolio for career goals.
        
        Args:
            projects_list: List of current/planned projects
            career_goal: Target career goal or role
            experience_level: Current experience level
            
        Returns:
            Portfolio optimization recommendations
        """
        projects_str = ", ".join(projects_list)
        return self.generate_content(
            "portfolio_optimization",
            projects_list=projects_str,
            career_goal=career_goal,
            experience_level=experience_level
        )
    
    def create_complete_project_package(self, technology: str, domain: str = "web development",
                                      difficulty: str = "intermediate") -> Dict[str, Any]:
        """Create a complete project package with ideas, architecture, and roadmap.
        
        Args:
            technology: Primary technology
            domain: Project domain
            difficulty: Difficulty level
            
        Returns:
            Complete project package
        """
        # Generate project ideas
        ideas = self.generate_project_ideas(technology, difficulty, 3, domain)
        
        # For the first project, create detailed package
        first_project = self._extract_first_project_title(ideas["generated_content"])
        
        if first_project:
            architecture = self.create_project_architecture(first_project, technology)
            roadmap = self.create_project_roadmap(first_project)
            setup_guide = self.create_implementation_guide(first_project, "setup and initialization", technology)
            
            return {
                "package_type": "complete_project_package",
                "technology": technology,
                "domain": domain,
                "difficulty": difficulty,
                "components": {
                    "project_ideas": ideas,
                    "detailed_architecture": architecture,
                    "project_roadmap": roadmap,
                    "setup_guide": setup_guide
                },
                "recommended_next_steps": [
                    "Review and select the most suitable project",
                    "Set up development environment",
                    "Create GitHub repository with proper structure",
                    "Follow the implementation roadmap",
                    "Document progress and learnings"
                ],
                "metadata": {
                    "created_at": self._get_timestamp(),
                    "estimated_completion_time": self._estimate_project_time(difficulty)
                }
            }
        else:
            return ideas
    
    def _extract_first_project_title(self, content: str) -> Optional[str]:
        """Extract the first project title from generated content."""
        lines = content.split('\n')
        for line in lines:
            if 'Project Title:' in line or '1.' in line:
                # Simple extraction logic - can be improved
                title = line.split(':')[-1].strip() if ':' in line else line.split('.')[-1].strip()
                return title[:50]  # Limit length
        return "Sample Project"
    
    def _estimate_reading_time(self, content: str) -> str:
        """Estimate reading time for the content."""
        word_count = len(content.split())
        minutes = max(1, word_count // 200)  # Average reading speed: 200 words/minute
        return f"{minutes} minutes"
    
    def _calculate_complexity_score(self, params: Dict[str, Any]) -> int:
        """Calculate complexity score based on parameters."""
        score = 1
        if params.get("difficulty") == "advanced":
            score += 2
        elif params.get("difficulty") == "intermediate":
            score += 1
        
        if params.get("project_count", 1) > 3:
            score += 1
        
        return min(score, 5)
    
    def _estimate_project_time(self, difficulty: str) -> str:
        """Estimate project completion time based on difficulty."""
        time_map = {
            "beginner": "2-4 weeks",
            "intermediate": "1-3 months", 
            "advanced": "3-6 months"
        }
        return time_map.get(difficulty, "1-3 months")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()