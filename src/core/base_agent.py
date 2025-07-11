"""Base agent class for all content generation agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging
from langchain.llms.base import LLM
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import BaseOutputParser

from .config import config


class BaseAgent(ABC):
    """Abstract base class for all content generation agents."""
    
    def __init__(self, model_name: Optional[str] = None, **kwargs):
        """Initialize the base agent.
        
        Args:
            model_name: Name of the model to use (defaults to config.default_model)
            **kwargs: Additional arguments for model configuration
        """
        self.model_name = model_name or config.default_model
        self.logger = logging.getLogger(self.__class__.__name__)
        self.model_kwargs = kwargs
        
        # Initialize LLM lazily (only when needed)
        self._llm = None
        
        # Initialize prompt templates (to be overridden by subclasses)
        self.prompt_templates = self._get_prompt_templates()
    
    @property
    def llm(self) -> LLM:
        """Get the language model instance, initializing if needed."""
        if self._llm is None:
            self._llm = self._initialize_llm(**self.model_kwargs)
        return self._llm
    
    def _initialize_llm(self, **kwargs) -> LLM:
        """Initialize the language model based on configuration.
        
        Returns:
            Initialized language model instance
        """
        # Default model settings
        model_kwargs = {
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            **kwargs
        }
        
        # Initialize OpenAI model (can be extended for other providers)
        if config.openai_api_key:
            return ChatOpenAI(
                model_name=self.model_name,
                openai_api_key=config.openai_api_key,
                **model_kwargs
            )
        else:
            raise ValueError("No valid API key found. Please set OPENAI_API_KEY in your environment.")
    
    @abstractmethod
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates specific to this agent.
        
        Returns:
            Dictionary of prompt templates keyed by operation name
        """
        pass
    
    @abstractmethod
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        """Generate content based on the agent's specific purpose.
        
        Args:
            **kwargs: Agent-specific parameters
            
        Returns:
            Generated content as a dictionary
        """
        pass
    
    def _format_prompt(self, template_name: str, **kwargs) -> str:
        """Format a prompt template with given parameters.
        
        Args:
            template_name: Name of the template to use
            **kwargs: Parameters to fill in the template
            
        Returns:
            Formatted prompt string
        """
        if template_name not in self.prompt_templates:
            raise ValueError(f"Template '{template_name}' not found in {self.__class__.__name__}")
        
        template = self.prompt_templates[template_name]
        return template.format(**kwargs)
    
    def _generate_with_prompt(self, prompt: str) -> str:
        """Generate content using the language model with the given prompt.
        
        Args:
            prompt: The formatted prompt string
            
        Returns:
            Generated content
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            raise
    
    def save_content(self, content: Dict[str, Any], filename: str) -> str:
        """Save generated content to a file.
        
        Args:
            content: Content to save
            filename: Name of the file (without extension)
            
        Returns:
            Path to the saved file
        """
        import json
        import os
        
        filepath = os.path.join(config.output_dir, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Content saved to {filepath}")
        return filepath