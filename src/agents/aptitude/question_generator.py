"""Question generator for aptitude interview prep."""

import logging
from typing import List

from langchain_core.prompts import PromptTemplate
from src.agents.base import BaseAgent

logger = logging.getLogger(__name__)

class AptitudeQuestionGenerator(BaseAgent):
    """Generates aptitude questions on the fly."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def generate_content(self, content_type: str = "questions", **kwargs) -> dict:
        if content_type == "questions":
            topic = kwargs.get("topic", "")
            count = kwargs.get("count", 5)
            return {"status": "success", "questions": self.generate_questions(topic, count)}
        raise ValueError(f"Unknown content type: {content_type}")

    def generate_questions(self, topic: str, count: int = 5) -> List[dict]:
        self.logger.info("Generating %d questions for topic: %s...", count, topic)

        prompt_template = PromptTemplate(
            input_variables=["topic", "count"],
            template="""You are an expert aptitude test creator.
Generate exactly {count} unique aptitude questions for the topic '{topic}'.
Return ONLY a raw JSON array of objects. Do not wrap in markdown blocks.

Each object must follow this exact schema:
{{
  "question": "The question text here...",
  "options": [
    {{ "text": "Option A text", "isCorrect": true }},
    {{ "text": "Option B text", "isCorrect": false }},
    {{ "text": "Option C text", "isCorrect": false }},
    {{ "text": "Option D text", "isCorrect": false }}
  ]
}}

Make sure exactly one option has "isCorrect": true. 
Vary which option is the correct one!

Questions JSON Array:"""
        )

        prompt = prompt_template.format(topic=topic, count=count)
        raw_output = self._generate_with_prompt(prompt)
        
        # Clean up output
        cleaned_json = raw_output.strip()
        if cleaned_json.startswith("```json"):
            cleaned_json = cleaned_json.split("```json", 1)[1]
        if cleaned_json.endswith("```"):
            cleaned_json = cleaned_json.rsplit("```", 1)[0]
        cleaned_json = cleaned_json.strip()

        try:
            import json
            import random
            questions_data = json.loads(cleaned_json)
            if not isinstance(questions_data, list):
                raise ValueError("LLM did not return a list")
            
            # Shuffle options to ensure "Option A" isn't always the correct one
            for q in questions_data:
                if "options" in q and isinstance(q["options"], list):
                    random.shuffle(q["options"])
            
            self.logger.info("Successfully generated %d questions with options.", len(questions_data[:count]))
            return questions_data[:count]
        except Exception as e:
            self.logger.error("Failed to parse JSON questions: %s", e)
            self.logger.debug("Raw output: %s", raw_output)
            return []
