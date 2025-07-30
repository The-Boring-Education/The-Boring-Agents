"""Quiz Question Creator Agent - Generates quiz questions with options and explanations."""

import json
import random
from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate
from rich.console import Console

from ...core.base_agent import BaseAgent
from ...core.config import config
from .types import QuizDifficulty, QuizQuestionModel, QuizTopic

console = Console()


class QuizQuestionCreator(BaseAgent):
    """Agent responsible for creating quiz questions with multiple choices and explanations."""
    
    def __init__(self, **kwargs):
        """Initialize the Quiz Question Creator Agent."""
        super().__init__(**kwargs)
        self.logger.info("Quiz Question Creator Agent initialized")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for quiz question creation."""
        return {
            "create_quiz_question": PromptTemplate(
                input_variables=["topic", "concept", "difficulty", "question_type", "context"],
                template="""You are an expert quiz creator for {topic}.

Create a high-quality multiple-choice quiz question with the following requirements:

Topic: {topic}
Concept to Test: {concept}
Difficulty Level: {difficulty}
Question Type: {question_type}
Additional Context: {context}

Requirements:
1. **Question**: Clear, unambiguous, and directly tests the concept
2. **Options**: Exactly 4 options (A, B, C, D)
   - One correct answer
   - Three plausible distractors (wrong answers)
   - Options should be similar in length and complexity
3. **Correct Answer**: Indicate which option (0-3 index)
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
}}"""
            ),
            
            "create_code_based_question": PromptTemplate(
                input_variables=["topic", "concept", "difficulty", "code_focus"],
                template="""Create a code-based multiple-choice question for {topic}.

Topic: {topic}
Concept: {concept}
Difficulty: {difficulty}
Code Focus: {code_focus}

Requirements:
1. Include a code snippet that demonstrates the concept
2. Ask about the output, behavior, or best practice
3. Create 4 options with believable alternatives
4. Consider common mistakes developers make

For {topic}, ensure the code:
- Uses modern syntax and best practices
- Is realistic and practical
- Tests understanding, not memorization

Format as JSON:
{{
    "question": "Given the following code:\\n```{topic}\\ncode here\\n```\\nWhat will be the output?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 0,
    "explanation": "Brief explanation",
    "detailedExplanation": "Detailed explanation with code walkthrough"
}}"""
            ),
            
            "create_scenario_question": PromptTemplate(
                input_variables=["topic", "scenario", "difficulty"],
                template="""Create a scenario-based multiple-choice question for {topic}.

Topic: {topic}
Scenario: {scenario}
Difficulty: {difficulty}

Create a real-world scenario question that:
1. Presents a practical problem developers face
2. Tests decision-making and best practices
3. Has multiple valid approaches but one best answer
4. Relates to Indian tech industry when possible

Format as JSON with all required fields."""
            ),
            
            "batch_create_questions": PromptTemplate(
                input_variables=["topic", "concepts", "difficulty_distribution", "count"],
                template="""Create {count} diverse quiz questions for {topic}.

Topic: {topic}
Concepts to Cover: {concepts}
Difficulty Distribution: {difficulty_distribution}

Create a balanced set of questions that:
1. Cover different concepts from the list
2. Use various question types (conceptual, code-based, scenario)
3. Follow the difficulty distribution
4. Avoid repetition and ensure variety

For each question, provide:
- Clear, unambiguous question text
- 4 well-crafted options
- Correct answer index (0-3)
- Brief and detailed explanations
- Appropriate difficulty level

Return as a JSON array of question objects."""
            ),
            
            "improve_question": PromptTemplate(
                input_variables=["question", "feedback"],
                template="""Improve the following quiz question based on feedback.

Original Question:
{question}

Feedback:
{feedback}

Improve the question by:
1. Making it clearer and more precise
2. Improving the distractors (wrong answers)
3. Enhancing the explanations
4. Ensuring technical accuracy
5. Following quiz best practices

