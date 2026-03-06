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

    def generate_questions(self, topic: str, count: int = 5) -> List[str]:
        self.logger.info("Generating %d questions for topic: %s...", count, topic)

        prompt_template = PromptTemplate(
            input_variables=["topic", "count"],
            template="""You are an expert aptitude test creator.
Generate exactly {count} unique aptitude questions for the topic '{topic}'.

Rules:
1. Return ONLY the questions.
2. Provide exactly one question per line.
3. DO NOT include numbering (like 1., 2., etc.).
4. DO NOT include options (A, B, C, D).
5. DO NOT include the answers.

Questions:"""
        )

        prompt = prompt_template.format(topic=topic, count=count)
        raw_output = self._generate_with_prompt(prompt)
        
        # Clean up output
        questions = [q.strip() for q in raw_output.split('\n') if q.strip()]
        
        # Strip numbering just in case the LLM disobeyed
        for i in range(len(questions)):
            if len(questions[i]) > 2 and questions[i][0].isdigit() and questions[i][1] in ('.', ')'):
                questions[i] = questions[i][2:].strip()
                
        self.logger.info("Successfully generated %d questions.", len(questions[:count]))
        return questions[:count]
