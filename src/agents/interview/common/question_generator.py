"""Question generator for interview sheets."""

from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent
from src.agents.interview.types import AnswerAgentType
from src.agents.interview.common.schema_utils import generate_slug


class QuestionGenerator(BaseAgent):
    """Generator for interview questions based on agent type."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for question generation."""
        return {
            "generate_questions": PromptTemplate(
                input_variables=["name", "description", "agent_type", "question_count", "roadmap"],
                template="""
You are an expert interview question generator for The Boring Education. Generate comprehensive interview questions based on the following requirements.

**Sheet Name:** {name}
**Description:** {description}
**Agent Type:** {agent_type}
**Question Count:** {question_count}
**Roadmap:** {roadmap}

Based on the requirements, generate a comprehensive list of interview questions that:
1. Cover all the topics mentioned in the description
2. Follow the difficulty distribution (Easy/Medium/Hard)
3. Are relevant for Indian tech companies and job market
4. Include practical, real-world scenarios
5. Test both conceptual understanding and implementation skills
6. Are suitable for the target audience mentioned
7. Match the style of {agent_type} questions

For {agent_type} questions:
- Generic: Focus on aptitude, reasoning, and basic concepts
- DSA: Include stepwise problems, real-world examples, not pure Leetcode style
- Tech: Include code examples and technology-specific concepts
- System Design: Focus on reasoning, architecture, and scalability

Please generate questions in a numbered list format:
1. [Question 1]
2. [Question 2]
3. [Question 3]
...and so on

Generate exactly {question_count} questions covering all the topics comprehensively. Make sure questions are:
- Clear and specific
- Interview-appropriate
- Practical and job-relevant
- Covering different difficulty levels
- Technology-specific where applicable

Questions:
"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "generate_questions":
            return self.generate_questions(
                name=kwargs.get("name", ""),
                description=kwargs.get("description", ""),
                agent_type=kwargs.get("agent_type", "generic"),
                question_count=kwargs.get("question_count", 20),
                roadmap=kwargs.get("roadmap", "Tech")
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def generate_questions(
        self,
        name: str,
        description: str,
        agent_type: str,
        question_count: int = 20,
        roadmap: str = "Tech"
    ) -> List[str]:
        """Generate questions for an interview sheet.
        
        Args:
            name: Sheet name
            description: Sheet description
            agent_type: Agent type (generic, dsa, tech, system_design)
            question_count: Number of questions to generate
            roadmap: Roadmap type
            
        Returns:
            List of question strings
        """
        prompt = self._format_prompt(
            "generate_questions",
            name=name,
            description=description,
            agent_type=agent_type,
            question_count=question_count,
            roadmap=roadmap
        )
        
        result = self._generate_with_prompt(prompt)
        questions = self._parse_questions(result, question_count)
        
        return questions
    
    def _parse_questions(self, questions_text: str, max_questions: int) -> List[str]:
        """Parse questions from generated text.
        
        Args:
            questions_text: Generated questions text
            max_questions: Maximum number of questions to return
            
        Returns:
            List of parsed questions
        """
        questions = []
        lines = questions_text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered questions
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering/bullets
                question = line
                # Remove leading number and period/bullet
                if line[0].isdigit():
                    # Find the first period or space after number
                    for i, char in enumerate(line):
                        if char in ['.', ')', '-'] and i > 0:
                            question = line[i+1:].strip()
                            break
                elif line.startswith('-'):
                    question = line[1:].strip()
                
                if question and len(question) > 10:  # Basic validation
                    questions.append(question)
                    if len(questions) >= max_questions:
                        break
        
        return questions[:max_questions]

