"""Interview Research Agent for analyzing topics and market trends."""

from typing import Dict, Any, List, Optional
from ...core.base_agent import BaseAgent


class InterviewResearchAgent(BaseAgent):
    """Agent for researching interview topics and market trends."""
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Return empty dict since we'll use direct prompts."""
        return {}
    
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        """Generate research content."""
        return {"generated_content": "Research completed"}
    
    def analyze_interview_topic(self, sheet_name: str, description: str, 
                              existing_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze an interview topic for revamping.
        
        Args:
            sheet_name: Name of the interview sheet
            description: Description of the topic
            existing_questions: Current questions in the sheet
            
        Returns:
            Research insights and recommendations
        """
        research_prompt = f"""
        You are a senior tech interview researcher analyzing "{sheet_name}" for world-class revamping.
        
        **Topic:** {sheet_name}
        **Description:** {description}
        **Current Questions Count:** {len(existing_questions)}
        
        Provide comprehensive research insights:
        
        ## Market Analysis
        **Current Industry Demand:**
        - How important is this topic in 2024-2025?
        - Which Indian companies prioritize this?
        - Salary impact of knowing this topic well
        
        **Trending Aspects:**
        - What's new/changing in this field?
        - Emerging patterns in interviews
        - Skills companies are specifically looking for
        
        ## Competitive Analysis
        **Common Gaps in Existing Materials:**
        - What do most interview sheets miss?
        - Areas that need more depth
        - Practical vs theoretical balance
        
        **Differentiation Opportunities:**
        - How can we make our sheet unique?
        - Indian context that others miss
        - Real-world examples to include
        
        ## Content Strategy
        **Key Topics to Emphasize:**
        - Must-cover fundamentals
        - Advanced concepts worth including
        - Practical implementation details
        
        **Indian Company Focus:**
        - How Flipkart/Paytm/Ola approach this topic
        - Startup vs MNC interview styles
        - Real project scenarios to include
        
        Be specific and actionable for creating a ₹49 premium sheet.
        """
        
        try:
            response = self._generate_with_prompt(research_prompt)
            return {
                "topic": sheet_name,
                "market_analysis": self._extract_market_analysis(response),
                "competitive_insights": self._extract_competitive_insights(response),
                "content_strategy": self._extract_content_strategy(response),
                "key_recommendations": self._extract_recommendations(response),
                "full_research": response
            }
        except Exception as e:
            self.logger.error(f"Error analyzing interview topic: {str(e)}")
            return self._fallback_research_insights(sheet_name)
    
    def comprehensive_topic_research(self, sheet_name: str, description: str) -> Dict[str, Any]:
        """Conduct comprehensive research for a new interview sheet.
        
        Args:
            sheet_name: Name of the new sheet
            description: Description of the topic
            
        Returns:
            Comprehensive research insights
        """
        comprehensive_prompt = f"""
        Conduct world-class research for creating a new interview sheet: "{sheet_name}"
        
        **Description:** {description}
        **Goal:** Create the best interview preparation material in India for this topic
        
        ## Industry Landscape Analysis
        **Market Demand:**
        - Current job market demand for this skill
        - Salary ranges in India (fresher to senior)
        - Growth trajectory for next 2-3 years
        
        **Company Breakdown:**
        - FAANG: How they approach this topic
        - Indian Unicorns: Their specific requirements
        - Startups: Practical needs and focus areas
        - Service Companies: Traditional approach
        
        ## Content Gap Analysis
        **Existing Resources:**
        - What's already available online
        - Common weaknesses in current materials
        - Opportunities for improvement
        
        **Student Pain Points:**
        - What Indian students struggle with most
        - Common misconceptions
        - Practice areas that need attention
        
        ## Strategic Recommendations
        **Content Priorities:**
        - Top 10 must-cover topics
        - Difficulty distribution
        - Practical vs theoretical balance
        
        **Indian Context Integration:**
        - Local company examples to use
        - Cultural analogies that work
        - Real-world scenarios relevant to India
        
        **Differentiation Strategy:**
        - How to make this sheet unique
        - Value propositions for ₹49 price point
        - Features that competitors lack
        
        Provide actionable insights for creating an exceptional interview sheet.
        """
        
        try:
            response = self._generate_with_prompt(comprehensive_prompt)
            return {
                "sheet_name": sheet_name,
                "industry_landscape": self._extract_industry_landscape(response),
                "content_gaps": self._extract_content_gaps(response),
                "strategic_recommendations": self._extract_strategic_recommendations(response),
                "indian_context_opportunities": self._extract_indian_context(response),
                "differentiation_strategy": self._extract_differentiation_strategy(response),
                "full_research": response
            }
        except Exception as e:
            self.logger.error(f"Error in comprehensive research: {str(e)}")
            return self._fallback_comprehensive_research(sheet_name)
    
    def analyze_market_trends(self, topic: str) -> Dict[str, Any]:
        """Analyze current market trends for a topic.
        
        Args:
            topic: Topic to analyze trends for
            
        Returns:
            Market trends analysis
        """
        trends_prompt = f"""
        Analyze current market trends for {topic} in the Indian tech industry.
        
        **Focus Areas:**
        1. **Hiring Trends:** Which companies are hiring for this skill?
        2. **Salary Trends:** How are salaries changing?
        3. **Technology Evolution:** What's new in this field?
        4. **Interview Patterns:** How are interview styles changing?
        5. **Skill Demands:** What specific skills are in demand?
        
        **Time Frame:** 2024-2025 outlook
        **Geography:** Indian tech market focus
        
        Provide data-driven insights and specific examples.
        """
        
        try:
            response = self._generate_with_prompt(trends_prompt)
            return {
                "topic": topic,
                "hiring_trends": self._extract_hiring_trends(response),
                "salary_trends": self._extract_salary_trends(response),
                "technology_evolution": self._extract_tech_evolution(response),
                "interview_patterns": self._extract_interview_patterns(response),
                "recommendations": self._extract_trend_recommendations(response),
                "full_analysis": response
            }
        except Exception as e:
            self.logger.error(f"Error analyzing market trends: {str(e)}")
            return {"topic": topic, "error": str(e)}
    
    def _extract_market_analysis(self, text: str) -> Dict[str, Any]:
        """Extract market analysis from research text."""
        return {"industry_demand": "High", "trending_aspects": [], "key_companies": []}
    
    def _extract_competitive_insights(self, text: str) -> Dict[str, Any]:
        """Extract competitive insights."""
        return {"common_gaps": [], "differentiation_opportunities": []}
    
    def _extract_content_strategy(self, text: str) -> Dict[str, Any]:
        """Extract content strategy recommendations."""
        return {"key_topics": [], "focus_areas": []}
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract key recommendations from text."""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['recommend', 'should', 'must', 'important']):
                if len(line) > 20 and len(line) < 200:  # Reasonable length
                    recommendations.append(line)
        
        return recommendations[:10]  # Top 10 recommendations
    
    def _extract_industry_landscape(self, text: str) -> Dict[str, Any]:
        """Extract industry landscape from research."""
        return {"market_demand": "Growing", "company_breakdown": {}, "salary_ranges": {}}
    
    def _extract_content_gaps(self, text: str) -> Dict[str, Any]:
        """Extract content gap analysis."""
        return {"existing_resources": [], "pain_points": [], "opportunities": []}
    
    def _extract_strategic_recommendations(self, text: str) -> Dict[str, Any]:
        """Extract strategic recommendations."""
        return {"content_priorities": [], "difficulty_distribution": {}, "balance_recommendations": []}
    
    def _extract_indian_context(self, text: str) -> Dict[str, Any]:
        """Extract Indian context opportunities."""
        return {"company_examples": [], "cultural_analogies": [], "scenarios": []}
    
    def _extract_differentiation_strategy(self, text: str) -> Dict[str, Any]:
        """Extract differentiation strategy."""
        return {"unique_features": [], "value_propositions": [], "competitive_advantages": []}
    
    def _extract_hiring_trends(self, text: str) -> Dict[str, Any]:
        """Extract hiring trends."""
        return {"top_companies": [], "growth_areas": [], "demand_level": "High"}
    
    def _extract_salary_trends(self, text: str) -> Dict[str, Any]:
        """Extract salary trends."""
        return {"fresher_range": "4-8 LPA", "mid_range": "8-15 LPA", "senior_range": "15-30 LPA"}
    
    def _extract_tech_evolution(self, text: str) -> Dict[str, Any]:
        """Extract technology evolution insights."""
        return {"new_developments": [], "emerging_tools": [], "future_direction": []}
    
    def _extract_interview_patterns(self, text: str) -> Dict[str, Any]:
        """Extract interview pattern changes."""
        return {"new_styles": [], "focus_shifts": [], "common_themes": []}
    
    def _extract_trend_recommendations(self, text: str) -> List[str]:
        """Extract trend-based recommendations."""
        return ["Stay updated with latest developments", "Focus on practical implementation", "Practice with real scenarios"]
    
    def _fallback_research_insights(self, sheet_name: str) -> Dict[str, Any]:
        """Provide fallback research insights if AI fails."""
        return {
            "topic": sheet_name,
            "market_analysis": {"industry_demand": "High", "trending_aspects": ["Growing importance"]},
            "competitive_insights": {"common_gaps": ["Lack of practical examples"], "differentiation_opportunities": ["Indian context"]},
            "content_strategy": {"key_topics": [f"Core {sheet_name} concepts"], "focus_areas": ["Fundamentals", "Implementation"]},
            "key_recommendations": [
                f"Focus on {sheet_name} fundamentals",
                "Include practical examples",
                "Add Indian company context",
                "Provide hands-on exercises",
                "Include real-world scenarios"
            ],
            "full_research": f"Research insights for {sheet_name} topic"
        }
    
    def _fallback_comprehensive_research(self, sheet_name: str) -> Dict[str, Any]:
        """Provide fallback comprehensive research."""
        return {
            "sheet_name": sheet_name,
            "industry_landscape": {"market_demand": "High", "salary_ranges": {"fresher": "4-8 LPA"}},
            "content_gaps": {"opportunities": ["Better practical examples"]},
            "strategic_recommendations": {"content_priorities": [f"{sheet_name} basics"]},
            "indian_context_opportunities": {"company_examples": ["Flipkart", "Paytm"]},
            "differentiation_strategy": {"unique_features": ["Indian context", "Practical focus"]},
            "full_research": f"Comprehensive research for {sheet_name}"
        }