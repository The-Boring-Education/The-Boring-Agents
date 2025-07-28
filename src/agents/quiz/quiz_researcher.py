"""Quiz Researcher Agent - Researches topics and best practices for quiz generation."""

import json
from typing import Dict, List, Any
from langchain.prompts import PromptTemplate
from rich.console import Console

from ...core.base_agent import BaseAgent
from ...core.config import config
from .types import QuizTopic, QuizDifficulty

console = Console()


class QuizResearcher(BaseAgent):
    """Agent responsible for researching quiz topics and best practices."""
    
    def __init__(self, **kwargs):
        """Initialize the Quiz Researcher Agent."""
        super().__init__(**kwargs)
        self.logger.info("Quiz Researcher Agent initialized")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for quiz research."""
        return {
            "research_topic": PromptTemplate(
                input_variables=["topic", "difficulty_level"],
                template="""You are an expert in creating technical quizzes for {topic}.

Research and analyze the following aspects for creating effective quiz questions:

Topic: {topic}
Target Difficulty: {difficulty_level}

Please provide:

1. **Core Concepts** (10-15 key concepts that must be covered)
   - List the most important concepts for this topic
   - Indicate which are fundamental vs advanced

2. **Common Misconceptions**
   - List 5-7 common misconceptions students have about {topic}
   - These make great quiz questions

3. **Real-World Applications**
   - Provide 5 practical scenarios where {topic} knowledge is applied
   - These help create scenario-based questions

4. **Best Practices to Test**
   - List 5-7 best practices that developers should know
   - These make good "which is the best approach" questions

5. **Common Pitfalls**
   - List 5 common mistakes developers make with {topic}
   - These make good "what's wrong with this code" questions

6. **Question Type Recommendations**
   - Suggest the best mix of question types for {topic}:
     * Conceptual understanding
     * Code analysis
     * Debug/Fix errors
     * Best practice selection
     * Real-world scenarios

7. **Difficulty Distribution**
   - Recommend how to distribute questions across difficulty levels
   - What makes a question easy, medium, or hard for {topic}

Format your response as a structured analysis that will guide quiz creation."""
            ),
            
            "analyze_learning_objectives": PromptTemplate(
                input_variables=["topic", "target_audience"],
                template="""Analyze the learning objectives for a {topic} quiz targeting {target_audience}.

Create a comprehensive list of learning objectives that the quiz should assess:

1. **Knowledge-Level Objectives** (Remember & Understand)
   - What facts and concepts should learners recall?
   - What terminology should they understand?

2. **Application-Level Objectives** (Apply & Analyze)
   - What skills should they be able to demonstrate?
   - What problems should they solve?

3. **Evaluation-Level Objectives** (Evaluate & Create)
   - What judgments should they make?
   - What solutions should they design?

For each objective, suggest:
- The type of quiz question that best assesses it
- The difficulty level appropriate for {target_audience}
- Example question patterns

Provide your analysis in a structured format."""
            ),
            
            "research_question_patterns": PromptTemplate(
                input_variables=["topic"],
                template="""Research effective quiz question patterns for {topic}.

Analyze and provide:

1. **Effective Question Patterns**
   For each pattern, provide:
   - Pattern name and description
   - When to use this pattern
   - Example question using this pattern for {topic}
   - Why this pattern is effective

2. **Question Variety Matrix**
   Create a matrix showing:
   - Question type vs Difficulty level
   - Recommended count for each combination
   - Example for each cell

3. **Distractors Strategy**
   For multiple choice questions about {topic}:
   - How to create believable wrong answers
   - Common mistakes that make good distractors
   - Patterns to avoid (too obvious, too tricky)

4. **Explanation Guidelines**
   - What makes a good explanation for {topic} questions
   - How detailed should explanations be
   - When to include code examples
   - How to reference documentation

Provide concrete examples for each recommendation."""
            ),
            
            "competitive_analysis": PromptTemplate(
                input_variables=["topic"],
                template="""Analyze existing quiz platforms and their approach to {topic} questions.

Research and provide insights on:

1. **Industry Standards**
   - How do platforms like LeetCode, HackerRank, Pluralsight handle {topic} quizzes?
   - What question formats work best?
   - What difficulty progression do they use?

2. **Engagement Patterns**
   - What types of questions get the most engagement?
   - What difficulty levels have the best completion rates?
   - How long should a {topic} quiz be?

3. **Quality Indicators**
   - What makes a high-quality quiz question?
   - How to ensure questions are unambiguous?
   - How to validate question difficulty?

4. **Indian Market Considerations**
   - What {topic} concepts are most relevant for Indian developers?
   - Which frameworks/tools are popular in Indian companies?
   - What skill levels to target?

