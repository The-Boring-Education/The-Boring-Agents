"""Base answer generator for interview agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent
from src.agents.interview.common.mdx_utils import format_answer_as_mdx


from langchain_core.output_parsers import PydanticOutputParser
from src.agents.interview.models import InterviewQuestionResponse

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
    def _get_output_parser(self) -> Optional[PydanticOutputParser]:
        """Get the output parser for structured generation.
        
        Returns:
            PydanticOutputParser or None
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
    ) -> InterviewQuestionResponse:
        """Generate an answer for an interview question.
        
        Args:
            question: The interview question
            topic: Topic/subject area
            difficulty: Difficulty level
            frequency: How often the question is asked
            priority: Priority level
            company_types: Types of companies that ask this question
            
        Returns:
            InterviewQuestionResponse object
        """
        if company_types is None:
            company_types = ["Startup", "MNC"]
        
        self.logger.info(f"Generating answer for: {question[:50]}...")
        
        # Get prompt template
        prompt_template = self._get_answer_prompt_template()
        
        # Get output parser
        parser = self._get_output_parser()
        format_instructions = parser.get_format_instructions() if parser else ""
        
        # Format prompt with question details
        prompt = prompt_template.format(
            question=question,
            topic=topic,
            difficulty=difficulty,
            frequency=frequency,
            priority=priority,
            company_types=", ".join(company_types) if company_types else "All types",
            format_instructions=format_instructions
        )
        
        # Generate answer using LLM
        raw_answer = self._generate_with_prompt(prompt)
        
        try:
            if parser:
                structured_answer = parser.parse(raw_answer)
                # Normalize response to match database enums
                structured_answer = self._normalize_response(structured_answer)
                self.logger.info("Answer generated, parsed, and normalized successfully")
                return structured_answer
            else:
                return raw_answer
        except Exception as e:
            self.logger.error(f"Failed to parse answer: {e}")
            raise e
            
    def _normalize_response(self, response: InterviewQuestionResponse) -> InterviewQuestionResponse:
        """Normalize response fields to match database enums.
        
        Args:
            response: The parsed InterviewQuestionResponse
            
        Returns:
            Normalized InterviewQuestionResponse
        """
        # 1. Normalize Frequency
        freq_map = {
            "high": "Most Asked",
            "most asked": "Most Asked",
            "most-asked": "Most Asked",
            "medium": "Asked Frequently",
            "asked frequently": "Asked Frequently",
            "frequently": "Asked Frequently",
            "low": "Asked Sometimes",
            "asked sometimes": "Asked Sometimes",
            "sometimes": "Asked Sometimes",
            "uncommon": "Asked Sometimes",
            "rare": "Asked Sometimes"
        }
        
        curr_freq = response.frequency.lower() if response.frequency else ""
        response.frequency = freq_map.get(curr_freq, "Asked Frequently")
        
        # 2. Normalize Priority
        priority_map = {
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "critical": "High",
            "normal": "Medium"
        }
        
        curr_priority = response.priority.lower() if response.priority else ""
        response.priority = priority_map.get(curr_priority, "Medium")
        
        # 3. Ensure difficulty is capitalized correctly
        diff_map = {
            "easy": "Easy",
            "medium": "Medium",
            "hard": "Hard"
        }
        curr_diff = response.difficulty.lower() if response.difficulty else ""
        response.difficulty = diff_map.get(curr_diff, "Medium")
        
        return response
    
    
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

