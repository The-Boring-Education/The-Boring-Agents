## NEW

from typing import List, Dict
from ..core.base_agent import BaseAgent

class QuizAgent(BaseAgent):
    """Generates quizzes and exercises for a given topic."""

    def generate_quiz(self, topic: str, difficulty: str = "Beginner") -> List[Dict]:
        """
        Generate multiple choice questions for the given topic.
        Returns a list of questions with options and answers.
        """
        # Placeholder for now
        questions = [
            {
                "question": f"What is the main concept of {topic}?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A"
            }
        ]
        return questions

    def generate_exercises(self, topic: str, difficulty: str = "Beginner") -> List[str]:
        """
        Generate exercises/practice problems for the given topic.
        """
        exercises = [
            f"Practice exercise related to {topic} - 1",
            f"Practice exercise related to {topic} - 2"
        ]
        return exercises
