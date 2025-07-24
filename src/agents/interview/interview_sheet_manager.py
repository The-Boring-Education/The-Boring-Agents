"""Interview Sheet Manager - Main coordinator for interview sheet lifecycle."""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate
from rich.console import Console
from rich.progress import Progress, TaskID

from ...core.base_agent import BaseAgent
from ...core.config import config
from ...utils.helpers import generate_filename, save_json_file, load_json_file
from ...utils.validation import InterviewQuestionValidator
from .answer_creator import AnswerCreator
from .dsa_answer_creator import DSAAnswerCreator
from .metadata_agent import MetadataAgent
from .mdx_styling_agent import MDXStylingAgent
from .types import AnswerAgentType

console = Console()


class InterviewSheetManager(BaseAgent):
    """Main manager for interview sheet lifecycle - creation, generation, review, and publication."""
    
    def __init__(self, agent_type: AnswerAgentType = AnswerAgentType.GENERIC, **kwargs):
        """Initialize the sheet manager with streamlined agents.
        
        Args:
            agent_type: Type of answer creator agent to use
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(**kwargs)
        
        # Initialize only essential agents for quality
        self.agent_type = agent_type
        self.answer_creator = self._create_answer_creator(agent_type, **kwargs)
        self.metadata_agent = MetadataAgent(**kwargs)
        self.mdx_styler = MDXStylingAgent(**kwargs)
        
        self.logger.info(f"Interview Sheet Manager initialized with {agent_type.value} answer creator")
    
    def _create_answer_creator(self, agent_type: AnswerAgentType, **kwargs):
        """Create the appropriate answer creator based on agent type.
        
        Args:
            agent_type: Type of answer creator to create
            **kwargs: Additional arguments passed to the creator
            
        Returns:
            Appropriate answer creator instance
        """
        if agent_type == AnswerAgentType.DSA:
            return DSAAnswerCreator(**kwargs)
        elif agent_type == AnswerAgentType.GENERIC:
            return AnswerCreator(**kwargs)
        elif agent_type == AnswerAgentType.TECH:
            # Future implementation - for now, use generic
            self.logger.warning("Tech agent not implemented yet, using generic answer creator")
            return AnswerCreator(**kwargs)
        elif agent_type == AnswerAgentType.SYSTEM_DESIGN:
            # Future implementation - for now, use generic
            self.logger.warning("System Design agent not implemented yet, using generic answer creator")
            return AnswerCreator(**kwargs)
        else:
            self.logger.warning(f"Unknown agent type {agent_type}, using generic answer creator")
            return AnswerCreator(**kwargs)
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for sheet management."""
        return {
            "create_sheet_meta": PromptTemplate(
                input_variables=["topic", "roadmap", "requirements"],
                template="""
You are an expert interview content manager for The Boring Education. Create comprehensive meta information for an interview sheet.

Topic: {topic}
Roadmap: {roadmap}
Requirements: {requirements}

Create a detailed meta description that covers:
1. What this interview sheet covers
2. Key areas and technologies included
3. Target audience and difficulty level
4. Real-world application and importance
5. Expected interview scenarios

Make it engaging, informative, and professional. Keep it under 200 words.

Meta Description:
"""
            ),
            "analyze_mdx_requirements": PromptTemplate(
                input_variables=["mdx_content"],
                template="""
You are an expert interview content analyst. Analyze the following MDX content and extract key requirements for interview sheet generation.

MDX Content:
{mdx_content}

Please analyze and provide:
1. **Topic/Technology**: What technology or topic this covers
2. **Target Audience**: Who this is for (freshers, mid-level, senior)
3. **Content Style**: Technical depth, practical focus, etc.
4. **Question Categories**: What types of questions needed
5. **Special Requirements**: Any specific focus areas
6. **Difficulty Level**: Beginner/Intermediate/Advanced
7. **Interview Context**: What kind of interviews this prepares for

Provide your analysis in a structured format.
"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "create_sheet_from_mdx":
            return self.create_sheet_from_mdx(kwargs.get("mdx_filepath"))
        elif content_type == "add_metadata_to_mdx":
            return self.metadata_agent.add_metadata_to_mdx(
                kwargs.get("mdx_filepath"),
                kwargs.get("topic", "General Tech")
            )
        elif content_type == "generate_answers_from_mdx":
            return self.generate_answers_from_mdx(kwargs.get("mdx_filepath"))
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def create_sheet_from_mdx(self, mdx_filepath: str) -> Dict[str, Any]:
        """Create interview sheet structure from MDX requirements."""
        console.print(f"[green]🎯 Creating interview sheet from MDX: {mdx_filepath}[/green]")
        
        try:
            # Load MDX content
            with open(mdx_filepath, 'r', encoding='utf-8') as f:
                mdx_content = f.read()
            
            # Analyze MDX requirements
            analysis_prompt = self._format_prompt("analyze_mdx_requirements", mdx_content=mdx_content)
            analysis_result = self._generate_with_prompt(analysis_prompt)
            requirements = self._parse_analysis_result(analysis_result)
            
            # Extract topic from MDX
            topic = self._extract_topic_from_mdx(mdx_content)
            
            # Generate sheet metadata
            meta_prompt = self._format_prompt("create_sheet_meta", 
                                            topic=topic,
                                            roadmap=requirements.get("roadmap", "Tech"),
                                            requirements=str(requirements))
            meta_content = self._generate_with_prompt(meta_prompt)
            
            # Create sheet structure
            sheet_data = {
                "id": self._generate_id(),
                "name": f"{topic} Interview Questions",
                "slug": self._generate_slug(topic),
                "description": meta_content,
                "roadmap": requirements.get("roadmap", "Tech"),
                "difficulty": requirements.get("difficulty_level", "Intermediate"),
                "target_audience": requirements.get("target_audience", "Developers"),
                "question_count": 0,
                "questions": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "cover_image_url": self._generate_cover_image_url(topic),
                "meta_content": meta_content,
                "requirements": requirements
            }
            
            # Save sheet structure
            filename = f"sheet_{self._generate_slug(topic)}.json"
            filepath = os.path.join(config.output_dir, filename)
            save_json_file(sheet_data, filepath)
            
            console.print(f"[green]✅ Sheet structure created: {filepath}[/green]")
            
            return {
                "status": "success",
                "sheet_data": sheet_data,
                "filepath": filepath,
                "topic": topic,
                "requirements": requirements
            }
            
        except Exception as e:
            self.logger.error(f"Error creating sheet from MDX: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def add_metadata_to_mdx(self, mdx_filepath: str) -> Dict[str, Any]:
        """Add metadata to questions in MDX file."""
        console.print(f"[green]🎯 Adding metadata to questions in MDX...[/green]")
        
        try:
            # Use the metadata agent to add metadata
            result = self.metadata_agent.add_metadata_to_mdx(mdx_filepath)
            
            if result["status"] == "success":
                console.print(f"[green]✅ Metadata added successfully![/green]")
                console.print(f"[blue]📁 Enhanced MDX: {result['enhanced_filepath']}[/blue]")
                console.print(f"[blue]📊 Questions processed: {result['questions_count']}[/blue]")
                
                console.print(f"\n[yellow]⚠️  Review the enhanced MDX file[/yellow]")
                console.print(f"[green]Then run: python main.py interview generate-answers-from-mdx --mdx-file {result['enhanced_filepath']}[/green]")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error adding metadata: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def generate_answers_from_mdx(self, mdx_filepath: str) -> Dict[str, Any]:
        """Generate answers for questions from MDX file with progressive saving."""
        console.print(f"[green]🎯 Generating answers from MDX questions...[/green]")
        
        try:
            # Load MDX content
            with open(mdx_filepath, 'r', encoding='utf-8') as f:
                mdx_content = f.read()
            
            # Parse questions from MDX
            questions = self._parse_questions_from_mdx(mdx_content)
            topic = self._extract_topic_from_mdx(mdx_content)
            
            if not questions:
                return {
                    "status": "error",
                    "message": "No questions found in MDX file"
                }
            
            # Check for existing progress
            progress_filepath = self._get_progress_filepath(mdx_filepath)
            progress_data = self._load_progress(progress_filepath)
            
            if progress_data:
                console.print(f"[yellow]📋 Found existing progress: {progress_data['completed_questions']}/{progress_data['total_questions']} questions completed[/yellow]")
                if console.input("[yellow]Resume from where you left off? (y/n): [/yellow]").lower() == 'y':
                    return self._resume_generation(progress_data, questions, topic, mdx_filepath)
                else:
                    # Start fresh - remove old progress
                    self._cleanup_progress(progress_filepath)
            
            # Start fresh generation
            return self._generate_answers_with_progress(questions, topic, mdx_filepath)
            
        except Exception as e:
            self.logger.error(f"Error generating answers: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _generate_answers_with_progress(self, questions: List[Dict[str, Any]], topic: str, mdx_filepath: str) -> Dict[str, Any]:
        """Generate answers with progressive saving."""
        progress_filepath = self._get_progress_filepath(mdx_filepath)
        total_questions = len(questions)
        
        # Initialize progress data
        progress_data = {
            "session_id": self._generate_id(),
            "mdx_filepath": mdx_filepath,
            "topic": topic,
            "agent_type": self.agent_type.value,
            "total_questions": total_questions,
            "completed_questions": 0,
            "current_question_index": 0,
            "answered_questions": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "status": "in_progress"
        }
        
        # Save initial progress
        self._save_progress(progress_data, progress_filepath)
        console.print(f"[blue]💾 Progress tracking initialized: {progress_filepath}[/blue]")
        
        # Generate answers with progress tracking
        with Progress() as progress:
            task = progress.add_task(f"[green]Generating {self.agent_type.value} answers...", total=total_questions)
            
            for i, question_data in enumerate(questions):
                try:
                    progress.update(task, description=f"[green]Question {i+1}/{total_questions}: {question_data['question'][:40]}...")
                    
                    # Generate answer
                    answer = self.answer_creator.generate_answer(
                        question=question_data['question'],
                        topic=topic,
                        difficulty=question_data.get('difficulty', 'Medium'),
                        frequency=question_data.get('frequency', 'Medium'),
                        priority=question_data.get('priority', 'Medium'),
                        company_types=question_data.get('company_types', ['Startup', 'MNC'])
                    )
                    
                    # Apply MDX styling
                    styled_answer = self.mdx_styler.format_mdx_content(answer, "interview_answer")
                    
                    # Create completed question entry
                    completed_question = {
                        **question_data,
                        "title": question_data['question'][:100],  # Add title field (max 100 chars)
                        "answer": styled_answer,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "question_index": i
                    }
                    
                    # Update progress data
                    progress_data["answered_questions"].append(completed_question)
                    progress_data["completed_questions"] = i + 1
                    progress_data["current_question_index"] = i + 1
                    progress_data["last_updated"] = datetime.now(timezone.utc).isoformat()
                    
                    # Save progress after each question
                    self._save_progress(progress_data, progress_filepath)
                    
                    # Update progress bar
                    progress.update(task, advance=1)
                    console.print(f"[green]✅ Question {i+1}/{total_questions} completed and saved[/green]")
                    
                except Exception as e:
                    self.logger.error(f"Error generating answer for question {i+1}: {str(e)}")
                    console.print(f"[red]❌ Failed to generate answer for question {i+1}: {str(e)}[/red]")
                    
                    # Save progress even on failure
                    progress_data["last_updated"] = datetime.now(timezone.utc).isoformat()
                    progress_data["last_error"] = str(e)
                    self._save_progress(progress_data, progress_filepath)
                    
                    # Ask user if they want to continue
                    if not console.input("[yellow]Continue with next question? (y/n): [/yellow]").lower() == 'y':
                        break
        
        # Mark as completed and create final sheet
        progress_data["status"] = "completed"
        progress_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._save_progress(progress_data, progress_filepath)
        
        # Create final complete sheet
        final_result = self._create_final_sheet(progress_data, topic)
        
        # Cleanup progress file after successful completion
        self._cleanup_progress(progress_filepath)
        
        return final_result
    
    def _resume_generation(self, progress_data: Dict[str, Any], questions: List[Dict[str, Any]], topic: str, mdx_filepath: str) -> Dict[str, Any]:
        """Resume generation from existing progress."""
        progress_filepath = self._get_progress_filepath(mdx_filepath)
        start_index = progress_data["completed_questions"]
        total_questions = len(questions)
        
        console.print(f"[green]🔄 Resuming from question {start_index + 1}/{total_questions}[/green]")
        
        # Continue generating from where we left off
        with Progress() as progress:
            task = progress.add_task(f"[green]Resuming {self.agent_type.value} answers...", total=total_questions - start_index)
            
            for i in range(start_index, total_questions):
                question_data = questions[i]
                
                try:
                    progress.update(task, description=f"[green]Question {i+1}/{total_questions}: {question_data['question'][:40]}...")
                    
                    # Generate answer
                    answer = self.answer_creator.generate_answer(
                        question=question_data['question'],
                        topic=topic,
                        difficulty=question_data.get('difficulty', 'Medium'),
                        frequency=question_data.get('frequency', 'Medium'),
                        priority=question_data.get('priority', 'Medium'),
                        company_types=question_data.get('company_types', ['Startup', 'MNC'])
                    )
                    
                    # Apply MDX styling
                    styled_answer = self.mdx_styler.format_mdx_content(answer, "interview_answer")
                    
                    # Create completed question entry
                    completed_question = {
                        **question_data,
                        "title": question_data['question'][:100],  # Add title field (max 100 chars)
                        "answer": styled_answer,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "question_index": i
                    }
                    
                    # Update progress data
                    progress_data["answered_questions"].append(completed_question)
                    progress_data["completed_questions"] = i + 1
                    progress_data["current_question_index"] = i + 1
                    progress_data["last_updated"] = datetime.now(timezone.utc).isoformat()
                    
                    # Save progress after each question
                    self._save_progress(progress_data, progress_filepath)
                    
                    # Update progress bar
                    progress.update(task, advance=1)
                    console.print(f"[green]✅ Question {i+1}/{total_questions} completed and saved[/green]")
                    
                except Exception as e:
                    self.logger.error(f"Error generating answer for question {i+1}: {str(e)}")
                    console.print(f"[red]❌ Failed to generate answer for question {i+1}: {str(e)}[/red]")
                    
                    # Save progress even on failure
                    progress_data["last_updated"] = datetime.now(timezone.utc).isoformat()
                    progress_data["last_error"] = str(e)
                    self._save_progress(progress_data, progress_filepath)
                    
                    # Ask user if they want to continue
                    if not console.input("[yellow]Continue with next question? (y/n): [/yellow]").lower() == 'y':
                        break
        
        # Mark as completed and create final sheet
        progress_data["status"] = "completed"
        progress_data["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._save_progress(progress_data, progress_filepath)
        
        # Create final complete sheet
        final_result = self._create_final_sheet(progress_data, topic)
        
        # Cleanup progress file after successful completion
        self._cleanup_progress(progress_filepath)
        
        return final_result
    
    def _create_final_sheet(self, progress_data: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Create final sheet from progress data."""
        answered_questions = progress_data["answered_questions"]
        
        # Create complete sheet
        sheet_data = {
            "id": self._generate_id(),
            "name": f"{topic} Interview Questions",
            "slug": self._generate_slug(topic),
            "description": f"Comprehensive {topic} interview questions with detailed answers",
            "roadmap": "Tech",
            "difficulty": "Intermediate",
            "target_audience": "Developers",
            "question_count": len(answered_questions),
            "questions": answered_questions,
            "created_at": progress_data["started_at"],
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "cover_image_url": self._generate_cover_image_url(topic),
            "generation_metadata": {
                "agent_type": progress_data["agent_type"],
                "session_id": progress_data["session_id"],
                "total_generation_time": progress_data.get("completed_at", datetime.now(timezone.utc).isoformat())
            }
        }
        
        # Save complete sheet
        filename = f"complete_sheet_{self._generate_slug(topic)}.json"
        filepath = os.path.join(config.output_dir, filename)
        save_json_file(sheet_data, filepath)
        
        console.print(f"[green]✅ Final sheet created successfully![/green]")
        console.print(f"[blue]📁 Complete sheet: {filepath}[/blue]")
        console.print(f"[blue]📊 Questions processed: {len(answered_questions)}[/blue]")
        
        console.print(f"\n[yellow]🎯 Ready for database publication![/yellow]")
        console.print(f"[green]Run: python main.py interview publish-sheet --sheet-file {filepath} --sheet-id your_sheet_id[/green]")
        
        return {
            "status": "success",
            "sheet_data": sheet_data,
            "filepath": filepath,
            "questions_count": len(answered_questions),
            "topic": topic
        }
    
    def _get_progress_filepath(self, mdx_filepath: str) -> str:
        """Get progress file path for given MDX file."""
        base_name = os.path.splitext(os.path.basename(mdx_filepath))[0]
        return os.path.join(config.temp_dir, f"progress_{base_name}_{self.agent_type.value}.json")
    
    def _load_progress(self, progress_filepath: str) -> Optional[Dict[str, Any]]:
        """Load existing progress data."""
        try:
            if os.path.exists(progress_filepath):
                return load_json_file(progress_filepath)
        except Exception as e:
            self.logger.warning(f"Could not load progress file: {str(e)}")
        return None
    
    def _save_progress(self, progress_data: Dict[str, Any], progress_filepath: str) -> None:
        """Save progress data."""
        try:
            # Ensure temp directory exists
            os.makedirs(config.temp_dir, exist_ok=True)
            save_json_file(progress_data, progress_filepath)
        except Exception as e:
            self.logger.error(f"Could not save progress: {str(e)}")
    
    def _cleanup_progress(self, progress_filepath: str) -> None:
        """Clean up progress file after completion."""
        try:
            if os.path.exists(progress_filepath):
                os.remove(progress_filepath)
                console.print(f"[blue]🗑️  Progress file cleaned up[/blue]")
        except Exception as e:
            self.logger.warning(f"Could not clean up progress file: {str(e)}")
    
    def list_active_sessions(self) -> Dict[str, Any]:
        """List all active generation sessions."""
        try:
            if not os.path.exists(config.temp_dir):
                return {"status": "success", "sessions": []}
            
            sessions = []
            for filename in os.listdir(config.temp_dir):
                if filename.startswith("progress_") and filename.endswith(".json"):
                    try:
                        filepath = os.path.join(config.temp_dir, filename)
                        progress_data = load_json_file(filepath)
                        
                        sessions.append({
                            "session_id": progress_data.get("session_id", "unknown"),
                            "topic": progress_data.get("topic", "unknown"),
                            "agent_type": progress_data.get("agent_type", "unknown"),
                            "progress": f"{progress_data.get('completed_questions', 0)}/{progress_data.get('total_questions', 0)}",
                            "status": progress_data.get("status", "unknown"),
                            "last_updated": progress_data.get("last_updated", "unknown"),
                            "filepath": filepath
                        })
                    except Exception as e:
                        self.logger.warning(f"Could not read progress file {filename}: {str(e)}")
            
            return {"status": "success", "sessions": sessions}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def resume_session(self, session_filepath: str) -> Dict[str, Any]:
        """Resume a specific session by filepath."""
        try:
            progress_data = load_json_file(session_filepath)
            mdx_filepath = progress_data.get("mdx_filepath")
            
            if not mdx_filepath or not os.path.exists(mdx_filepath):
                return {
                    "status": "error",
                    "message": "Original MDX file not found"
                }
            
            # Load questions and resume
            with open(mdx_filepath, 'r', encoding='utf-8') as f:
                mdx_content = f.read()
            
            questions = self._parse_questions_from_mdx(mdx_content)
            topic = progress_data.get("topic", self._extract_topic_from_mdx(mdx_content))
            
            return self._resume_generation(progress_data, questions, topic, mdx_filepath)
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Could not resume session: {str(e)}"
            }

    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """Parse analysis result into structured format."""
        requirements = {
            "topic": "General Tech",
            "target_audience": "Developers",
            "content_style": "Technical",
            "question_categories": "Fundamentals, Advanced",
            "special_requirements": "",
            "difficulty_level": "Intermediate",
            "roadmap": "Tech"
        }
        
        # Extract key information from analysis
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if key in requirements:
                    requirements[key] = value
        
        return requirements
    
    def _extract_topic_from_mdx(self, mdx_content: str) -> str:
        """Extract topic from MDX content."""
        lines = mdx_content.split('\n')
        for line in lines:
            if line.startswith('# ') and 'Interview' in line:
                return line.replace('# ', '').replace(' Interview Questions', '').strip()
        
        # Fallback: extract from first heading
        for line in lines:
            if line.startswith('# '):
                return line.replace('# ', '').strip()
        
        return "General Tech"
    
    def _parse_questions_from_mdx(self, mdx_content: str) -> List[Dict[str, Any]]:
        """Parse questions from MDX content."""
        questions = []
        lines = mdx_content.split('\n')
        
        current_question = None
        for original_line in lines:
            line = original_line.strip()  # Keep original for indentation checking
            
            if line.startswith('- Question:'):
                if current_question:
                    questions.append(current_question)
                
                question_text = line.replace('- Question:', '').strip()
                current_question = {
                    "question": question_text,
                    "difficulty": "Medium",
                    "frequency": "Medium",
                    "priority": "Medium",
                    "company_types": ["Startup", "MNC"]
                }
            
            elif original_line.startswith('  - Difficulty:') and current_question:
                current_question["difficulty"] = line.replace('- Difficulty:', '').strip()
            elif original_line.startswith('  - Frequency:') and current_question:
                current_question["frequency"] = line.replace('- Frequency:', '').strip()
            elif original_line.startswith('  - Priority:') and current_question:
                current_question["priority"] = line.replace('- Priority:', '').strip()
            elif original_line.startswith('  - Company Types:') and current_question:
                company_types = line.replace('- Company Types:', '').strip()
                current_question["company_types"] = [ct.strip() for ct in company_types.split(',')]
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _format_questions_for_mdx(self, questions: List[Dict[str, Any]]) -> str:
        """Format questions for MDX output."""
        formatted = ""
        for i, q in enumerate(questions, 1):
            formatted += f"""
### Question {i}

- Question: {q['question']}
  - Difficulty: {q.get('difficulty', 'Medium')}
  - Frequency: {q.get('frequency', 'Medium')}
  - Priority: {q.get('priority', 'Medium')}
  - Company Types: {', '.join(q.get('company_types', ['Startup', 'MNC']))}

"""
        return formatted
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _generate_slug(self, name: str) -> str:
        """Generate slug from name."""
        return name.lower().replace(' ', '-').replace('_', '-')
    
    def _generate_cover_image_url(self, topic: str) -> str:
        """Generate cover image URL."""
        return f"https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=800&h=400&fit=crop&crop=center" 