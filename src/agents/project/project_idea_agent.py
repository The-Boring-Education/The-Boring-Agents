"""Project Idea Agent for generating real-life project ideas for Indian students and professionals."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class ProjectIdeaAgent(BaseAgent):
    """Agent for generating real-life project ideas that solve actual problems and help with career growth."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for project idea generation."""
        
        real_life_project_template = PromptTemplate(
            input_variables=["domain", "tech_stack", "difficulty", "user_profile", "market_focus"],
            template="""
            You are a successful Indian entrepreneur and tech mentor who has built 15+ startups and hired 200+ developers.
            You understand the Indian market, student struggles, and what employers actually want to see in portfolios.
            
            **Domain:** {domain}
            **Tech Stack:** {tech_stack}
            **Difficulty:** {difficulty}
            **User Profile:** {user_profile}
            **Market Focus:** {market_focus}
            
            Generate a REAL-LIFE project idea that:
            
            ## 🎯 Project Vision
            **Project Name:** [Catchy, memorable name that sounds like a real startup]
            
            **One-Line Problem:** [What specific problem does this solve for Indian users?]
            
            **Real-World Context:**
            - Why this problem exists in India specifically
            - How current solutions fail Indian users
            - Market size and opportunity in India
            - Examples of similar successful Indian companies
            
            ## 💡 The Big Idea
            **Core Solution:**
            [Explain the solution in 2-3 sentences like you're pitching to an investor]
            
            **Why This Will Work:**
            1. [First reason why this is a great idea]
            2. [Second reason with Indian market context]
            3. [Third reason about timing and opportunity]
            
            **Target Users:**
            - Primary: [Who will use this the most?]
            - Secondary: [Who else might find this useful?]
            - Pain Points: [What frustrates these users currently?]
            
            ## 🚀 Career Impact
            **Why This Project Will Get You Hired:**
            1. **Problem-Solving:** Shows you can identify and solve real problems
            2. **Market Understanding:** Demonstrates knowledge of Indian market
            3. **Technical Skills:** Uses relevant tech stack employers want
            4. **Product Thinking:** Shows you think like a product manager
            5. **Impact Potential:** Interviewers love projects that could be real businesses
            
            **Interview Talking Points:**
            - "I identified this problem when I personally faced..."
            - "Research showed that 60% of Indian users struggle with..."
            - "My solution reduces [specific metric] by 40%..."
            - "This could potentially serve [X million] Indians..."
            
            **Resume Headlines:**
            - Built [Project Name] - A platform that [impact metric]
            - Solved [problem] for [target users] using [tech stack]
            - Created [solution] that [specific achievement/metric]
            
            ## 💼 Industry Relevance
            **Companies That Would Love This:**
            - **FAANG:** [Why would Google/Meta/Amazon be interested?]
            - **Indian Unicorns:** [How does this relate to Flipkart/Swiggy/Paytm?]
            - **Startups:** [What startups are working on similar problems?]
            - **MNCs:** [Why would TCS/Infosys/Accenture value this?]
            
            **Current Market Trends:**
            - [Trend 1] - How your project aligns with this
            - [Trend 2] - Why this technology is hot right now
            - [Trend 3] - Future potential and scalability
            
            ## 📊 Success Metrics
            **How to Measure Impact:**
            1. [Metric 1] - [How to measure it]
            2. [Metric 2] - [Why this matters to users]
            3. [Metric 3] - [Business impact measurement]
            
            **Portfolio Showcase:**
            - Demo video showing the problem and solution
            - Before/after comparisons
            - User feedback or testimonials
            - Technical architecture diagram
            - Growth metrics and potential scale
            
            ## 🎨 Innovation Factor
            **What Makes This Different:**
            - [Unique aspect 1] - Not available in existing solutions
            - [Unique aspect 2] - Indian-specific innovation
            - [Unique aspect 3] - Technical differentiation
            
            **Future Expansion Ideas:**
            - Phase 2: [Next level features]
            - Phase 3: [Scale and monetization]
            - Long-term: [How this could become a real startup]
            
            Make this sound like a project that could actually become the next big Indian startup! 
            Students should feel excited to build this and confident it will help their career.
            """
        )
        
        problem_research_template = PromptTemplate(
            input_variables=["domain", "indian_context"],
            template="""
            You are a market researcher who has studied the Indian tech ecosystem for 10+ years.
            You understand what problems Indian users face and what gaps exist in current solutions.
            
            **Domain:** {domain}
            **Indian Context:** {indian_context}
            
            Research and identify REAL problems in this domain that students can solve:
            
            ## 🔍 Problem Discovery
            
            **Current Pain Points in India:**
            1. [Problem 1] - Specific to Indian market conditions
            2. [Problem 2] - Cultural or economic factors
            3. [Problem 3] - Infrastructure or technology gaps
            
            **Why These Problems Exist:**
            - [Root cause 1] - Systemic issues
            - [Root cause 2] - Market dynamics
            - [Root cause 3] - User behavior patterns
            
            **Existing Solutions and Their Gaps:**
            - [Solution 1] - Why it doesn't work well in India
            - [Solution 2] - What it misses for Indian users
            - [Solution 3] - Opportunities for improvement
            
            ## 💡 Opportunity Analysis
            
            **Market Size:**
            - Total Addressable Market (TAM) in India
            - Serviceable Addressable Market (SAM)
            - Immediate opportunity size
            
            **User Behavior Insights:**
            - How Indians currently solve this problem
            - What frustrates them about current solutions
            - What they're willing to pay for
            
            **Technology Trends:**
            - Emerging tech that could solve this better
            - Mobile-first considerations for India
            - Offline-to-online bridge opportunities
            
            ## 🎯 Project Viability
            
            **Why This is Perfect for Students:**
            - Can be built with [{domain}] tech stack
            - Doesn't require massive infrastructure
            - Shows understanding of Indian market
            - Demonstrates problem-solving skills
            
            **Success Examples:**
            - Similar problems solved by Indian startups
            - International solutions adapted for India
            - Student projects that became real companies
            
            Focus on problems that are real, solvable, and impressive to employers!
            """
        )
        
        career_impact_template = PromptTemplate(
            input_variables=["project_idea", "target_role", "experience_level"],
            template="""
            You are a senior technical recruiter who has hired 500+ developers for Indian startups and MNCs.
            You know exactly what impresses hiring managers and what gets candidates hired.
            
            **Project Idea:** {project_idea}
            **Target Role:** {target_role}
            **Experience Level:** {experience_level}
            
            Analyze how this project will boost their career prospects:
            
            ## 💼 Hiring Manager's Perspective
            
            **What They'll Love:**
            1. **Problem-First Thinking:** "This candidate doesn't just code, they solve real problems"
            2. **Market Awareness:** "They understand the Indian market and user needs"
            3. **Product Mindset:** "They think beyond just technical implementation"
            4. **Initiative:** "They built something meaningful on their own"
            
            **Interview Questions This Will Help With:**
            - "Tell me about a challenging project you built"
            - "How do you approach problem-solving?"
            - "What's your understanding of our market?"
            - "Show me something you're proud of building"
            
            ## 🎯 Role-Specific Value
            
            **For {target_role} Positions:**
            - Skill 1: [How project demonstrates this key skill]
            - Skill 2: [Real-world application of this skill]
            - Skill 3: [Why this matters for the role]
            
            **Company-Type Fit:**
            - **Startups:** Love the entrepreneurial thinking and end-to-end ownership
            - **MNCs:** Appreciate the scale considerations and systematic approach
            - **Product Companies:** Value the user-centric design and market research
            - **Service Companies:** Impressed by client-ready solution and business understanding
            
            ## 📈 Career Progression Impact
            
            **Immediate Benefits:**
            - Portfolio differentiator in a sea of todo apps and clones
            - Conversation starter in networking events
            - Confidence boost from building something real
            
            **Long-term Advantages:**
            - Foundation for future entrepreneurship
            - Understanding of full product development lifecycle
            - Network opportunities with like-minded builders
            
            **Salary Impact:**
            - {experience_level} developers with real projects: ₹{self._get_salary_range(experience_level)} higher
            - Premium for problem-solving skills vs just coding skills
            - Negotiation power from demonstrable impact
            
            ## 🏆 Success Stories
            
            **Students Who Got Hired Because of Similar Projects:**
            - [Example 1] - Fresher who got hired at [company] for [reason]
            - [Example 2] - Career switcher who impressed [company] with [project aspect]
            - [Example 3] - Experienced dev who got promoted because of [skill demonstrated]
            
            This project will make them stand out in a competitive job market!
            """
        )
        
        return {
            "real_life_project": real_life_project_template,
            "problem_research": problem_research_template,
            "career_impact": career_impact_template
        }
    
    def generate_real_life_project(self, domain: str, tech_stack: str, 
                                 difficulty: str = "Intermediate", 
                                 user_profile: str = "College student looking for internships",
                                 market_focus: str = "Indian market") -> Dict[str, Any]:
        """Generate a real-life project idea that solves actual problems.
        
        Args:
            domain: Domain/industry for the project (fintech, edtech, healthtech, etc.)
            tech_stack: Technology stack to use
            difficulty: Project difficulty level
            user_profile: Target user's background and goals
            market_focus: Geographic and market focus
            
        Returns:
            Comprehensive project idea with career impact analysis
        """
        result = self.generate_content(
            "real_life_project",
            domain=domain,
            tech_stack=tech_stack,
            difficulty=difficulty,
            user_profile=user_profile,
            market_focus=market_focus
        )
        
        return {
            "project_idea": result["generated_content"],
            "domain": domain,
            "tech_stack": tech_stack,
            "difficulty": difficulty,
            "market_value": self._assess_market_value(domain, tech_stack),
            "implementation_complexity": self._assess_complexity(difficulty, tech_stack)
        }
    
    def research_problem_space(self, domain: str, indian_context: str = "") -> Dict[str, Any]:
        """Research problems in a specific domain for project opportunities.
        
        Args:
            domain: Domain to research
            indian_context: Specific Indian market context
            
        Returns:
            Problem analysis and opportunities
        """
        context = indian_context or f"General {domain} problems in Indian market"
        
        result = self.generate_content(
            "problem_research",
            domain=domain,
            indian_context=context
        )
        
        return {
            "problem_analysis": result["generated_content"],
            "opportunities": self._extract_opportunities(result["generated_content"]),
            "market_insights": self._extract_market_insights(result["generated_content"])
        }
    
    def analyze_career_impact(self, project_idea: str, target_role: str = "Software Developer",
                            experience_level: str = "Entry Level") -> Dict[str, Any]:
        """Analyze how a project idea will impact career prospects.
        
        Args:
            project_idea: The project idea to analyze
            target_role: Target job role
            experience_level: Current experience level
            
        Returns:
            Career impact analysis
        """
        result = self.generate_content(
            "career_impact",
            project_idea=project_idea,
            target_role=target_role,
            experience_level=experience_level
        )
        
        return {
            "career_analysis": result["generated_content"],
            "hiring_advantages": self._extract_hiring_advantages(result["generated_content"]),
            "skill_demonstration": self._extract_skills(result["generated_content"])
        }
    
    def generate_project_suite(self, domain: str, tech_stack: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple related project ideas in a domain.
        
        Args:
            domain: Domain for projects
            tech_stack: Technology stack
            count: Number of projects to generate
            
        Returns:
            List of project ideas with varying complexity
        """
        difficulties = ["Beginner", "Intermediate", "Advanced"]
        user_profiles = [
            "College student looking for first internship",
            "Working professional seeking career switch", 
            "Experienced developer targeting senior roles"
        ]
        
        projects = []
        for i in range(count):
            difficulty = difficulties[i % len(difficulties)]
            profile = user_profiles[i % len(user_profiles)]
            
            project = self.generate_real_life_project(
                domain=domain,
                tech_stack=tech_stack,
                difficulty=difficulty,
                user_profile=profile
            )
            
            projects.append(project)
        
        return projects
    
    def _assess_market_value(self, domain: str, tech_stack: str) -> str:
        """Assess the market value of a domain and tech stack combination."""
        high_value_domains = ["fintech", "healthtech", "edtech", "ecommerce", "logistics"]
        trending_stacks = ["react", "node", "python", "go", "kubernetes", "aws"]
        
        domain_score = 3 if domain.lower() in high_value_domains else 2
        stack_score = 3 if any(tech in tech_stack.lower() for tech in trending_stacks) else 2
        
        total_score = domain_score + stack_score
        
        if total_score >= 5:
            return "High market value - very relevant to current hiring trends"
        elif total_score >= 4:
            return "Good market value - solid choice for career growth"
        else:
            return "Moderate market value - good for learning and skill building"
    
    def _assess_complexity(self, difficulty: str, tech_stack: str) -> str:
        """Assess implementation complexity."""
        complexity_map = {
            "Beginner": "2-3 weeks with guided learning",
            "Intermediate": "1-2 months with independent research",
            "Advanced": "3-4 months with significant innovation required"
        }
        
        base_time = complexity_map.get(difficulty, "1-2 months")
        
        if "microservices" in tech_stack.lower() or "kubernetes" in tech_stack.lower():
            return f"{base_time} (Complex architecture - great for senior roles)"
        else:
            return f"{base_time} (Manageable scope - perfect for learning)"
    
    def _extract_opportunities(self, content: str) -> List[str]:
        """Extract opportunity insights from problem research."""
        # Simple extraction - in production, would use more sophisticated parsing
        lines = content.split('\n')
        opportunities = []
        
        for line in lines:
            if 'opportunity' in line.lower() or 'potential' in line.lower():
                clean_line = line.strip('- ').strip()
                if len(clean_line) > 20:
                    opportunities.append(clean_line)
        
        return opportunities[:5]
    
    def _extract_market_insights(self, content: str) -> List[str]:
        """Extract market insights from research content."""
        lines = content.split('\n')
        insights = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['market', 'user', 'trend', 'behavior']):
                clean_line = line.strip('- ').strip()
                if len(clean_line) > 20:
                    insights.append(clean_line)
        
        return insights[:5]
    
    def _extract_hiring_advantages(self, content: str) -> List[str]:
        """Extract hiring advantages from career analysis."""
        lines = content.split('\n')
        advantages = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['love', 'impressed', 'value', 'hire']):
                clean_line = line.strip('- ').strip()
                if len(clean_line) > 20:
                    advantages.append(clean_line)
        
        return advantages[:5]
    
    def _extract_skills(self, content: str) -> List[str]:
        """Extract demonstrated skills from career analysis."""
        lines = content.split('\n')
        skills = []
        
        for line in lines:
            if 'skill' in line.lower() or 'demonstrates' in line.lower():
                clean_line = line.strip('- ').strip()
                if len(clean_line) > 15:
                    skills.append(clean_line)
        
        return skills[:5]
    
    def _get_salary_range(self, experience_level: str) -> str:
        """Get salary range based on experience level."""
        ranges = {
            "Entry Level": "2-4 LPA",
            "Intermediate": "6-12 LPA", 
            "Advanced": "15-25 LPA"
        }
        return ranges.get(experience_level, "5-10 LPA")
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate project idea content based on the content type."""
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