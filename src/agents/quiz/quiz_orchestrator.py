"""Quiz Orchestrator Agent - Main coordinator for quiz generation workflow."""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from langchain_core.prompts import PromptTemplate
from rich.console import Console
from rich.progress import Progress, TaskID

from src.core.base_agent import BaseAgent
from src.core.config import config
from src.utils.helpers import generate_filename, save_json_file, load_json_file
from src.utils.session_logger import append_log
from src.agents.quiz.quiz_researcher import QuizResearcher
from src.agents.quiz.quiz_question_creator import QuizQuestionCreator
from src.agents.quiz.quiz_uploader import QuizUploader
from src.agents.quiz.types import QuizTopic, QuizDifficulty, QuizModel, QuizQuestionModel

console = Console()


class QuizOrchestrator(BaseAgent):
    """Main orchestrator for quiz generation workflow."""
    
    def __init__(self, **kwargs):
        """Initialize the Quiz Orchestrator Agent."""
        super().__init__(**kwargs)
        
        # Initialize sub-agents
        self.researcher = QuizResearcher(**kwargs)
        self.question_creator = QuizQuestionCreator(**kwargs)
        self.uploader = QuizUploader(**kwargs)
        
        # Progress tracking
        self.progress_dir = os.path.join(config.temp_dir, "quiz_progress")
        os.makedirs(self.progress_dir, exist_ok=True)
        
        self.logger.info("Quiz Orchestrator Agent initialized")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for quiz orchestration."""
        return {
            "plan_quiz_generation": PromptTemplate(
                input_variables=["topic", "question_count", "target_audience"],
                template="""Plan the quiz generation process for {topic}.

Requirements:
- Total Questions: {question_count}
- Target Audience: {target_audience}

Create a detailed plan that includes:
1. Key concepts to cover (prioritized list)
2. Question type distribution (conceptual, code-based, scenario)
3. Difficulty distribution (easy, medium, hard)
4. Special considerations for {topic}
5. Quality checkpoints

Provide a structured plan that ensures comprehensive coverage and appropriate difficulty progression."""
            ),
            
            "generate_category_metadata": PromptTemplate(
                input_variables=["topic"],
                template="""Generate metadata for a {topic} quiz category.

Provide:
1. **Category ID**: A unique identifier (lowercase, hyphenated)
2. **Category Name**: Display name for the quiz
3. **Category Description**: Engaging description (2-3 sentences) that:
   - Explains what the quiz covers
   - Mentions the target audience
   - Highlights key learning outcomes
4. **Category Icon**: Suggest an appropriate emoji or icon name

Format as JSON:
{{
    "categoryName": "Display Name",
    "categoryDescription": "Description here",
    "categoryIcon": "🎯"
}}"""
            ),
            
            "review_quiz_quality": PromptTemplate(
                input_variables=["quiz_data", "topic"],
                template="""Review the quality of the generated {topic} quiz.

Quiz Data:
{quiz_data}

Evaluate:
1. **Content Quality**
   - Are questions clear and unambiguous?
   - Do they test appropriate concepts?
   - Is difficulty assessment accurate?

2. **Answer Quality**
   - Are distractors plausible but clearly wrong?
   - Are explanations helpful and accurate?
   - Do they teach, not just tell?

3. **Overall Balance**
   - Good mix of question types?
   - Appropriate difficulty progression?
   - Comprehensive topic coverage?

