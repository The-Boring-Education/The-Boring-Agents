"""Metadata generator for quiz categories."""

from typing import Dict, Any
from langchain_core.prompts import PromptTemplate
import json
import logging

from src.core.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class QuizMetadataGenerator(BaseAgent):
    """Generator for quiz category metadata (name, description, icon)."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for metadata generation."""
        return {
            "generate_category_metadata": PromptTemplate(
                input_variables=["topic", "question_count", "target_audience"],
                template="""
                Generate metadata for a {topic} quiz category.

                Topic: {topic}
                Question Count: {question_count}
                Target Audience: {target_audience}

                Provide:
                1. **Category Name**: Display name for the quiz (should be the topic name or a variation)
                2. **Category Description**: Engaging description (2-3 sentences) that:
                - Explains what the quiz covers
                - Mentions the target audience
                - Highlights key learning outcomes
                - Makes it appealing to take
                3. **Category Icon**: Suggest an appropriate emoji or icon name (single emoji preferred)

                Format as JSON:
                {{
                    "categoryName": "Display Name",
                    "categoryDescription": "Description here",
                    "categoryIcon": "🎯"
                }}

                Keep the description concise (100-150 words), engaging, and professional.
                """
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate metadata content."""
        if content_type == "generate_category_metadata":
            return self.generate_category_metadata(
                topic=kwargs.get("topic", ""),
                question_count=kwargs.get("question_count", 20),
                target_audience=kwargs.get("target_audience", "developers")
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def generate_category_metadata(
        self,
        topic: str,
        question_count: int = 20,
        target_audience: str = "developers"
    ) -> Dict[str, Any]:
        """Generate category metadata for a quiz.
        
        Args:
            topic: Quiz topic
            question_count: Number of questions in the quiz
            target_audience: Target audience
            
        Returns:
            Dictionary with categoryName, categoryDescription, categoryIcon
        """
        prompt = self._format_prompt(
            "generate_category_metadata",
            topic=topic,
            question_count=question_count,
            target_audience=target_audience
        )
        
        response = self._generate_with_prompt(prompt)
        metadata = self._parse_json_response(response)
        
        if not metadata:
            # Fallback to defaults
            logger.warning(f"Failed to parse metadata, using defaults for {topic}")
            metadata = self._get_default_metadata(topic)
        
        # Validate and normalize
        metadata = self._validate_metadata(metadata, topic)
        
        return metadata
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response."""
        try:
            # Find JSON block in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            logger.debug(f"Response: {response[:500]}...")
            return None
    
    def _validate_metadata(self, metadata: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Validate and normalize metadata."""
        # Ensure all required fields
        if "categoryName" not in metadata:
            metadata["categoryName"] = topic
        
        if "categoryDescription" not in metadata:
            metadata["categoryDescription"] = f"Test your knowledge of {topic} with this comprehensive quiz."
        
        if "categoryIcon" not in metadata:
            metadata["categoryIcon"] = self._get_default_icon(topic)
        
        # Ensure categoryName is not too long
        if len(metadata["categoryName"]) > 100:
            metadata["categoryName"] = metadata["categoryName"][:100]
        
        # Ensure description is reasonable length
        if len(metadata["categoryDescription"]) > 500:
            metadata["categoryDescription"] = metadata["categoryDescription"][:500]
        
        return metadata
    
    def _get_default_metadata(self, topic: str) -> Dict[str, Any]:
        """Get default metadata for a topic."""
        return {
            "categoryName": topic,
            "categoryDescription": f"Test your knowledge of {topic} with this comprehensive quiz covering key concepts, best practices, and real-world scenarios.",
            "categoryIcon": self._get_default_icon(topic)
        }
    
    def _get_default_icon(self, topic: str) -> str:
        """Get default icon for a topic."""
        icon_map = {
            "react": "⚛️",
            "node": "🟩",
            "javascript": "🟨",
            "python": "🐍",
            "java": "☕",
            "html": "🌐",
            "css": "🎨",
            "mongodb": "🍃",
            "sql": "🗄️",
            "devops": "⚙️",
            "cloud": "☁️",
            "security": "🔒",
            "ai": "🤖",
            "machine learning": "🧠",
            "data science": "📊",
            "dsa": "📚",
            "algorithms": "🔢"
        }
        
        topic_lower = topic.lower()
        for key, icon in icon_map.items():
            if key in topic_lower:
                return icon
        
        return "📝"  # Default icon