"""Metadata generator for interview sheets and questions."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent
from src.agents.interview.common.schema_utils import (
    INTERVIEW_QUESTION_FREQUENCY,
    PRIORITY_LEVELS,
    COMPANY_TYPES,
    validate_frequency,
    validate_priority,
    validate_company_types
)


class MetadataGenerator(BaseAgent):
    """Generator for sheet and question metadata."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for metadata generation."""
        return {
            "sheet_meta": PromptTemplate(
                input_variables=["name", "description", "roadmap"],
                template="""
Generate comprehensive metadata content for an interview sheet.

**Sheet Name:** {name}
**Description:** {description}
**Roadmap:** {roadmap}

Create engaging metadata that:
1. Summarizes what the sheet covers
2. Highlights key topics and technologies
3. Explains the value for interview preparation
4. Mentions target audience and difficulty level
5. Includes real-world application context

Keep it concise (150-200 words), engaging, and professional.

Metadata:
"""
            ),
            "question_metadata": PromptTemplate(
                input_variables=["question", "topic", "context"],
                template="""
You are an expert interview question analyst with 20+ years of experience in tech hiring. Analyze the following interview question and provide appropriate metadata.

**Question:** {question}
**Topic:** {topic}
**Context:** {context}

Based on your extensive experience, determine:

1. **Frequency**: How often this question is asked in interviews
   - "Most Asked" (asked in 80%+ of interviews)
   - "Asked Frequently" (asked in 50-80% of interviews) 
   - "Asked Sometimes" (asked in 20-50% of interviews)

2. **Priority**: How important this question is for interview success
   - "High" (critical for passing the interview)
   - "Medium" (important but not critical)
   - "Low" (nice to know but not essential)

3. **Company Types**: Which types of companies typically ask this question (can select multiple)
   - "Startup" (early-stage companies, fast-paced)
   - "MidSize" (growing companies, established processes)
   - "MNC" (multinational corporations, formal processes)
   - "FAANG" (top tech companies, high standards)

Provide your analysis in this exact format:
Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
Priority: [High/Medium/Low]
Company Types: [Startup, MidSize, MNC, FAANG] (select relevant ones, comma-separated)
"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "sheet_meta":
            return self.generate_sheet_meta(
                name=kwargs.get("name", ""),
                description=kwargs.get("description", ""),
                roadmap=kwargs.get("roadmap", "Tech")
            )
        elif content_type == "question_metadata":
            return self.generate_question_metadata(
                question=kwargs.get("question", ""),
                topic=kwargs.get("topic", ""),
                context=kwargs.get("context", "")
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def generate_sheet_meta(
        self,
        name: str,
        description: str,
        roadmap: str = "Tech"
    ) -> str:
        """Generate metadata content for a sheet.
        
        Args:
            name: Sheet name
            description: Sheet description
            roadmap: Roadmap type
            
        Returns:
            Generated metadata content
        """
        prompt = self._format_prompt(
            "sheet_meta",
            name=name,
            description=description,
            roadmap=roadmap
        )
        
        meta = self._generate_with_prompt(prompt)
        return meta.strip()
    
    def generate_question_metadata(
        self,
        question: str,
        topic: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """Generate metadata for a question.
        
        Args:
            question: Question text
            topic: Topic area
            context: Additional context
            
        Returns:
            Dictionary with frequency, priority, and companyTypes
        """
        prompt = self._format_prompt(
            "question_metadata",
            question=question,
            topic=topic,
            context=context
        )
        
        result = self._generate_with_prompt(prompt)
        metadata = self._parse_metadata_result(result)
        
        # Validate enum values
        if not validate_frequency(metadata["frequency"]):
            metadata["frequency"] = "Asked Sometimes"
        
        if not validate_priority(metadata["priority"]):
            metadata["priority"] = "Medium"
        
        if not validate_company_types(metadata["companyTypes"]):
            metadata["companyTypes"] = ["Startup", "MNC"]
        
        return metadata
    
    def _parse_metadata_result(self, result: str) -> Dict[str, Any]:
        """Parse metadata from AI response.
        
        Args:
            result: AI response text
            
        Returns:
            Parsed metadata dictionary
        """
        metadata = {
            "frequency": "Asked Sometimes",
            "priority": "Medium",
            "companyTypes": ["Startup", "MNC"]
        }
        
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "frequency":
                    # Validate and set frequency
                    if value in INTERVIEW_QUESTION_FREQUENCY:
                        metadata["frequency"] = value
                elif key == "priority":
                    # Validate and set priority
                    if value in PRIORITY_LEVELS:
                        metadata["priority"] = value
                elif key == "company types":
                    # Parse comma-separated company types
                    company_types = [ct.strip() for ct in value.split(',')]
                    # Filter to only valid types
                    valid_types = [ct for ct in company_types if ct in COMPANY_TYPES]
                    if valid_types:
                        metadata["companyTypes"] = valid_types
        
        return metadata