Provide:
- Overall quality score (1-10)
- Specific improvements needed
- Questions that need revision
- Final recommendations"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content for quiz orchestration."""
        if content_type == "generate_quiz":
            return self.generate_complete_quiz(
                kwargs.get("topic", ""),
                kwargs.get("question_count", 20),
                kwargs.get("target_audience", "developers")
            )
        elif content_type == "plan_quiz":
            return self.plan_quiz_generation(
                kwargs.get("topic", ""),
                kwargs.get("question_count", 20),
                kwargs.get("target_audience", "developers")
            )
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}
    
    def generate_complete_quiz(self, topic: str, question_count: int = 20, 
                              target_audience: str = "developers") -> Dict[str, Any]:
        """Generate a complete quiz with research, questions, and metadata."""
        console.print(f"[green]🚀 Starting quiz generation for {topic}...[/green]")
        
        # Create session ID for progress tracking
        session_id = str(uuid.uuid4())[:8]
        progress_file = os.path.join(self.progress_dir, f"quiz_{topic.lower().replace(' ', '_')}_{session_id}.json")
        
        # Initialize progress
        progress_data = {
            "session_id": session_id,
            "topic": topic,
            "question_count": question_count,
            "target_audience": target_audience,
            "status": "in_progress",
            "steps_completed": [],
            "current_step": "research",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "questions": [],
            "research_data": {},
            "metadata": {}
        }
        
        # Session start log
        append_log(session_id, "session_started", {"workflow": "quiz", "topic": topic, "question_count": question_count, "target_audience": target_audience})

        try:
            # Step 1: Research the topic
            console.print(f"[blue]📚 Step 1/4: Researching {topic}...[/blue]")
            research_result = self.researcher.comprehensive_research(topic, target_audience)
            
            if research_result.get("status") != "success":
                raise Exception(f"Research failed: {research_result.get('message', 'Unknown error')}")
            
            progress_data["research_data"] = research_result
            progress_data["steps_completed"].append("research")
            progress_data["current_step"] = "planning"
            self._save_progress(progress_data, progress_file)
            append_log(session_id, "step_completed", {"step": "research"})
            
            # Step 2: Plan quiz generation
            console.print(f"[blue]📋 Step 2/4: Planning quiz structure...[/blue]")
            plan_result = self.plan_quiz_generation(topic, question_count, target_audience)
            
            if plan_result.get("status") != "success":
                raise Exception(f"Planning failed: {plan_result.get('message', 'Unknown error')}")
            
            progress_data["quiz_plan"] = plan_result.get("plan", {})
            progress_data["steps_completed"].append("planning")
            progress_data["current_step"] = "generation"
            self._save_progress(progress_data, progress_file)
            append_log(session_id, "step_completed", {"step": "planning"})
            
            # Step 3: Generate questions
            console.print(f"[blue]🎯 Step 3/4: Generating {question_count} questions...[/blue]")
            questions = self._generate_questions_with_progress(
                research_result, plan_result.get("plan", {}), 
                topic, question_count, progress_data, progress_file
            )
            
            progress_data["questions"] = questions
            progress_data["steps_completed"].append("generation")
            progress_data["current_step"] = "metadata"
            self._save_progress(progress_data, progress_file)
            append_log(session_id, "step_completed", {"step": "generation", "questions_generated": len(questions)})
            
            # Step 4: Generate category metadata
            console.print(f"[blue]🏷️ Step 4/4: Generating quiz metadata...[/blue]")
            metadata_result = self._generate_category_metadata(topic)
            
            if metadata_result.get("status") != "success":
                raise Exception(f"Metadata generation failed: {metadata_result.get('message', 'Unknown error')}")
            
            progress_data["metadata"] = metadata_result.get("metadata", {})
            progress_data["steps_completed"].append("metadata")
            progress_data["current_step"] = "completed"
            progress_data["status"] = "completed"
            self._save_progress(progress_data, progress_file)
            append_log(session_id, "step_completed", {"step": "metadata"})
            
            # Create final quiz model
            quiz_model = self._create_quiz_model(progress_data)
            
            # Quality review
            console.print(f"[yellow]🔍 Performing quality review...[/yellow]")
            quality_review = self._review_quiz_quality(quiz_model.to_dict(), topic)
            
            # Save final output
            output_data = {
                "quiz": quiz_model.to_dict(),
                "metadata": {
                    "session_id": session_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "question_count": len(questions),
                    "topic": topic,
                    "target_audience": target_audience,
                    "quality_review": quality_review
                },
                "research_insights": research_result.get("compiled_insights", {})
            }
            
            # Save to output directory
            output_file = os.path.join(config.output_dir, f"quiz_{topic.lower().replace(' ', '_')}_{session_id}.json")
            save_json_file(output_data, output_file)
            
            console.print(f"[green]✅ Quiz generation completed![/green]")
            console.print(f"[green]📁 Output saved to: {output_file}[/green]")
            append_log(session_id, "session_completed", {"output_file": output_file})
            
            # Auto-create new quiz in database
            upload_result = None
            console.print(f"[blue]🚀 Auto-creating new quiz in database...[/blue]")
            try:
                upload_result = self.uploader.upload_quiz(quiz_model.to_dict())
                
                if upload_result.get("status") == "success":
                    console.print(f"[green]✅ Successfully created new quiz![/green]")
                    append_log(session_id, "auto_upload_success", {"action": "create"})
                else:
                    console.print(f"[red]❌ Auto-create failed: {upload_result.get('message', 'Unknown error')}[/red]")
                    append_log(session_id, "auto_upload_failed", {"error": upload_result.get('message')})
                    
            except Exception as create_error:
                upload_result = {
                    "status": "error",
                    "message": f"Create error: {str(create_error)}"
                }
                console.print(f"[red]❌ Auto-create error: {str(create_error)}[/red]")
                append_log(session_id, "auto_upload_error", {"error": str(create_error)})
            
            return {
                "status": "success",
                "quiz": quiz_model.to_dict(),
                "output_file": output_file,
                "session_id": session_id,
                "quality_score": quality_review.get("score", 0),
                "upload_result": upload_result  # Include upload result for frontend feedback
            }
            
        except Exception as e:
            self.logger.error(f"Error generating quiz: {str(e)}")
            progress_data["status"] = "failed"
            progress_data["error"] = str(e)
            self._save_progress(progress_data, progress_file)
            append_log(session_id, "session_failed", {"error": str(e)})
            
            return {
                "status": "error",
                "message": f"Quiz generation failed: {str(e)}",
                "session_id": session_id,
                "progress_file": progress_file
            }
    
    def plan_quiz_generation(self, topic: str, question_count: int = 20,
                           target_audience: str = "developers") -> Dict[str, Any]:
        """Plan the quiz generation process."""
        try:
            prompt = self._format_prompt("plan_quiz_generation",
                                       topic=topic,
                                       question_count=question_count,
                                       target_audience=target_audience)
            
            plan_content = self._generate_with_prompt(prompt)
            
            # Parse the plan
            plan = self._parse_quiz_plan(plan_content)
            
            return {
                "status": "success",
                "topic": topic,
                "plan": plan,
                "raw_plan": plan_content
            }
            
        except Exception as e:
            self.logger.error(f"Error planning quiz: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to plan quiz: {str(e)}"
            }
    
    def resume_quiz_generation(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused quiz generation session."""
        console.print(f"[yellow]📂 Resuming quiz generation session: {session_id}[/yellow]")
        
        # Find progress file
        progress_files = [f for f in os.listdir(self.progress_dir) if session_id in f]
        
        if not progress_files:
            return {
                "status": "error",
                "message": f"No session found with ID: {session_id}"
            }
        
        progress_file = os.path.join(self.progress_dir, progress_files[0])
        progress_data = load_json_file(progress_file)
        
        if progress_data.get("status") == "completed":
            return {
                "status": "success",
                "message": "Session already completed",
                "quiz": progress_data.get("quiz", {})
            }
        
        # Resume from current step
        current_step = progress_data.get("current_step", "research")
        console.print(f"[blue]Resuming from step: {current_step}[/blue]")
        
        # Continue generation based on current step
        if current_step == "research":
            return self.generate_complete_quiz(
                progress_data.get("topic"),
                progress_data.get("question_count"),
                progress_data.get("target_audience")
            )
        elif current_step == "planning":
            # Resume with existing research
            return self._resume_from_planning(progress_data, progress_file)
        elif current_step == "generation":
            # Resume question generation
            return self._resume_from_generation(progress_data, progress_file)
        elif current_step == "metadata":
            # Resume metadata generation
            return self._resume_from_metadata(progress_data, progress_file)
        else:
            return {
                "status": "error",
                "message": f"Unknown step: {current_step}"
            }
    
    def list_active_sessions(self) -> Dict[str, Any]:
        """List all active quiz generation sessions."""
        sessions = []
        
        for filename in os.listdir(self.progress_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.progress_dir, filename)
                try:
                    data = load_json_file(filepath)
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "topic": data.get("topic"),
                        "status": data.get("status"),
                        "current_step": data.get("current_step"),
                        "questions_generated": len(data.get("questions", [])),
                        "created_at": data.get("created_at"),
                        "filename": filename
                    })
                except Exception as e:
                    self.logger.error(f"Error reading session file {filename}: {str(e)}")
        
        # Sort by creation date
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "status": "success",
            "sessions": sessions,
            "count": len(sessions)
        }
    
    def _generate_questions_with_progress(self, research_data: Dict[str, Any],
                                        quiz_plan: Dict[str, Any], topic: str,
                                        question_count: int, progress_data: Dict[str, Any],
                                        progress_file: str) -> List[Dict[str, Any]]:
        """Generate questions with progress tracking."""
        questions = []
        existing_questions = progress_data.get("questions", [])
        
        # Start from where we left off
        start_index = len(existing_questions)
        questions.extend(existing_questions)
        
        # Get concepts from research
        concepts = research_data.get("compiled_insights", {}).get("key_concepts", [])
        
        # Difficulty distribution from plan
        difficulty_dist = quiz_plan.get("difficulty_distribution", {
            "easy": int(question_count * 0.3),
            "medium": int(question_count * 0.5),
            "hard": question_count - int(question_count * 0.3) - int(question_count * 0.5)
        })
        
        with Progress() as progress:
            task = progress.add_task(f"[green]Generating questions...", total=question_count)
            progress.update(task, completed=start_index)
            
            for i in range(start_index, question_count):
                # Determine difficulty for this question
                if i < difficulty_dist.get("easy", 0):
                    difficulty = QuizDifficulty.EASY
                elif i < difficulty_dist.get("easy", 0) + difficulty_dist.get("medium", 0):
                    difficulty = QuizDifficulty.MEDIUM
                else:
                    difficulty = QuizDifficulty.HARD
                
                # Select concept
                concept_index = i % len(concepts) if concepts else 0
                concept = concepts[concept_index] if concepts else f"{topic} concept {i+1}"
                
                # Determine question type based on position
                if i % 3 == 0:
                    question_type = "conceptual"
                elif i % 3 == 1:
                    question_type = "code_based"
                else:
                    question_type = "scenario"
                
                # Generate question
                result = self.question_creator.create_quiz_question(
                    topic=topic,
                    concept=concept,
                    difficulty=difficulty,
                    question_type=question_type
                )
                
                if result.get("status") == "success":
                    questions.append(result.get("question"))
                    progress_data["questions"] = questions
                    
                    # Save progress every 5 questions
                    if (i + 1) % 5 == 0:
                        self._save_progress(progress_data, progress_file)
                        append_log(progress_data.get("session_id", "unknown"), "progress", {"generated": len(questions), "total": question_count})
                
                progress.update(task, advance=1)
        
        return questions
    
    def _generate_category_metadata(self, topic: str) -> Dict[str, Any]:
        """Generate category metadata for the quiz."""
        try:
            prompt = self._format_prompt("generate_category_metadata", topic=topic)
            response = self._generate_with_prompt(prompt)
            
            # Parse JSON response
            metadata = self._parse_json_response(response)
            
            if metadata:
                # Remove categoryId if it exists in the metadata
                metadata.pop("categoryId", None)
                
                return {
                    "status": "success",
                    "metadata": metadata
                }
            else:
                # Generate default metadata
                return {
                    "status": "success",
                    "metadata": {
                        "categoryName": topic,
                        "categoryDescription": f"Test your knowledge of {topic} with this comprehensive quiz covering key concepts, best practices, and real-world scenarios.",
                        "categoryIcon": self._get_default_icon(topic)
                    }
                }
                
        except Exception as e:
            self.logger.error(f"Error generating metadata: {str(e)}")
            # Return default metadata on error
            return {
                "status": "success",
                "metadata": {
                    "categoryName": topic,
                    "categoryDescription": f"Test your knowledge of {topic} with this comprehensive quiz.",
                    "categoryIcon": "📝"
                }
            }
    

    
    def _review_quiz_quality(self, quiz_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Review the quality of generated quiz."""
        try:
            # Truncate quiz data for review (just show first 3 questions)
            review_data = {
                "categoryName": quiz_data.get("categoryName"),
                "questions": quiz_data.get("questions", [])[:3],
                "total_questions": len(quiz_data.get("questions", []))
            }
            
            prompt = self._format_prompt("review_quiz_quality",
                                       quiz_data=json.dumps(review_data, indent=2),
                                       topic=topic)
            
            review_content = self._generate_with_prompt(prompt)
            
            # Parse review
            return self._parse_quality_review(review_content)
            
        except Exception as e:
            self.logger.error(f"Error reviewing quiz quality: {str(e)}")
            return {
                "score": 7,
                "feedback": "Automated review completed",
                "improvements": []
            }
    
    def _create_quiz_model(self, progress_data: Dict[str, Any]) -> QuizModel:
        """Create QuizModel from progress data."""
        metadata = progress_data.get("metadata", {})
        questions = progress_data.get("questions", [])
        
        # Convert questions to QuizQuestionModel objects
        question_models = []
        for q in questions:
            if isinstance(q, dict):
                question_models.append(QuizQuestionModel.from_dict(q))
        
        # Create quiz model
        return QuizModel(
            category_name=metadata.get("categoryName", ""),
            category_description=metadata.get("categoryDescription", ""),
            category_icon=metadata.get("categoryIcon", "📝"),
            questions=question_models,
            is_active=True
        )
    
    def _parse_quiz_plan(self, content: str) -> Dict[str, Any]:
        """Parse quiz generation plan from content."""
        plan = {
            "concepts": [],
            "question_types": {},
            "difficulty_distribution": {},
            "special_considerations": []
        }
        
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "concepts" in line.lower() and ":" in line:
                current_section = "concepts"
            elif "question type" in line.lower():
                current_section = "question_types"
            elif "difficulty" in line.lower() and "distribution" in line.lower():
                current_section = "difficulty"
            elif "considerations" in line.lower():
                current_section = "considerations"
            elif line.startswith('-') or line.startswith('•'):
                item = line.lstrip('-•').strip()
                if current_section == "concepts" and item:
                    plan["concepts"].append(item)
                elif current_section == "considerations" and item:
                    plan["special_considerations"].append(item)
            elif current_section == "difficulty" and ':' in line:
                parts = line.split(':')
                if len(parts) == 2:
                    level = parts[0].strip().lower()
                    try:
                        count = int(''.join(filter(str.isdigit, parts[1])))
                        plan["difficulty_distribution"][level] = count
                    except:
                        pass
        
        return plan
    
    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response."""
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            return None
    
    def _parse_quality_review(self, content: str) -> Dict[str, Any]:
        """Parse quality review results."""
        review = {
            "score": 7,
            "feedback": "",
            "improvements": [],
            "questions_to_revise": []
        }
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if "score:" in line.lower() or "quality score:" in line.lower():
                try:
                    score_text = line.split(':')[1].strip()
                    score = int(''.join(filter(str.isdigit, score_text)))
                    review["score"] = min(10, max(1, score))
                except:
                    pass
            elif line.startswith('-') and "improve" in line.lower():
                review["improvements"].append(line.lstrip('-').strip())
        
        return review
    
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
            "data science": "📊"
        }
        
        topic_lower = topic.lower()
        for key, icon in icon_map.items():
            if key in topic_lower:
                return icon
        
        return "📝"  # Default icon
    
    def _save_progress(self, progress_data: Dict[str, Any], progress_file: str):
        """Save progress to file."""
        progress_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        save_json_file(progress_data, progress_file)
    
    def _resume_from_planning(self, progress_data: Dict[str, Any], progress_file: str) -> Dict[str, Any]:
        """Resume quiz generation from planning step."""
        # Implementation for resuming from planning
        topic = progress_data.get("topic")
        question_count = progress_data.get("question_count")
        target_audience = progress_data.get("target_audience")
        
        # Continue with planning
        console.print(f"[blue]Continuing planning for {topic}...[/blue]")
        plan_result = self.plan_quiz_generation(topic, question_count, target_audience)
        
        if plan_result.get("status") == "success":
            progress_data["quiz_plan"] = plan_result.get("plan", {})
            progress_data["steps_completed"].append("planning")
            progress_data["current_step"] = "generation"
            self._save_progress(progress_data, progress_file)
            
            # Continue to generation
            return self._resume_from_generation(progress_data, progress_file)
        else:
            return plan_result
    
    def _resume_from_generation(self, progress_data: Dict[str, Any], progress_file: str) -> Dict[str, Any]:
        """Resume quiz generation from question generation step."""
        # Implementation for resuming from generation
        console.print(f"[blue]Continuing question generation...[/blue]")
        
        # Continue generating questions
        research_data = progress_data.get("research_data", {})
        quiz_plan = progress_data.get("quiz_plan", {})
        topic = progress_data.get("topic")
        question_count = progress_data.get("question_count")
        
        questions = self._generate_questions_with_progress(
            research_data, quiz_plan, topic, question_count, 
            progress_data, progress_file
        )
        
        progress_data["questions"] = questions
        progress_data["steps_completed"].append("generation")
        progress_data["current_step"] = "metadata"
        self._save_progress(progress_data, progress_file)
        
        # Continue to metadata
        return self._resume_from_metadata(progress_data, progress_file)
    
    def _resume_from_metadata(self, progress_data: Dict[str, Any], progress_file: str) -> Dict[str, Any]:
        """Resume quiz generation from metadata step."""
        # Implementation for resuming from metadata
        console.print(f"[blue]Generating metadata...[/blue]")
        
        topic = progress_data.get("topic")
        metadata_result = self._generate_category_metadata(topic)
        
        if metadata_result.get("status") == "success":
            progress_data["metadata"] = metadata_result.get("metadata", {})
            progress_data["steps_completed"].append("metadata")
            progress_data["current_step"] = "completed"
            progress_data["status"] = "completed"
            self._save_progress(progress_data, progress_file)
            
            # Create final quiz
            quiz_model = self._create_quiz_model(progress_data)
            
            # Save output
            session_id = progress_data.get("session_id")
            output_file = os.path.join(config.output_dir, f"quiz_{topic.lower().replace(' ', '_')}_{session_id}.json")
            
            output_data = {
                "quiz": quiz_model.to_dict(),
                "metadata": {
                    "session_id": session_id,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "topic": topic
                }
            }
            
            save_json_file(output_data, output_file)
            
            return {
                "status": "success",
                "quiz": quiz_model.to_dict(),
                "output_file": output_file,
                "session_id": session_id
            }
        else:
            return metadata_result 