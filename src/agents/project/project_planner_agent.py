"""Project Planner Agent for structuring real-life projects into comprehensive learning paths."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate
import json
import uuid

from ...core.base_agent import BaseAgent


class ProjectPlannerAgent(BaseAgent):
    """Agent for planning comprehensive project structures that take students from idea to career success."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for project planning."""
        
        project_structure_template = PromptTemplate(
            input_variables=["project_idea", "tech_stack", "difficulty", "target_audience", "learning_goals"],
            template="""
            You are the world's best product manager and technical educator who has designed 50+ successful tech courses.
            You understand how to break down complex projects into manageable, engaging learning experiences.
            
            **Project Idea:** {project_idea}
            **Tech Stack:** {tech_stack}  
            **Difficulty:** {difficulty}
            **Target Audience:** {target_audience}
            **Learning Goals:** {learning_goals}
            
            Create a comprehensive project structure that follows this proven learning path:
            
            # 📋 Project Structure: [Project Name]
            
            ## 🎯 Learning Journey Overview
            **Total Duration:** [X weeks/months]
            **Key Skills Students Will Gain:**
            1. [Skill 1] - [Why this matters for their career]
            2. [Skill 2] - [Real-world application]
            3. [Skill 3] - [Industry relevance]
            
            **Career Outcomes:**
            - Portfolio project that stands out to employers
            - Technical skills relevant to current job market
            - Problem-solving experience for interview discussions
            - Understanding of full product development lifecycle
            
            ## 📚 Section Breakdown
            
            ### Section 1: Foundation & Research (Week 1-2)
            **Goal:** Understand the problem deeply and research the market
            
            **Chapters:**
            1. **Project Introduction** 
               - What problem are we solving and why?
               - Real-world context and market opportunity
               - Success stories of similar solutions
               
            2. **Market Research & User Analysis**
               - Understanding target users in India
               - Competitive analysis of existing solutions
               - Identifying gaps and opportunities
               
            3. **Technical Planning**
               - Architecture decisions and tech stack rationale
               - Development environment setup
               - Project scope and MVP definition
            
            ### Section 2: Design & User Experience (Week 2-3)
            **Goal:** Create user-centered design and plan the user journey
            
            **Chapters:**
            1. **User Journey Mapping**
               - Understanding user flow and pain points
               - Creating user personas for Indian market
               - Defining success metrics
               
            2. **Design System Planning**
               - UI/UX principles for your target users
               - Design tools and workflow setup
               - Mobile-first design considerations for India
               
            3. **Prototyping & Validation**
               - Creating wireframes and mockups
               - Getting feedback from potential users
               - Iterating based on user input
            
            ### Section 3: Development Setup & Foundation (Week 3-4)
            **Goal:** Set up development environment and create project foundation
            
            **Chapters:**
            1. **Development Environment Setup**
               - Version control with Git and GitHub
               - Development tools and IDE configuration
               - Setting up CI/CD pipeline basics
               
            2. **Project Structure & Architecture**
               - Creating scalable project structure
               - Database design and modeling
               - API planning and documentation
               
            3. **Authentication & Security**
               - User authentication implementation
               - Data security best practices
               - Privacy considerations for Indian users
            
            ### Section 4: Core Feature Development (Week 4-6)
            **Goal:** Build the main features that solve the core problem
            
            **Chapters:**
            1. **Core Feature Implementation**
               - Building the main problem-solving feature
               - Data processing and business logic
               - Error handling and edge cases
               
            2. **User Interface Development**
               - Building responsive and accessible UI
               - Implementing design system
               - User feedback and interaction design
               
            3. **Data Management & Analytics**
               - Database operations and optimization
               - User analytics and behavior tracking
               - Performance monitoring setup
            
            ### Section 5: Advanced Features & Integration (Week 6-7)
            **Goal:** Add advanced features that make the project stand out
            
            **Chapters:**
            1. **Third-Party Integrations**
               - Payment gateway integration (for Indian market)
               - Social media and sharing features
               - External API integrations
               
            2. **Performance Optimization**
               - Code optimization and refactoring
               - Database query optimization
               - Frontend performance improvements
               
            3. **Advanced User Features**
               - Personalization and recommendations
               - Advanced search and filtering
               - Social features and community building
            
            ### Section 6: Testing & Quality Assurance (Week 7-8)
            **Goal:** Ensure the project is production-ready and robust
            
            **Chapters:**
            1. **Comprehensive Testing**
               - Unit testing and integration testing
               - User acceptance testing
               - Performance and load testing
               
            2. **Bug Fixing & Refinement**
               - Issue tracking and resolution
               - Code review and quality improvements
               - User feedback incorporation
               
            3. **Documentation & Code Quality**
               - Technical documentation writing
               - Code commenting and maintainability
               - README and setup instructions
            
            ### Section 7: Deployment & DevOps (Week 8-9)
            **Goal:** Deploy the project to production and set up monitoring
            
            **Chapters:**
            1. **Production Deployment**
               - Cloud platform setup (AWS/GCP/Azure)
               - Domain configuration and SSL setup
               - Environment configuration management
               
            2. **Monitoring & Analytics**
               - Application monitoring setup
               - User analytics implementation
               - Error tracking and alerting
               
            3. **Scaling & Maintenance**
               - Auto-scaling configuration
               - Backup and disaster recovery
               - Maintenance and update procedures
            
            ### Section 8: Career Growth & Showcase (Week 9-10)
            **Goal:** Transform the project into career advancement opportunities
            
            **Chapters:**
            1. **Portfolio Presentation**
               - Creating compelling project documentation
               - Recording demo videos and walkthroughs
               - Writing technical blog posts about learnings
               
            2. **Resume & Interview Preparation**
               - Adding project to resume effectively
               - Preparing interview talking points
               - Creating technical presentation slides
               
            3. **Community Engagement & Growth**
               - Open-sourcing and community building
               - Speaking about the project at meetups
               - Networking with industry professionals
               
            4. **Business Development (Optional)**
               - Market validation and user feedback
               - Business model development
               - Funding and investment preparation
            
            ## 🎯 Assignment Strategy
            **Throughout each section:**
            - Hands-on coding assignments
            - Research and analysis tasks
            - User feedback collection
            - Portfolio building activities
            - Peer review and collaboration
            
            ## 📊 Success Metrics
            **Technical Metrics:**
            - Functional features that solve real problems
            - Clean, maintainable, and well-documented code
            - Production-ready deployment with monitoring
            
            **Career Metrics:**
            - Compelling portfolio piece for job applications
            - Technical skills relevant to target roles
            - Ability to discuss project confidently in interviews
            - Network connections made through project sharing
            
            This structure ensures students don't just build a project, but develop into confident, hireable developers who understand the full product lifecycle!
            """
        )
        
        chapter_breakdown_template = PromptTemplate(
            input_variables=["section_name", "section_goal", "project_context", "chapter_number", "total_chapters"],
            template="""
            You are an expert technical educator creating detailed chapter content for project-based learning.
            
            **Section:** {section_name}
            **Section Goal:** {section_goal}
            **Project Context:** {project_context}
            **Chapter:** {chapter_number} of {total_chapters}
            
            Create a detailed chapter breakdown that follows the proven learning methodology:
            
            # Chapter {chapter_number}: [Chapter Name]
            
            ## 🎯 Learning Objectives
            By the end of this chapter, students will be able to:
            1. [Specific skill 1] - [Why this matters for their project]
            2. [Specific skill 2] - [How this applies to real-world scenarios]
            3. [Specific skill 3] - [Career relevance and industry application]
            
            ## 🧠 Problem-Solving Focus
            **Real Challenge:** [What specific challenge does this chapter solve?]
            **Why It Matters:** [Why is this important for the overall project success?]
            **Industry Context:** [How do professional developers handle this challenge?]
            
            ## 📚 Content Structure
            
            ### Introduction (5 minutes)
            - **The Challenge:** Brief overview of what we're solving
            - **Real-World Context:** Examples from successful Indian startups
            - **Success Vision:** What students will accomplish by chapter end
            
            ### Theory & Concepts (15 minutes)
            - **Core Concepts:** [Key technical concepts to understand]
            - **Best Practices:** [Industry-standard approaches]
            - **Indian Context:** [Specific considerations for Indian market/users]
            
            ### Hands-On Implementation (45 minutes)
            - **Step-by-Step Guide:** [Detailed implementation steps]
            - **Code Examples:** [Specific code snippets and explanations]
            - **Common Pitfalls:** [What to avoid and why]
            
            ### Testing & Validation (15 minutes)
            - **How to Test:** [Testing methodology for this feature]
            - **Success Criteria:** [How to know if implementation is correct]
            - **User Feedback:** [How to validate with real users]
            
            ### Career Connection (10 minutes)
            - **Interview Relevance:** [How this skill helps in interviews]
            - **Portfolio Impact:** [How to showcase this in portfolio]
            - **Industry Application:** [Where this skill is used professionally]
            
            ## 🛠️ Practical Activities
            
            ### Main Assignment
            **Task:** [Specific, measurable task for students to complete]
            **Deliverable:** [What they should submit/achieve]
            **Success Metrics:** [How to measure completion and quality]
            
            ### Bonus Challenges (Optional)
            1. [Advanced challenge 1] - For students who want to go deeper
            2. [Research challenge] - To understand industry applications better
            3. [Innovation challenge] - To add unique features or improvements
            
            ## 🤔 Reflection Questions
            1. How does this implementation solve the user's problem?
            2. What would you do differently for a larger scale application?
            3. How would you explain this feature to a non-technical stakeholder?
            4. What additional features could enhance this functionality?
            
            ## 🚀 Next Steps
            **Preparation for Next Chapter:**
            - [Specific prep work needed]
            - [Concepts to review or research]
            - [Tools or setup required]
            
            **Continuous Learning:**
            - [Additional resources for deeper understanding]
            - [Related industry articles or case studies]
            - [Community forums or discussions to join]
            
            Make this chapter practical, engaging, and directly connected to career success!
            """
        )
        
        project_roadmap_template = PromptTemplate(
            input_variables=["project_name", "duration", "difficulty", "career_goals"],
            template="""
            You are a senior engineering manager creating a development roadmap for a high-impact project.
            
            **Project:** {project_name}
            **Duration:** {duration}
            **Difficulty:** {difficulty}
            **Career Goals:** {career_goals}
            
            Create a comprehensive project roadmap that balances learning, building, and career growth:
            
            # 🗺️ Project Roadmap: {project_name}
            
            ## 📅 Timeline Overview
            **Total Duration:** {duration}
            **Weekly Commitment:** 15-20 hours (3 hours/day weekdays + weekends)
            **Milestone Schedule:** Weekly check-ins with major milestones every 2 weeks
            
            ## 🎯 Phase-by-Phase Breakdown
            
            ### Phase 1: Foundation (20% of timeline)
            **Focus:** Understanding, Planning, and Setup
            
            **Week-by-Week:**
            - **Week 1:** Problem research and market analysis
            - **Week 2:** Technical planning and environment setup
            
            **Key Deliverables:**
            - Market research document
            - Technical architecture diagram
            - Development environment ready
            - GitHub repository with initial structure
            
            **Skills Developed:**
            - Problem analysis and market research
            - Technical planning and architecture design
            - Development workflow setup
            
            ### Phase 2: Core Development (40% of timeline)
            **Focus:** Building the main features that solve the problem
            
            **Week-by-Week Progression:**
            - **Week 3:** Authentication and basic user management
            - **Week 4:** Core feature implementation (main problem-solving functionality)
            - **Week 5:** User interface and experience implementation
            - **Week 6:** Data management and business logic refinement
            
            **Key Deliverables:**
            - Working authentication system
            - Core features fully implemented
            - Responsive user interface
            - Database with real data
            
            **Skills Developed:**
            - Full-stack development
            - User experience design
            - Database design and management
            - API development
            
            ### Phase 3: Enhancement (25% of timeline)
            **Focus:** Advanced features, optimization, and polish
            
            **Week-by-Week Progression:**
            - **Week 7:** Advanced features and integrations
            - **Week 8:** Performance optimization and testing
            
            **Key Deliverables:**
            - Advanced features working
            - Optimized performance
            - Comprehensive test suite
            - Bug-free user experience
            
            **Skills Developed:**
            - Performance optimization
            - Testing methodologies
            - Third-party integrations
            - Quality assurance
            
            ### Phase 4: Deployment & Career (15% of timeline)
            **Focus:** Production deployment and career preparation
            
            **Week-by-Week Progression:**
            - **Week 9:** Production deployment and monitoring
            - **Week 10:** Portfolio preparation and career activities
            
            **Key Deliverables:**
            - Live, production-ready application
            - Comprehensive documentation
            - Portfolio presentation materials
            - Resume and interview preparation
            
            **Skills Developed:**
            - DevOps and deployment
            - Documentation and communication
            - Portfolio presentation
            - Professional networking
            
            ## 🏆 Milestone Achievements
            
            **Milestone 1 (End of Week 2):** Foundation Complete
            - ✅ Problem clearly defined and researched
            - ✅ Technical architecture documented
            - ✅ Development environment operational
            
            **Milestone 2 (End of Week 4):** MVP Complete
            - ✅ Core functionality working
            - ✅ Basic user interface implemented
            - ✅ Authentication system functional
            
            **Milestone 3 (End of Week 6):** Full Features Complete
            - ✅ All planned features implemented
            - ✅ User experience polished
            - ✅ Data management robust
            
            **Milestone 4 (End of Week 8):** Production Ready
            - ✅ Performance optimized
            - ✅ Testing comprehensive
            - ✅ Code quality high
            
            **Milestone 5 (End of Week 10):** Career Ready
            - ✅ Application deployed and live
            - ✅ Portfolio materials prepared
            - ✅ Ready for job applications and interviews
            
            ## 🚀 Risk Management
            
            **Common Challenges & Solutions:**
            1. **Technical Roadblocks:** 
               - Solution: Community support, office hours, fallback simpler approaches
            2. **Time Management:**
               - Solution: Flexible milestone dates, priority-focused development
            3. **Scope Creep:**
               - Solution: Clear MVP definition, feature prioritization framework
            4. **Learning Curve:**
               - Solution: Just-in-time learning, practical tutorials, peer support
            
            ## 📊 Success Metrics
            
            **Technical Success:**
            - Functional application solving the defined problem
            - Clean, maintainable, well-documented code
            - Production deployment with monitoring
            
            **Learning Success:**
            - Demonstrated competency in target tech stack
            - Understanding of full development lifecycle
            - Ability to explain technical decisions and trade-offs
            
            **Career Success:**
            - Compelling portfolio piece for job applications
            - Increased confidence in technical interviews
            - Network connections and community engagement
            - Clear next steps for continued growth
            
            This roadmap ensures students build both technical skills and career readiness simultaneously!
            """
        )
        
        return {
            "project_structure": project_structure_template,
            "chapter_breakdown": chapter_breakdown_template,
            "project_roadmap": project_roadmap_template
        }
    
    def create_project_structure(self, project_idea: str, tech_stack: str, 
                               difficulty: str = "Intermediate",
                               target_audience: str = "College students and working professionals",
                               learning_goals: str = "Build portfolio project and gain job-ready skills") -> Dict[str, Any]:
        """Create comprehensive project structure with sections and chapters.
        
        Args:
            project_idea: The project idea to structure
            tech_stack: Technology stack for the project
            difficulty: Project difficulty level
            target_audience: Target learners
            learning_goals: Desired learning outcomes
            
        Returns:
            Complete project structure with metadata
        """
        result = self.generate_content(
            "project_structure",
            project_idea=project_idea,
            tech_stack=tech_stack,
            difficulty=difficulty,
            target_audience=target_audience,
            learning_goals=learning_goals
        )
        
        # Parse the structure into usable format
        structure = self._parse_project_structure(result["generated_content"])
        
        return {
            "project_structure": result["generated_content"],
            "parsed_structure": structure,
            "metadata": {
                "tech_stack": tech_stack,
                "difficulty": difficulty,
                "estimated_duration": self._estimate_duration(difficulty),
                "target_skills": self._extract_target_skills(result["generated_content"]),
                "career_outcomes": self._extract_career_outcomes(result["generated_content"])
            }
        }
    
    def create_detailed_chapter(self, section_name: str, section_goal: str, 
                              project_context: str, chapter_number: int, 
                              total_chapters: int) -> Dict[str, Any]:
        """Create detailed breakdown for a specific chapter.
        
        Args:
            section_name: Name of the section this chapter belongs to
            section_goal: Goal of the section
            project_context: Context about the overall project
            chapter_number: Chapter number
            total_chapters: Total chapters in the section
            
        Returns:
            Detailed chapter breakdown
        """
        result = self.generate_content(
            "chapter_breakdown",
            section_name=section_name,
            section_goal=section_goal,
            project_context=project_context,
            chapter_number=chapter_number,
            total_chapters=total_chapters
        )
        
        return {
            "chapter_content": result["generated_content"],
            "learning_objectives": self._extract_learning_objectives(result["generated_content"]),
            "practical_activities": self._extract_activities(result["generated_content"]),
            "time_estimate": self._estimate_chapter_time(result["generated_content"])
        }
    
    def create_project_roadmap(self, project_name: str, duration: str = "10 weeks",
                             difficulty: str = "Intermediate", 
                             career_goals: str = "Get hired as a software developer") -> Dict[str, Any]:
        """Create a comprehensive project roadmap with timelines and milestones.
        
        Args:
            project_name: Name of the project
            duration: Project duration
            difficulty: Difficulty level
            career_goals: Career objectives
            
        Returns:
            Detailed project roadmap
        """
        result = self.generate_content(
            "project_roadmap",
            project_name=project_name,
            duration=duration,
            difficulty=difficulty,
            career_goals=career_goals
        )
        
        return {
            "roadmap": result["generated_content"],
            "milestones": self._extract_milestones(result["generated_content"]),
            "phases": self._extract_phases(result["generated_content"]),
            "success_metrics": self._extract_success_metrics(result["generated_content"])
        }
    
    def generate_course_schema(self, project_structure: Dict[str, Any], 
                             project_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the course schema compatible with the existing API format.
        
        Args:
            project_structure: The structured project content
            project_metadata: Project metadata
            
        Returns:
            Course schema following the API format
        """
        sections = self._create_sections_from_structure(project_structure)
        
        schema = {
            "_id": self._generate_id(),
            "name": project_metadata.get("name", "Untitled Project"),
            "description": project_metadata.get("description", ""),
            "coverImageURL": self._generate_cover_image_url(project_metadata.get("name", "")),
            "slug": self._generate_slug(project_metadata.get("name", "")),
            "requiredSkills": project_metadata.get("tech_stack", []),
            "roadmap": project_metadata.get("roadmap", "Full Stack"),
            "difficultyLevel": project_metadata.get("difficulty", "Intermediate"),
            "isActive": True,
            "sections": sections,
            "meta": self._generate_meta_content(project_metadata),
            "isEnrolled": False
        }
        
        return schema
    
    def _parse_project_structure(self, content: str) -> Dict[str, Any]:
        """Parse project structure content into structured data."""
        # Simple parsing - in production would use more sophisticated methods
        lines = content.split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('### Section'):
                if current_section:
                    sections.append(current_section)
                section_name = line.replace('### Section', '').strip()
                current_section = {
                    "name": section_name,
                    "chapters": []
                }
            elif line.startswith('1. **') or line.startswith('2. **') or line.startswith('3. **'):
                if current_section:
                    chapter_name = line.split('**')[1] if '**' in line else line
                    current_section["chapters"].append({"name": chapter_name})
        
        if current_section:
            sections.append(current_section)
        
        return {"sections": sections}
    
    def _estimate_duration(self, difficulty: str) -> str:
        """Estimate project duration based on difficulty."""
        duration_map = {
            "Beginner": "6-8 weeks",
            "Intermediate": "8-12 weeks",
            "Advanced": "12-16 weeks"
        }
        return duration_map.get(difficulty, "8-10 weeks")
    
    def _extract_target_skills(self, content: str) -> List[str]:
        """Extract target skills from content."""
        # Simple extraction - would be more sophisticated in production
        return ["Full-stack development", "Problem-solving", "Product thinking", "Career readiness"]
    
    def _extract_career_outcomes(self, content: str) -> List[str]:
        """Extract career outcomes from content."""
        return ["Portfolio project", "Interview readiness", "Technical skills", "Industry knowledge"]
    
    def _extract_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from chapter content."""
        lines = content.split('\n')
        objectives = []
        in_objectives = False
        
        for line in lines:
            if 'Learning Objectives' in line:
                in_objectives = True
            elif in_objectives and line.strip().startswith(('1.', '2.', '3.')):
                objectives.append(line.strip())
            elif in_objectives and not line.strip():
                in_objectives = False
        
        return objectives
    
    def _extract_activities(self, content: str) -> List[str]:
        """Extract practical activities from chapter content."""
        lines = content.split('\n')
        activities = []
        in_activities = False
        
        for line in lines:
            if 'Practical Activities' in line:
                in_activities = True
            elif in_activities and '**Task:**' in line:
                activities.append(line.replace('**Task:**', '').strip())
            elif in_activities and line.startswith('##'):
                in_activities = False
        
        return activities
    
    def _estimate_chapter_time(self, content: str) -> str:
        """Estimate time needed for chapter completion."""
        # Simple estimation based on content length
        word_count = len(content.split())
        if word_count > 1000:
            return "3-4 hours"
        elif word_count > 500:
            return "2-3 hours"
        else:
            return "1-2 hours"
    
    def _extract_milestones(self, content: str) -> List[str]:
        """Extract milestones from roadmap content."""
        lines = content.split('\n')
        milestones = []
        
        for line in lines:
            if 'Milestone' in line and ':' in line:
                milestones.append(line.strip())
        
        return milestones
    
    def _extract_phases(self, content: str) -> List[str]:
        """Extract phases from roadmap content."""
        lines = content.split('\n')
        phases = []
        
        for line in lines:
            if 'Phase' in line and ':' in line:
                phases.append(line.strip())
        
        return phases
    
    def _extract_success_metrics(self, content: str) -> List[str]:
        """Extract success metrics from roadmap content."""
        return ["Technical competency", "Portfolio quality", "Career readiness", "Industry knowledge"]
    
    def _create_sections_from_structure(self, structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create sections array from parsed structure."""
        sections = []
        
        for i, section_data in enumerate(structure.get("sections", []), 1):
            chapters = []
            for j, chapter_data in enumerate(section_data.get("chapters", []), 1):
                chapters.append({
                    "chapterId": self._generate_id(),
                    "chapterName": f"{j}. {chapter_data.get('name', 'Chapter')}",
                    "content": f"# {j}. {chapter_data.get('name', 'Chapter')}\n\nContent will be generated here...",
                    "isOptional": False
                })
            
            sections.append({
                "sectionId": self._generate_id(),
                "sectionName": f"{i}. {section_data.get('name', 'Section')}",
                "chapters": chapters
            })
        
        return sections
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        return str(uuid.uuid4()).replace("-", "")
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug."""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_cover_image_url(self, name: str) -> str:
        """Generate cover image URL."""
        slug = self._generate_slug(name)
        return f"https://ik.imagekit.io/tbe/webapp/tbp-{slug}-1.svg"
    
    def _generate_meta_content(self, metadata: Dict[str, Any]) -> str:
        """Generate meta content for the project."""
        return f"""# Introduction

Welcome to building {metadata.get('name', 'your project')}! This is a comprehensive, hands-on project that will take you from problem identification to deployment, building real-world skills that employers value.

# Problem Statement

{metadata.get('description', 'We will solve a real problem that affects millions of users.')}

# What will you learn?

You'll gain practical experience in:
- Full-stack development with {metadata.get('tech_stack', 'modern technologies')}
- Product thinking and user-centered design
- Professional development workflows
- Deployment and DevOps practices
- Portfolio building and career preparation

This project will make you stand out in the competitive job market!"""
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate project planning content based on the content type."""
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