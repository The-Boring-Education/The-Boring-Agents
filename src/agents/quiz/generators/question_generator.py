"""Question generator for quiz questions with options and explanations."""

from typing import Dict, Any, List
from langchain_core.prompts import PromptTemplate
import json
import logging

from src.agents.base import BaseAgent
from src.agents.quiz.types import QuizDifficulty

logger = logging.getLogger(__name__)

class QuizQuestionGenerator(BaseAgent):
    """Generator for quiz questions with multiple choice options."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for quiz question generation."""
        return {
            "generate_question": PromptTemplate(
                input_variables=["topic", "concept", "difficulty", "target_audience", "question_type"],
                template="""
                    You are an expert quiz creator for {topic}. Create a high-quality multiple-choice quiz question.

                    Topic: {topic}
                    Concept to Test: {concept}
                    Difficulty Level: {difficulty}
                    Target Audience: {target_audience}
                    Question Type: {question_type}

                    Requirements:
                    1. **Question**: Clear, unambiguous, directly tests the concept
                    2. **Options**: Exactly 4 options (A, B, C, D)
                    - One correct answer
                    - Three plausible distractors (wrong but believable)
                    - Options should be similar in length and complexity
                    3. **Correct Answer**: Index 0-3 (which option is correct)
                    4. **Explanation**: Brief explanation (2-3 sentences) of why the answer is correct
                    5. **Detailed Explanation**: Comprehensive explanation (1-2 paragraphs) that:
                    - Explains why the correct answer is right
                    - Explains why each wrong answer is incorrect
                    - Provides additional context or tips
                    - References best practices when applicable

                    For {difficulty} difficulty:
                    - Easy: Test basic understanding, straightforward concepts
                    - Medium: Apply knowledge, some analysis required
                    - Hard: Complex scenarios, deep understanding, edge cases

                    Format your response as JSON:
                    {{
                        "question": "Your question here",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correctAnswer": 0,
                        "explanation": "Brief explanation",
                        "detailedExplanation": "Comprehensive explanation"
                    }}
                    """
                                ),
                                "generate_batch_questions": PromptTemplate(
                                    input_variables=["topic", "question_count", "difficulty", "target_audience", "concepts"],
                                    template="""
                    You are an expert quiz creator for {topic}. Generate {question_count} diverse quiz questions.

                    Topic: {topic}
                    Question Count: {question_count}
                    Difficulty: {difficulty}
                    Target Audience: {target_audience}
                    Concepts to Cover: {concepts}

                    Create a balanced set of questions that:
                    1. Cover different concepts from the list
                    2. Use various question types (conceptual, code-based, scenario)
                    3. Follow the difficulty level ({difficulty})
                    4. Avoid repetition and ensure variety

                    For each question, provide:
                    - Clear, unambiguous question text
                    - 4 well-crafted options
                    - Correct answer index (0-3)
                    - Brief and detailed explanations
                    - Appropriate difficulty level

                    Return as a JSON array of question objects:
                    [
                        {{
                            "question": "Question 1",
                            "options": ["A", "B", "C", "D"],
                            "correctAnswer": 0,
                            "explanation": "Brief",
                            "detailedExplanation": "Detailed"
                        }},
                        ...
                    ]
                """
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate quiz question content."""
        if content_type == "generate_question":
            return self.generate_question(
                topic=kwargs.get("topic", ""),
                concept=kwargs.get("concept", ""),
                difficulty=kwargs.get("difficulty", QuizDifficulty.MEDIUM),
                target_audience=kwargs.get("target_audience", "developers"),
                question_type=kwargs.get("question_type", "conceptual")
            )
        elif content_type == "generate_batch":
            return self.generate_batch_questions(
                topic=kwargs.get("topic", ""),
                question_count=kwargs.get("question_count", 20),
                difficulty=kwargs.get("difficulty", QuizDifficulty.MEDIUM),
                target_audience=kwargs.get("target_audience", "developers"),
                concepts=kwargs.get("concepts", [])
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def generate_question(
        self,
        topic: str,
        concept: str,
        difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
        target_audience: str = "developers",
        question_type: str = "conceptual"
    ) -> Dict[str, Any]:
        """Generate a single quiz question."""
        prompt = self._format_prompt(
            "generate_question",
            topic=topic,
            concept=concept,
            difficulty=difficulty.value,
            target_audience=target_audience,
            question_type=question_type
        )
        
        response = self._generate_with_prompt(prompt)
        question_data = self._parse_json_response(response)
        
        if not question_data:
            raise ValueError("Failed to parse question from LLM response")
        
        # Validate and normalize
        question_data["difficulty"] = difficulty.value
        question_data = self._validate_question(question_data)
        
        return question_data
    
    def generate_batch_questions(
        self,
        topic: str,
        question_count: int,
        difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
        target_audience: str = "developers",
        concepts: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate multiple quiz questions in batch."""
        if concepts is None:
            concepts = [f"{topic} concept {i+1}" for i in range(question_count)]
        
        concepts_str = "\n".join([f"- {c}" for c in concepts[:20]])  # Limit to 20 concepts
        
        prompt = self._format_prompt(
            "generate_batch_questions",
            topic=topic,
            question_count=question_count,
            difficulty=difficulty.value,
            target_audience=target_audience,
            concepts=concepts_str
        )
        
        response = self._generate_with_prompt(prompt)
        questions = self._parse_json_array_response(response)
        
        if not questions or len(questions) < question_count:
            # Fallback: generate questions one by one
            logger.warning(f"Batch generation returned {len(questions) if questions else 0} questions, generating individually")
            questions = []
            for i in range(question_count):
                concept = concepts[i % len(concepts)] if concepts else f"{topic} concept {i+1}"
                try:
                    question = self.generate_question(
                        topic=topic,
                        concept=concept,
                        difficulty=difficulty,
                        target_audience=target_audience,
                        question_type="conceptual" if i % 3 == 0 else ("code_based" if i % 3 == 1 else "scenario")
                    )
                    questions.append(question)
                except Exception as e:
                    logger.error(f"Error generating question {i+1}: {e}")
                    continue
        
        # Validate all questions
        validated_questions = []
        for q in questions[:question_count]:
            try:
                q["difficulty"] = difficulty.value
                validated_questions.append(self._validate_question(q))
            except Exception as e:
                logger.error(f"Error validating question: {e}")
                continue
        
        return validated_questions
    
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
    
    def _parse_json_array_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse JSON array from LLM response."""
        try:
            # Find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON array parse error: {e}")
            logger.debug(f"Response: {response[:500]}...")
            return None
    
    def _validate_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize question data."""
        # Ensure all required fields
        required_fields = ["question", "options", "correctAnswer", "explanation", "detailedExplanation"]
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate options
        options = question.get("options", [])
        if len(options) != 4:
            raise ValueError(f"Must have exactly 4 options, found {len(options)}")
        
        # Validate correctAnswer
        correct_answer = question.get("correctAnswer")
        if not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer >= len(options):
            raise ValueError(f"correctAnswer must be 0-3, found {correct_answer}")
        
        # Ensure difficulty is set
        if "difficulty" not in question:
            question["difficulty"] = "medium"
        
        # Normalize difficulty
        difficulty = question.get("difficulty", "medium").lower()
        if difficulty not in ["easy", "medium", "hard"]:
            question["difficulty"] = "medium"
        else:
            question["difficulty"] = difficulty
        
        return question