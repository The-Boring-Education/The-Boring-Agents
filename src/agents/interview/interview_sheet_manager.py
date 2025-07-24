"""Interview Sheet Manager - Main coordinator for interview sheet lifecycle."""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate
from rich.console import Console

from ...core.base_agent import BaseAgent
from ...core.config import config
from ...utils.helpers import generate_filename, save_json_file, load_json_file
from ...utils.validation import InterviewQuestionValidator
from .answer_creator import AnswerCreator
from .metadata_agent import MetadataAgent
from .mdx_styling_agent import MDXStylingAgent

console = Console()


class InterviewSheetManager(BaseAgent):
    """Main manager for interview sheet lifecycle - creation, generation, review, and publication."""
    
    def __init__(self, **kwargs):
        """Initialize the sheet manager with streamlined agents."""
        super().__init__(**kwargs)
        
        # Initialize only essential agents for quality
        self.answer_creator = AnswerCreator(**kwargs)
        self.metadata_agent = MetadataAgent(**kwargs)
        self.mdx_styler = MDXStylingAgent(**kwargs)
        
        self.logger.info("Interview Sheet Manager initialized with streamlined agents")
    
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
        """Generate answers for questions from MDX file."""
        console.print(f"[green]🎯 Generating answers from MDX questions...[/green]")
        
        try:
            # Load MDX content
            with open(mdx_filepath, 'r', encoding='utf-8') as f:
                mdx_content = f.read()
            
            # Parse questions from MDX
            questions = self._parse_questions_from_mdx(mdx_content)
            topic = self._extract_topic_from_mdx(mdx_content)
            
            # Generate answers for each question
            answered_questions = []
            for i, question_data in enumerate(questions):
                console.print(f"[yellow]Generating answer {i+1}/{len(questions)}: {question_data['question'][:50]}...[/yellow]")
                
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
                
                answered_questions.append({
                    **question_data,
                    "answer": styled_answer,
                    "created_at": datetime.now(timezone.utc).isoformat()
                })
            
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
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "cover_image_url": self._generate_cover_image_url(topic)
            }
            
            # Save complete sheet
            filename = f"complete_sheet_{self._generate_slug(topic)}.json"
            filepath = os.path.join(config.output_dir, filename)
            save_json_file(sheet_data, filepath)
            
            console.print(f"[green]✅ Answers generated successfully![/green]")
            console.print(f"[blue]📁 Complete sheet: {filepath}[/blue]")
            console.print(f"[blue]📊 Questions processed: {len(answered_questions)}[/blue]")
            
            return {
                "status": "success",
                "sheet_data": sheet_data,
                "filepath": filepath,
                "questions_count": len(answered_questions),
                "topic": topic
            }
            
        except Exception as e:
            self.logger.error(f"Error generating answers: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
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
        for line in lines:
            line = line.strip()
            
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
            
            elif line.startswith('  - Difficulty:') and current_question:
                current_question["difficulty"] = line.replace('  - Difficulty:', '').strip()
            elif line.startswith('  - Frequency:') and current_question:
                current_question["frequency"] = line.replace('  - Frequency:', '').strip()
            elif line.startswith('  - Priority:') and current_question:
                current_question["priority"] = line.replace('  - Priority:', '').strip()
            elif line.startswith('  - Company Types:') and current_question:
                company_types = line.replace('  - Company Types:', '').strip()
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