"""Sheet Researcher Agent - Researches interview topics and market trends."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class SheetResearcher(BaseAgent):
    """Agent for researching interview topics and market trends."""
    
    def __init__(self, **kwargs):
        """Initialize the researcher with moderate temperature for research."""
        super().__init__(temperature=0.7, **kwargs)  # Moderate temperature for research
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for research."""
        
        analyze_topic_template = PromptTemplate(
            input_variables=["topic", "description"],
            template="""
You are an expert tech industry researcher with deep knowledge of the Indian tech market and interview trends.

**Topic:** {topic}
**Description:** {description}

Research and analyze this interview topic to provide:

## Market Analysis

**Current Industry Demand:**
- [High/Medium/Low] demand in Indian tech industry
- [Specific companies and roles that need this skill]
- [Salary ranges and career progression]

**Technology Trends:**
- [Current trends and adoption rates]
- [Emerging technologies in this space]
- [Future outlook (1-3 years)]

## Interview Landscape

**Question Categories:**
- [Fundamental concepts commonly asked]
- [Advanced topics for senior roles]
- [Practical implementation questions]
- [System design considerations]

**Difficulty Distribution:**
- [Easy questions - 30%]
- [Medium questions - 50%]
- [Hard questions - 20%]

**Company-Specific Patterns:**
- [FAANG companies focus areas]
- [Indian startups specific needs]
- [MNCs and service companies]
- [Product vs service company differences]

## Content Strategy

**Key Focus Areas:**
- [Most important concepts to cover]
- [Common interview pitfalls]
- [Success strategies]

**Real-world Applications:**
- [How companies use this technology]
- [Indian context and examples]
- [Industry-specific use cases]

**Competitive Analysis:**
- [What other platforms cover]
- [Gaps in existing content]
- [Unique value propositions]

## Recommendations

**Content Priorities:**
1. [First priority]
2. [Second priority]
3. [Third priority]

**Target Audience:**
- [Primary audience]
- [Secondary audience]
- [Experience levels]

**Success Metrics:**
- [How to measure content effectiveness]
- [Student success indicators]
"""
        )
        
        comprehensive_research_template = PromptTemplate(
            input_variables=["topic"],
            template="""
You are conducting comprehensive research on {topic} for interview preparation content.

Provide a detailed research report covering:

## Industry Overview

**Market Size and Growth:**
- [Market size and growth rate]
- [Key players and companies]
- [Regional distribution in India]

**Technology Evolution:**
- [Historical development]
- [Current state of the art]
- [Future roadmap and trends]

## Interview Preparation Needs

**Skill Requirements:**
- [Core skills needed]
- [Advanced skills for senior roles]
- [Soft skills and communication]

**Common Interview Formats:**
- [Technical screening]
- [Coding challenges]
- [System design discussions]
- [Behavioral questions]

**Success Patterns:**
- [What successful candidates do]
- [Common failure points]
- [Preparation strategies]

## Content Opportunities

**Gaps in Existing Content:**
- [What's missing from current resources]
- [Underserved topics]
- [Quality improvement opportunities]

**Unique Value Propositions:**
- [What makes our content different]
- [Indian context advantages]
- [Real-world application focus]

## Strategic Recommendations

**Content Strategy:**
- [Recommended approach]
- [Key differentiators]
- [Success metrics]

**Implementation Plan:**
- [Phase 1 priorities]
- [Phase 2 expansion]
- [Long-term vision]
"""
        )
        
        return {
            "analyze_topic": analyze_topic_template,
            "comprehensive_research": comprehensive_research_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "analyze_topic":
            return self.analyze_topic(
                topic=kwargs.get("topic"),
                description=kwargs.get("description", "")
            )
        elif content_type == "comprehensive_research":
            return self.comprehensive_research(
                topic=kwargs.get("topic")
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def analyze_topic(self, topic: str, description: str = "") -> Dict[str, Any]:
        """Analyze a specific interview topic."""
        self.logger.info(f"Analyzing topic: {topic}")
        
        prompt = self._format_prompt("analyze_topic",
                                   topic=topic,
                                   description=description)
        
        analysis_result = self._generate_with_prompt(prompt)
        
        # Parse analysis result
        parsed_analysis = self._parse_analysis_result(analysis_result)
        
        return {
            "status": "success",
            "analysis": parsed_analysis,
            "raw_analysis": analysis_result
        }
    
    def comprehensive_research(self, topic: str) -> Dict[str, Any]:
        """Conduct comprehensive research on a topic."""
        self.logger.info(f"Conducting comprehensive research on: {topic}")
        
        prompt = self._format_prompt("comprehensive_research",
                                   topic=topic)
        
        research_result = self._generate_with_prompt(prompt)
        
        # Parse research result
        parsed_research = self._parse_research_result(research_result)
        
        return {
            "status": "success",
            "research": parsed_research,
            "raw_research": research_result
        }
    
    def analyze_market_trends(self, topic: str) -> Dict[str, Any]:
        """Analyze market trends for a specific topic."""
        self.logger.info(f"Analyzing market trends for: {topic}")
        
        trends_prompt = f"""
Analyze current market trends for {topic} in the Indian tech industry:

1. **Demand Trends:**
   - Current demand level
   - Growth trajectory
   - Regional variations

2. **Salary Trends:**
   - Entry-level salaries
   - Mid-level salaries
   - Senior-level salaries

3. **Company Preferences:**
   - FAANG companies
   - Indian startups
   - MNCs
   - Service companies

4. **Skill Evolution:**
   - Emerging skills
   - Obsolete skills
   - Future requirements

5. **Interview Trends:**
   - Question patterns
   - Difficulty levels
   - Focus areas

Provide specific data and insights.
"""
        
        trends_result = self._generate_with_prompt(trends_prompt)
        
        return {
            "status": "success",
            "trends": self._parse_trends_result(trends_result),
            "raw_trends": trends_result
        }
    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """Parse analysis result into structured format."""
        analysis = {
            "market_demand": "Medium",
            "technology_trends": [],
            "question_categories": [],
            "difficulty_distribution": {},
            "company_patterns": {},
            "focus_areas": [],
            "real_world_applications": [],
            "content_priorities": [],
            "target_audience": [],
            "success_metrics": []
        }
        
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "Current Industry Demand:" in line:
                current_section = "market_demand"
            elif "Technology Trends:" in line:
                current_section = "technology_trends"
            elif "Question Categories:" in line:
                current_section = "question_categories"
            elif "Difficulty Distribution:" in line:
                current_section = "difficulty_distribution"
            elif "Company-Specific Patterns:" in line:
                current_section = "company_patterns"
            elif "Key Focus Areas:" in line:
                current_section = "focus_areas"
            elif "Real-world Applications:" in line:
                current_section = "real_world_applications"
            elif "Content Priorities:" in line:
                current_section = "content_priorities"
            elif "Target Audience:" in line:
                current_section = "target_audience"
            elif "Success Metrics:" in line:
                current_section = "success_metrics"
            
            elif line.startswith('-') and current_section:
                item = line.lstrip('- ').strip()
                if item and current_section in analysis:
                    if isinstance(analysis[current_section], list):
                        analysis[current_section].append(item)
                    else:
                        analysis[current_section] = item
        
        return analysis
    
    def _parse_research_result(self, research_text: str) -> Dict[str, Any]:
        """Parse research result into structured format."""
        research = {
            "market_size": "Unknown",
            "growth_rate": "Unknown",
            "key_players": [],
            "technology_evolution": [],
            "skill_requirements": [],
            "interview_formats": [],
            "success_patterns": [],
            "content_gaps": [],
            "unique_value_props": [],
            "strategic_recommendations": []
        }
        
        lines = research_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "Market Size and Growth:" in line:
                current_section = "market_size"
            elif "Technology Evolution:" in line:
                current_section = "technology_evolution"
            elif "Skill Requirements:" in line:
                current_section = "skill_requirements"
            elif "Common Interview Formats:" in line:
                current_section = "interview_formats"
            elif "Success Patterns:" in line:
                current_section = "success_patterns"
            elif "Gaps in Existing Content:" in line:
                current_section = "content_gaps"
            elif "Unique Value Propositions:" in line:
                current_section = "unique_value_props"
            elif "Strategic Recommendations:" in line:
                current_section = "strategic_recommendations"
            
            elif line.startswith('-') and current_section:
                item = line.lstrip('- ').strip()
                if item and current_section in research:
                    if isinstance(research[current_section], list):
                        research[current_section].append(item)
                    else:
                        research[current_section] = item
        
        return research
    
    def _parse_trends_result(self, trends_text: str) -> Dict[str, Any]:
        """Parse trends result into structured format."""
        trends = {
            "demand_trends": {},
            "salary_trends": {},
            "company_preferences": {},
            "skill_evolution": {},
            "interview_trends": {}
        }
        
        lines = trends_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "Demand Trends:" in line:
                current_section = "demand_trends"
            elif "Salary Trends:" in line:
                current_section = "salary_trends"
            elif "Company Preferences:" in line:
                current_section = "company_preferences"
            elif "Skill Evolution:" in line:
                current_section = "skill_evolution"
            elif "Interview Trends:" in line:
                current_section = "interview_trends"
            
            elif line.startswith('-') and current_section:
                item = line.lstrip('- ').strip()
                if item and current_section in trends:
                    if isinstance(trends[current_section], list):
                        trends[current_section].append(item)
                    else:
                        trends[current_section] = item
        
        return trends 