"""Research Agent for analyzing existing courses and market trends."""

from typing import Dict, Any, List, Optional
import requests
import json
from langchain_core.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class ResearchAgent(BaseAgent):
    """Agent for researching existing courses, market trends, and learning patterns."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for research analysis."""
        
        course_analysis_template = PromptTemplate(
            input_variables=["existing_courses", "target_topic", "difficulty_level"],
            template="""
            You are a world-class educational researcher specializing in tech courses for Indian learners.
            
            Analyze the following existing courses and identify gaps and opportunities:
            
            Existing Courses: {existing_courses}
            Target Topic: {target_topic}
            Difficulty Level: {difficulty_level}
            
            Provide insights on:
            
            1. **Market Gap Analysis**
               - What's missing in current courses?
               - Unique angles we can take
               - Underserved sub-topics
            
            2. **Indian Context Opportunities**
               - How can we make this more relevant to Indian learners?
               - Local examples, case studies, and companies to reference
               - Cultural context and scenarios
            
            3. **Learning Pattern Analysis**
               - What teaching methods work best for this topic?
               - Common pain points students face
               - Best practices from successful courses
            
            4. **Differentiation Strategy**
               - How to make our course unique and stand out
               - Innovative teaching approaches
               - Practical projects that others don't cover
            
            5. **Content Recommendations**
               - Key topics that must be covered
               - Advanced topics to include for completeness
               - Hands-on projects that will impress employers
            
            Focus on creating something truly unique and valuable for Indian tech students.
            """
        )
        
        market_trends_template = PromptTemplate(
            input_variables=["technology", "industry_context"],
            template="""
            Analyze current market trends and industry demands for {technology}.
            
            Industry Context: {industry_context}
            
            Research and provide:
            
            1. **Current Industry Trends**
               - Latest developments in {technology}
               - Hot topics and emerging technologies
               - What companies are looking for in candidates
            
            2. **Indian Tech Market Specifics**
               - Which Indian companies are using {technology}
               - Salary ranges and career prospects in India
               - Popular tech stacks in Indian startups/MNCs
            
            3. **Learning Path Recommendations**
               - Prerequisites for learning {technology}
               - Logical progression from basics to advanced
               - Integration with other technologies
            
            4. **Real-world Applications**
               - Popular use cases in Indian companies
               - Success stories and case studies
               - Common challenges and solutions
            
            5. **Future Outlook**
               - Where is {technology} heading?
               - Skills that will be valuable in 2-3 years
               - Emerging frameworks and tools
            
            Provide actionable insights for course creation.
            """
        )
        
        competitor_analysis_template = PromptTemplate(
            input_variables=["course_topic", "existing_platforms"],
            template="""
            Conduct competitor analysis for {course_topic} courses.
            
            Existing Platforms Data: {existing_platforms}
            
            Analyze:
            
            1. **Content Gap Analysis**
               - What topics are well-covered vs. poorly covered
               - Common mistakes in existing courses
               - Areas where content is outdated
            
            2. **Teaching Style Analysis**
               - What teaching styles are overused?
               - What approaches are missing?
               - How can we be more engaging and relatable?
            
            3. **Project Quality Assessment**
               - Quality of hands-on projects in existing courses
               - Real-world relevance of assignments
               - Opportunities for better practical learning
            
            4. **Indian Context Integration**
               - How well do existing courses serve Indian learners?
               - Cultural references and examples used
               - Local industry context and relevance
            
            5. **Unique Positioning Opportunities**
               - How can we position our course differently?
               - What unique value proposition can we offer?
               - Target audience segments that are underserved
            
            Provide specific recommendations for our course differentiation.
            """
        )
        
        return {
            "course_analysis": course_analysis_template,
            "market_trends": market_trends_template,
            "competitor_analysis": competitor_analysis_template
        }
    
    def analyze_existing_courses(self, target_topic: str, difficulty_level: str, 
                               api_base_url: str = None) -> Dict[str, Any]:
        """Analyze existing courses from the API to understand current offerings.
        
        Args:
            target_topic: The topic for the new course
            difficulty_level: Target difficulty level
            api_base_url: Base URL for the courses API
            
        Returns:
            Analysis of existing courses and recommendations
        """
        # Fetch existing courses data
        existing_courses = self._fetch_existing_courses(api_base_url)
        
        # Analyze the courses
        result = self.generate_content(
            "course_analysis",
            existing_courses=json.dumps(existing_courses, indent=2),
            target_topic=target_topic,
            difficulty_level=difficulty_level
        )
        
        return {
            "analysis": result["generated_content"],
            "raw_data": existing_courses,
            "recommendations": self._extract_recommendations(result["generated_content"])
        }
    
    def research_market_trends(self, technology: str, industry_context: str = "Indian tech industry") -> Dict[str, Any]:
        """Research current market trends for a technology.
        
        Args:
            technology: Technology to research
            industry_context: Industry context for the research
            
        Returns:
            Market trends analysis and insights
        """
        result = self.generate_content(
            "market_trends",
            technology=technology,
            industry_context=industry_context
        )
        
        return {
            "trends": result["generated_content"],
            "key_insights": self._extract_key_insights(result["generated_content"]),
            "recommendations": self._extract_recommendations(result["generated_content"])
        }
    
    def analyze_competitors(self, course_topic: str, existing_platforms: List[str] = None) -> Dict[str, Any]:
        """Analyze competitor courses and platforms.
        
        Args:
            course_topic: Topic to analyze
            existing_platforms: List of platform data or descriptions
            
        Returns:
            Competitor analysis with differentiation opportunities
        """
        platforms_data = existing_platforms or ["Udemy", "Coursera", "edX", "YouTube tutorials"]
        
        result = self.generate_content(
            "competitor_analysis",
            course_topic=course_topic,
            existing_platforms=json.dumps(platforms_data, indent=2)
        )
        
        return {
            "analysis": result["generated_content"],
            "differentiation_opportunities": self._extract_differentiation_opportunities(result["generated_content"]),
            "recommendations": self._extract_recommendations(result["generated_content"])
        }
    
    def comprehensive_research(self, course_name: str, technology: str, 
                             difficulty_level: str, api_base_url: str = None) -> Dict[str, Any]:
        """Conduct comprehensive research for course creation.
        
        Args:
            course_name: Name of the course to create
            technology: Primary technology focus
            difficulty_level: Target difficulty level
            api_base_url: API base URL for existing courses
            
        Returns:
            Comprehensive research report with all insights
        """
        self.logger.info(f"Starting comprehensive research for {course_name}")
        
        # Analyze existing courses
        course_analysis = self.analyze_existing_courses(technology, difficulty_level, api_base_url)
        
        # Research market trends
        market_trends = self.research_market_trends(technology)
        
        # Analyze competitors
        competitor_analysis = self.analyze_competitors(technology)
        
        # Compile comprehensive report
        research_report = {
            "course_name": course_name,
            "technology": technology,
            "difficulty_level": difficulty_level,
            "research_date": self._get_timestamp(),
            "course_analysis": course_analysis,
            "market_trends": market_trends,
            "competitor_analysis": competitor_analysis,
            "key_recommendations": self._compile_key_recommendations(
                course_analysis, market_trends, competitor_analysis
            )
        }
        
        self.logger.info(f"Research completed for {course_name}")
        return research_report
    
    def _fetch_existing_courses(self, api_base_url: str = None) -> List[Dict[str, Any]]:
        """Fetch existing courses from the API."""
        if not api_base_url:
            api_base_url = "https://tbe-dev-git-development-tbe.vercel.app/api/v1/shiksha"
        
        try:
            response = requests.get(api_base_url, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Failed to fetch courses: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error fetching courses: {str(e)}")
            return []
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from generated content."""
        # Simple extraction - can be enhanced with better parsing
        lines = content.split('\n')
        recommendations = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'must']):
                recommendations.append(line.strip())
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """Extract key insights from content."""
        lines = content.split('\n')
        insights = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['trend', 'insight', 'key', 'important']):
                insights.append(line.strip())
        
        return insights[:8]  # Top 8 insights
    
    def _extract_differentiation_opportunities(self, content: str) -> List[str]:
        """Extract differentiation opportunities from content."""
        lines = content.split('\n')
        opportunities = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['unique', 'different', 'opportunity', 'gap']):
                opportunities.append(line.strip())
        
        return opportunities[:6]  # Top 6 opportunities
    
    def _compile_key_recommendations(self, course_analysis: Dict, market_trends: Dict, 
                                   competitor_analysis: Dict) -> List[str]:
        """Compile key recommendations from all research components."""
        all_recommendations = []
        
        all_recommendations.extend(course_analysis.get("recommendations", []))
        all_recommendations.extend(market_trends.get("recommendations", []))
        all_recommendations.extend(competitor_analysis.get("recommendations", []))
        
        # Remove duplicates and return top recommendations
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        return unique_recommendations[:15]  # Top 15 unique recommendations
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate research content based on the content type."""
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
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()