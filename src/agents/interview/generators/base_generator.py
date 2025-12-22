"""Base answer generator for interview agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent
from src.agents.interview.common.mdx_utils import format_answer_as_mdx


class BaseAnswerGenerator(BaseAgent, ABC):
    """Abstract base class for all answer generators."""
    
    def __init__(self, **kwargs):
        """Initialize the base answer generator."""
        super().__init__(**kwargs)
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates (required by BaseAgent).
        
        Returns:
            Empty dict - subclasses use _get_answer_prompt_template instead
        """
        return {}
    
    @abstractmethod
    def _get_answer_prompt_template(self) -> PromptTemplate:
        """Get the prompt template for answer generation.
        
        Returns:
            PromptTemplate for generating answers
        """
        pass
    
    @abstractmethod
    def _get_answer_structure(self) -> Dict[str, str]:
        """Get the expected answer structure for this generator type.
        
        Returns:
            Dictionary describing required sections in the answer
        """
        pass
    
    def generate_answer(
        self,
        question: str,
        topic: str,
        difficulty: str = "Medium",
        frequency: str = "Asked Sometimes",
        priority: str = "Medium",
        company_types: Optional[List[str]] = None
    ) -> str:
        """Generate an answer for an interview question.
        
        Args:
            question: The interview question
            topic: Topic/subject area
            difficulty: Difficulty level
            frequency: How often the question is asked
            priority: Priority level
            company_types: Types of companies that ask this question
            
        Returns:
            MDX-formatted answer string
        """
        if company_types is None:
            company_types = ["Startup", "MNC"]
        
        self.logger.info(f"Generating answer for: {question[:50]}...")
        
        # Get prompt template
        prompt_template = self._get_answer_prompt_template()
        
        # Format prompt with question details
        prompt = prompt_template.format(
            question=question,
            topic=topic,
            difficulty=difficulty,
            frequency=frequency,
            priority=priority,
            company_types=", ".join(company_types) if company_types else "All types"
        )
        
        # Generate answer using LLM
        raw_answer = self._generate_with_prompt(prompt)
        
        # Apply quality improvements
        improved_answer = self._apply_quality_improvements(
            raw_answer,
            question,
            topic,
            difficulty
        )
        
        # Format as MDX
        mdx_answer = format_answer_as_mdx(improved_answer)
        
        self.logger.info("Answer generated successfully")
        return mdx_answer
    
    def _apply_quality_improvements(
        self,
        answer: str,
        question: str,
        topic: str,
        difficulty: str
    ) -> str:
        """Apply quality improvements to the generated answer.
        
        Args:
            answer: Raw generated answer
            question: Original question
            topic: Topic area
            difficulty: Difficulty level
            
        Returns:
            Improved answer
        """
        # Check for required sections
        required_sections = self._get_answer_structure()
        missing_sections = self._check_missing_sections(answer, required_sections)
        
        if missing_sections:
            answer = self._add_missing_sections(answer, missing_sections, question, topic)
        
        # Ensure proper formatting
        answer = self._ensure_proper_formatting(answer)
        
        return answer
    
    def _check_missing_sections(
        self,
        answer: str,
        required_sections: Dict[str, str]
    ) -> List[str]:
        """Check for missing required sections in the answer.
        
        Args:
            answer: Generated answer
            required_sections: Dictionary of required sections
            
        Returns:
            List of missing section names
        """
        missing = []
        for section_name, section_keyword in required_sections.items():
            if section_keyword.lower() not in answer.lower():
                missing.append(section_name)
        return missing
    
    def _add_missing_sections(
        self,
        answer: str,
        missing_sections: List[str],
        question: str,
        topic: str
    ) -> str:
        """Add missing sections to the answer.
        
        Args:
            answer: Current answer
            missing_sections: List of missing section names
            question: Original question
            topic: Topic area
            
        Returns:
            Answer with missing sections added
        """
        # Default implementation - can be overridden by subclasses
        for section in missing_sections:
            section_content = self._generate_missing_section(section, question, topic)
            answer += f"\n\n{section_content}"
        return answer
    
    def _generate_missing_section(
        self,
        section_name: str,
        question: str,
        topic: str
    ) -> str:
        """Generate content for a missing section.
        
        Args:
            section_name: Name of the section
            question: Original question
            topic: Topic area
            
        Returns:
            Generated section content
        """
        prompt = f"Generate a brief {section_name} section for this interview question: {question}\nTopic: {topic}"
        return self._generate_with_prompt(prompt)
    
    def _ensure_proper_formatting(self, answer: str) -> str:
        """Ensure proper markdown formatting.
        
        Args:
            answer: Answer text
            
        Returns:
            Formatted answer
        """
        # Fix headers - ensure consistent header levels
        answer = answer.replace("###", "#####")
        answer = answer.replace("##", "#####")
        
        # Fix spacing
        answer = answer.replace("\n\n\n", "\n\n")
        
        # Ensure code blocks are properly formatted
        if "```" in answer:
            # Ensure language tags are present
            lines = answer.split('\n')
            formatted_lines = []
            in_code_block = False
            code_language = "text"
            
            for line in lines:
                if line.strip().startswith("```"):
                    if not in_code_block:
                        # Opening code block
                        in_code_block = True
                        # Check if language is specified
                        if len(line.strip()) > 3:
                            code_language = line.strip()[3:].strip()
                        else:
                            code_language = "text"
                        formatted_lines.append(f"```{code_language}")
                    else:
                        # Closing code block
                        in_code_block = False
                        formatted_lines.append("```")
                else:
                    formatted_lines.append(line)
            
            answer = '\n'.join(formatted_lines)
        
        return answer
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type.
        
        Args:
            content_type: Type of content to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated content dictionary
        """
        if content_type == "answer":
            answer = self.generate_answer(
                question=kwargs.get("question", ""),
                topic=kwargs.get("topic", ""),
                difficulty=kwargs.get("difficulty", "Medium"),
                frequency=kwargs.get("frequency", "Asked Sometimes"),
                priority=kwargs.get("priority", "Medium"),
                company_types=kwargs.get("company_types", ["Startup", "MNC"])
            )
            return {
                "status": "success",
                "answer": answer,
                "content_type": "answer"
            }
        else:
            raise ValueError(f"Unknown content type: {content_type}")