Return the improved question in the same JSON format."""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate quiz question content."""
        if content_type == "create_question":
            return self.create_quiz_question(
                kwargs.get("topic", ""),
                kwargs.get("concept", ""),
                kwargs.get("difficulty", QuizDifficulty.MEDIUM),
                kwargs.get("question_type", "conceptual"),
                kwargs.get("context", "")
            )
        elif content_type == "create_code_question":
            return self.create_code_based_question(
                kwargs.get("topic", ""),
                kwargs.get("concept", ""),
                kwargs.get("difficulty", QuizDifficulty.MEDIUM),
                kwargs.get("code_focus", "")
            )
        elif content_type == "batch_create":
            return self.batch_create_questions(
                kwargs.get("topic", ""),
                kwargs.get("concepts", []),
                kwargs.get("difficulty_distribution", {}),
                kwargs.get("count", 10)
            )
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}
    
    def create_quiz_question(self, topic: str, concept: str, 
                           difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
                           question_type: str = "conceptual",
                           context: str = "") -> Dict[str, Any]:
        """Create a single quiz question."""
        console.print(f"[blue]🎯 Creating {difficulty.value} {question_type} question for {topic}...[/blue]")
        
        try:
            prompt = self._format_prompt("create_quiz_question",
                                       topic=topic,
                                       concept=concept,
                                       difficulty=difficulty.value,
                                       question_type=question_type,
                                       context=context)
            
            response = self._generate_with_prompt(prompt)
            
            # Parse JSON response
            question_data = self._parse_json_response(response)
            
            if question_data:
                # Create QuizQuestionModel
                question_model = QuizQuestionModel(
                    question=question_data.get("question", ""),
                    options=question_data.get("options", []),
                    correct_answer=question_data.get("correctAnswer", 0),
                    explanation=question_data.get("explanation", ""),
                    detailed_explanation=question_data.get("detailedExplanation", ""),
                    difficulty=difficulty
                )
                
                return {
                    "status": "success",
                    "question": question_model.to_dict(),
                    "metadata": {
                        "topic": topic,
                        "concept": concept,
                        "question_type": question_type
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to parse question response"
                }
                
        except Exception as e:
            self.logger.error(f"Error creating question: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create question: {str(e)}"
            }
    
    def create_code_based_question(self, topic: str, concept: str,
                                 difficulty: QuizDifficulty = QuizDifficulty.MEDIUM,
                                 code_focus: str = "") -> Dict[str, Any]:
        """Create a code-based quiz question."""
        console.print(f"[blue]💻 Creating code-based question for {topic}...[/blue]")
        
        try:
            prompt = self._format_prompt("create_code_based_question",
                                       topic=topic,
                                       concept=concept,
                                       difficulty=difficulty.value,
                                       code_focus=code_focus)
            
            response = self._generate_with_prompt(prompt)
            question_data = self._parse_json_response(response)
            
            if question_data:
                question_model = QuizQuestionModel(
                    question=question_data.get("question", ""),
                    options=question_data.get("options", []),
                    correct_answer=question_data.get("correctAnswer", 0),
                    explanation=question_data.get("explanation", ""),
                    detailed_explanation=question_data.get("detailedExplanation", ""),
                    difficulty=difficulty
                )
                
                return {
                    "status": "success",
                    "question": question_model.to_dict(),
                    "metadata": {
                        "topic": topic,
                        "concept": concept,
                        "question_type": "code_based",
                        "code_focus": code_focus
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to parse code question response"
                }
                
        except Exception as e:
            self.logger.error(f"Error creating code question: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create code question: {str(e)}"
            }
    
    def create_scenario_question(self, topic: str, scenario: str,
                               difficulty: QuizDifficulty = QuizDifficulty.MEDIUM) -> Dict[str, Any]:
        """Create a scenario-based quiz question."""
        console.print(f"[blue]🌟 Creating scenario-based question for {topic}...[/blue]")
        
        try:
            prompt = self._format_prompt("create_scenario_question",
                                       topic=topic,
                                       scenario=scenario,
                                       difficulty=difficulty.value)
            
            response = self._generate_with_prompt(prompt)
            question_data = self._parse_json_response(response)
            
            if question_data:
                question_model = QuizQuestionModel(
                    question=question_data.get("question", ""),
                    options=question_data.get("options", []),
                    correct_answer=question_data.get("correctAnswer", 0),
                    explanation=question_data.get("explanation", ""),
                    detailed_explanation=question_data.get("detailedExplanation", ""),
                    difficulty=difficulty
                )
                
                return {
                    "status": "success",
                    "question": question_model.to_dict(),
                    "metadata": {
                        "topic": topic,
                        "scenario": scenario,
                        "question_type": "scenario_based"
                    }
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to parse scenario question response"
                }
                
        except Exception as e:
            self.logger.error(f"Error creating scenario question: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create scenario question: {str(e)}"
            }
    
    def batch_create_questions(self, topic: str, concepts: List[str],
                             difficulty_distribution: Dict[str, int],
                             count: int = 10) -> Dict[str, Any]:
        """Create multiple quiz questions in batch."""
        console.print(f"[green]📚 Creating {count} questions for {topic}...[/green]")
        
        # Default distribution if not provided
        if not difficulty_distribution:
            difficulty_distribution = {
                "easy": int(count * 0.3),
                "medium": int(count * 0.5),
                "hard": count - int(count * 0.3) - int(count * 0.5)
            }
        
        try:
            # Prepare concepts list
            concepts_str = "\n".join([f"- {c}" for c in concepts[:10]])
            dist_str = ", ".join([f"{k}: {v}" for k, v in difficulty_distribution.items()])
            
            prompt = self._format_prompt("batch_create_questions",
                                       topic=topic,
                                       concepts=concepts_str,
                                       difficulty_distribution=dist_str,
                                       count=count)
            
            response = self._generate_with_prompt(prompt)
            questions_data = self._parse_json_array_response(response)
            
            if questions_data:
                questions = []
                for q_data in questions_data:
                    # Determine difficulty
                    diff_str = q_data.get("difficulty", "medium").lower()
                    difficulty = QuizDifficulty(diff_str) if diff_str in ["easy", "medium", "hard"] else QuizDifficulty.MEDIUM
                    
                    question_model = QuizQuestionModel(
                        question=q_data.get("question", ""),
                        options=q_data.get("options", []),
                        correct_answer=q_data.get("correctAnswer", 0),
                        explanation=q_data.get("explanation", ""),
                        detailed_explanation=q_data.get("detailedExplanation", ""),
                        difficulty=difficulty
                    )
                    questions.append(question_model.to_dict())
                
                return {
                    "status": "success",
                    "questions": questions,
                    "count": len(questions),
                    "topic": topic,
                    "difficulty_distribution": self._calculate_actual_distribution(questions)
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to parse batch questions response"
                }
                
        except Exception as e:
            self.logger.error(f"Error creating batch questions: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to create batch questions: {str(e)}"
            }
    
    def improve_question(self, question: Dict[str, Any], feedback: str) -> Dict[str, Any]:
        """Improve an existing question based on feedback."""
        console.print(f"[yellow]🔧 Improving question based on feedback...[/yellow]")
        
        try:
            question_str = json.dumps(question, indent=2)
            prompt = self._format_prompt("improve_question",
                                       question=question_str,
                                       feedback=feedback)
            
            response = self._generate_with_prompt(prompt)
            improved_data = self._parse_json_response(response)
            
            if improved_data:
                # Create improved question model
                difficulty = QuizDifficulty(question.get("difficulty", "medium"))
                question_model = QuizQuestionModel(
                    question=improved_data.get("question", ""),
                    options=improved_data.get("options", []),
                    correct_answer=improved_data.get("correctAnswer", 0),
                    explanation=improved_data.get("explanation", ""),
                    detailed_explanation=improved_data.get("detailedExplanation", ""),
                    difficulty=difficulty
                )
                
                return {
                    "status": "success",
                    "improved_question": question_model.to_dict(),
                    "feedback_applied": feedback
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to parse improved question"
                }
                
        except Exception as e:
            self.logger.error(f"Error improving question: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to improve question: {str(e)}"
            }
    
    def create_questions_from_research(self, research_data: Dict[str, Any], 
                                     count: int = 20) -> Dict[str, Any]:
        """Create questions based on research insights."""
        console.print(f"[green]🧠 Creating questions from research insights...[/green]")
        
        # Extract insights from research
        insights = research_data.get("compiled_insights", {})
        concepts = insights.get("key_concepts", [])
        misconceptions = insights.get("common_misconceptions", [])
        best_practices = insights.get("best_practices", [])
        
        # Create a mix of question types
        questions = []
        
        # Concept-based questions (40%)
        concept_count = int(count * 0.4)
        for i in range(min(concept_count, len(concepts))):
            result = self.create_quiz_question(
                topic=research_data.get("topic", ""),
                concept=concepts[i],
                difficulty=self._assign_difficulty(i, concept_count),
                question_type="conceptual"
            )
            if result.get("status") == "success":
                questions.append(result["question"])
        
        # Misconception-based questions (30%)
        misconception_count = int(count * 0.3)
        for i in range(min(misconception_count, len(misconceptions))):
            result = self.create_quiz_question(
                topic=research_data.get("topic", ""),
                concept=f"Common misconception: {misconceptions[i]}",
                difficulty=QuizDifficulty.MEDIUM,
                question_type="misconception",
                context="Test understanding by addressing common misconceptions"
            )
            if result.get("status") == "success":
                questions.append(result["question"])
        
        # Best practice questions (30%)
        practice_count = count - len(questions)
        for i in range(min(practice_count, len(best_practices))):
            result = self.create_scenario_question(
                topic=research_data.get("topic", ""),
                scenario=f"Best practice scenario: {best_practices[i]}",
                difficulty=self._assign_difficulty(i, practice_count)
            )
            if result.get("status") == "success":
                questions.append(result["question"])
        
        return {
            "status": "success",
            "questions": questions,
            "count": len(questions),
            "topic": research_data.get("topic", ""),
            "sources": {
                "concepts": len([q for q in questions if "concept" in str(q)]),
                "misconceptions": len([q for q in questions if "misconception" in str(q)]),
                "best_practices": len([q for q in questions if "practice" in str(q)])
            }
        }
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response."""
        try:
            # Find JSON block in response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Try parsing entire response
                return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {str(e)}")
            self.logger.debug(f"Response: {response[:500]}...")
            return None
    
    def _parse_json_array_response(self, response: str) -> Optional[List[Dict[str, Any]]]:
        """Parse JSON array from LLM response."""
        try:
            # Find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Try parsing entire response
                return json.loads(response)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON array parse error: {str(e)}")
            self.logger.debug(f"Response: {response[:500]}...")
            return None
    
    def _assign_difficulty(self, index: int, total: int) -> QuizDifficulty:
        """Assign difficulty based on index position."""
        if index < total * 0.3:
            return QuizDifficulty.EASY
        elif index < total * 0.8:
            return QuizDifficulty.MEDIUM
        else:
            return QuizDifficulty.HARD
    
    def _calculate_actual_distribution(self, questions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate actual difficulty distribution of questions."""
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        
        for q in questions:
            difficulty = q.get("difficulty", "medium")
            if difficulty in distribution:
                distribution[difficulty] += 1
        
        return distribution 