5. **Unique Value Propositions**
   - What gaps exist in current {topic} quizzes?
   - How can we make our quizzes more practical?
   - What would make developers choose our quizzes?

Provide actionable recommendations based on this analysis."""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate research content for quiz creation."""
        if content_type == "research_topic":
            return self.research_topic(
                kwargs.get("topic", ""),
                kwargs.get("difficulty_level", "mixed")
            )
        elif content_type == "analyze_objectives":
            return self.analyze_learning_objectives(
                kwargs.get("topic", ""),
                kwargs.get("target_audience", "developers")
            )
        elif content_type == "research_patterns":
            return self.research_question_patterns(kwargs.get("topic", ""))
        elif content_type == "competitive_analysis":
            return self.competitive_analysis(kwargs.get("topic", ""))
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}
    
    def research_topic(self, topic: str, difficulty_level: str = "mixed") -> Dict[str, Any]:
        """Research a topic for quiz generation."""
        console.print(f"[blue]🔍 Researching {topic} for quiz generation...[/blue]")
        
        try:
            prompt = self._format_prompt("research_topic", 
                                       topic=topic,
                                       difficulty_level=difficulty_level)
            
            research_content = self._generate_with_prompt(prompt)
            
            return {
                "status": "success",
                "topic": topic,
                "difficulty_level": difficulty_level,
                "research": research_content,
                "core_concepts": self._extract_core_concepts(research_content),
                "misconceptions": self._extract_misconceptions(research_content),
                "best_practices": self._extract_best_practices(research_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error researching topic: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to research topic: {str(e)}"
            }
    
    def analyze_learning_objectives(self, topic: str, target_audience: str = "developers") -> Dict[str, Any]:
        """Analyze learning objectives for a quiz topic."""
        console.print(f"[blue]📚 Analyzing learning objectives for {topic}...[/blue]")
        
        try:
            prompt = self._format_prompt("analyze_learning_objectives",
                                       topic=topic,
                                       target_audience=target_audience)
            
            objectives_content = self._generate_with_prompt(prompt)
            
            return {
                "status": "success",
                "topic": topic,
                "target_audience": target_audience,
                "objectives": objectives_content,
                "summary": self._summarize_objectives(objectives_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing objectives: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to analyze objectives: {str(e)}"
            }
    
    def research_question_patterns(self, topic: str) -> Dict[str, Any]:
        """Research effective question patterns for a topic."""
        console.print(f"[blue]🎯 Researching question patterns for {topic}...[/blue]")
        
        try:
            prompt = self._format_prompt("research_question_patterns", topic=topic)
            patterns_content = self._generate_with_prompt(prompt)
            
            return {
                "status": "success",
                "topic": topic,
                "patterns": patterns_content,
                "recommended_patterns": self._extract_patterns(patterns_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error researching patterns: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to research patterns: {str(e)}"
            }
    
    def competitive_analysis(self, topic: str) -> Dict[str, Any]:
        """Analyze competitive landscape for quiz topics."""
        console.print(f"[blue]🏆 Analyzing competitive landscape for {topic} quizzes...[/blue]")
        
        try:
            prompt = self._format_prompt("competitive_analysis", topic=topic)
            analysis_content = self._generate_with_prompt(prompt)
            
            return {
                "status": "success",
                "topic": topic,
                "analysis": analysis_content,
                "recommendations": self._extract_recommendations(analysis_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error in competitive analysis: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed competitive analysis: {str(e)}"
            }
    
    def comprehensive_research(self, topic: str, target_audience: str = "developers") -> Dict[str, Any]:
        """Conduct comprehensive research for quiz generation."""
        console.print(f"[green]🚀 Conducting comprehensive research for {topic} quiz...[/green]")
        
        results = {
            "topic": topic,
            "target_audience": target_audience,
            "research_sections": {}
        }
        
        # 1. Research the topic
        topic_research = self.research_topic(topic)
        if topic_research.get("status") == "success":
            results["research_sections"]["topic_analysis"] = topic_research
        
        # 2. Analyze learning objectives
        objectives = self.analyze_learning_objectives(topic, target_audience)
        if objectives.get("status") == "success":
            results["research_sections"]["learning_objectives"] = objectives
        
        # 3. Research question patterns
        patterns = self.research_question_patterns(topic)
        if patterns.get("status") == "success":
            results["research_sections"]["question_patterns"] = patterns
        
        # 4. Competitive analysis
        competition = self.competitive_analysis(topic)
        if competition.get("status") == "success":
            results["research_sections"]["competitive_analysis"] = competition
        
        # Compile insights
        results["compiled_insights"] = self._compile_research_insights(results["research_sections"])
        results["status"] = "success"
        
        console.print(f"[green]✅ Research complete for {topic}![/green]")
        return results
    
    def _extract_core_concepts(self, content: str) -> List[str]:
        """Extract core concepts from research content."""
        # Simple extraction - in production, use NLP
        concepts = []
        lines = content.split('\n')
        in_concepts = False
        
        for line in lines:
            if "Core Concepts" in line:
                in_concepts = True
                continue
            elif in_concepts and line.strip().startswith('-'):
                concept = line.strip().lstrip('- ').split('(')[0].strip()
                if concept:
                    concepts.append(concept)
            elif in_concepts and line.strip() and not line.startswith(' '):
                break
                
        return concepts[:15]  # Limit to 15 concepts
    
    def _extract_misconceptions(self, content: str) -> List[str]:
        """Extract common misconceptions from research content."""
        misconceptions = []
        lines = content.split('\n')
        in_section = False
        
        for line in lines:
            if "Common Misconceptions" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('-'):
                misconception = line.strip().lstrip('- ')
                if misconception:
                    misconceptions.append(misconception)
            elif in_section and line.strip() and not line.startswith(' '):
                break
                
        return misconceptions[:7]  # Limit to 7
    
    def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices from research content."""
        practices = []
        lines = content.split('\n')
        in_section = False
        
        for line in lines:
            if "Best Practices" in line:
                in_section = True
                continue
            elif in_section and line.strip().startswith('-'):
                practice = line.strip().lstrip('- ')
                if practice:
                    practices.append(practice)
            elif in_section and line.strip() and not line.startswith(' '):
                break
                
        return practices[:7]  # Limit to 7
    
    def _summarize_objectives(self, content: str) -> Dict[str, List[str]]:
        """Summarize learning objectives by level."""
        summary = {
            "knowledge": [],
            "application": [],
            "evaluation": []
        }
        
        # Simple extraction based on sections
        lines = content.split('\n')
        current_level = None
        
        for line in lines:
            if "Knowledge-Level" in line:
                current_level = "knowledge"
            elif "Application-Level" in line:
                current_level = "application"
            elif "Evaluation-Level" in line:
                current_level = "evaluation"
            elif current_level and line.strip().startswith('-'):
                objective = line.strip().lstrip('- ')
                if objective:
                    summary[current_level].append(objective)
        
        return summary
    
    def _extract_patterns(self, content: str) -> List[Dict[str, str]]:
        """Extract question patterns from research."""
        patterns = []
        lines = content.split('\n')
        current_pattern = None
        
        for line in lines:
            if "Pattern:" in line or line.strip().endswith("Pattern"):
                if current_pattern:
                    patterns.append(current_pattern)
                current_pattern = {
                    "name": line.replace("Pattern:", "").strip(),
                    "description": "",
                    "when_to_use": "",
                    "example": ""
                }
            elif current_pattern:
                if "Description:" in line:
                    current_pattern["description"] = line.split("Description:")[1].strip()
                elif "When to use:" in line:
                    current_pattern["when_to_use"] = line.split("When to use:")[1].strip()
                elif "Example:" in line:
                    current_pattern["example"] = line.split("Example:")[1].strip()
        
        if current_pattern:
            patterns.append(current_pattern)
            
        return patterns[:10]  # Limit to 10 patterns
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract recommendations from competitive analysis."""
        recommendations = []
        lines = content.split('\n')
        in_recommendations = False
        
        for line in lines:
            if "Recommendations" in line or "recommendations" in line:
                in_recommendations = True
                continue
            elif in_recommendations and line.strip().startswith('-'):
                rec = line.strip().lstrip('- ')
                if rec:
                    recommendations.append(rec)
        
        return recommendations[:10]  # Limit to 10
    
    def _compile_research_insights(self, research_sections: Dict[str, Any]) -> Dict[str, Any]:
        """Compile insights from all research sections."""
        insights = {
            "key_concepts": [],
            "question_strategies": [],
            "difficulty_guidelines": {},
            "best_practices": []
        }
        
        # Extract from topic analysis
        if "topic_analysis" in research_sections:
            topic_data = research_sections["topic_analysis"]
            insights["key_concepts"] = topic_data.get("core_concepts", [])
            insights["common_misconceptions"] = topic_data.get("misconceptions", [])
            insights["best_practices"] = topic_data.get("best_practices", [])
        
        # Extract from learning objectives
        if "learning_objectives" in research_sections:
            obj_data = research_sections["learning_objectives"]
            insights["learning_objectives"] = obj_data.get("summary", {})
        
        # Extract from question patterns
        if "question_patterns" in research_sections:
            pattern_data = research_sections["question_patterns"]
            insights["question_strategies"] = pattern_data.get("recommended_patterns", [])
        
        # Extract from competitive analysis
        if "competitive_analysis" in research_sections:
            comp_data = research_sections["competitive_analysis"]
            insights["market_insights"] = comp_data.get("recommendations", [])
        
        return insights 