"""
Interview Sheet Creator Agent for phased interview sheet creation.
Handles the complete lifecycle from initial sheet creation to final database update.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate
from rich.console import Console
import click

from src.core.base_agent import BaseAgent
from src.core.config import config
from src.utils.helpers import generate_filename, save_json_file, load_json_file

console = Console()


class InterviewSheetCreator(BaseAgent):
    """Agent for creating interview sheets in phases."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for interview sheet creation."""
        return {
            "create_sheet_meta": PromptTemplate(
                input_variables=["topic", "roadmap"],
                template="""
You are an expert interview content creator for The Boring Education. Create comprehensive meta information for an interview sheet.

Topic: {topic}
Roadmap: {roadmap}

Create a detailed meta description that covers:
1. What this interview sheet covers
2. Key areas and technologies included
3. Target audience and difficulty level
4. Real-world application and importance

Make it engaging, informative, and professional. Keep it under 200 words.

Meta Description:
"""
            ),
            "generate_questions_list": PromptTemplate(
                input_variables=["topic", "roadmap", "target_count"],
                template="""
You are an expert interview question generator with 20+ years of experience conducting 300+ interviews.

Generate a comprehensive list of interview questions for: {topic}
Roadmap: {roadmap}
Target Count: {target_count} questions

Requirements:
1. Focus on REAL questions asked in actual interviews
2. Cover fundamental concepts, advanced topics, and practical scenarios
3. Include questions from different difficulty levels (Beginner, Intermediate, Advanced)
4. Consider questions asked by different company types (Startup, MidSize, MNC, FAANG)
5. Include coding problems, system design questions, and behavioral questions
6. Prioritize questions by frequency and importance

Format each question as:
- Question: [The actual question]
- Category: [Fundamentals/Advanced/Practical/System Design/Behavioral]
- Difficulty: [Beginner/Intermediate/Advanced]
- Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
- Priority: [High/Medium/Low]
- CompanyTypes: [Startup, MidSize, MNC, FAANG] (select 2-3 most relevant)

Generate exactly {target_count} high-quality questions.
"""
            ),
            "generate_answer": PromptTemplate(
                input_variables=["question", "topic", "difficulty"],
                template="""
You are an expert technical interviewer and educator with 20+ years of experience.

Generate a comprehensive answer for this interview question:

Question: {question}
Topic: {topic}
Difficulty: {difficulty}

Requirements:
1. Provide a detailed, step-by-step explanation
2. Include code examples where applicable
3. Explain the reasoning and concepts clearly
4. Add real-world examples and use cases
5. Include common pitfalls and best practices
6. Make it suitable for Indian tech industry context
7. Add memory tricks or mnemonics if helpful
8. Include follow-up questions that might be asked

Write a comprehensive answer that would help a candidate ace this question in an interview.
"""
            ),
            "validate_sheet": PromptTemplate(
                input_variables=["sheet_data"],
                template="""
You are a quality assurance expert for interview content.

Review this interview sheet data and validate it for database publication:

{sheet_data}

Check for:
1. Complete required fields (name, slug, description, roadmap, questions)
2. Valid question format with all required fields
3. Proper answer quality and completeness
4. Appropriate difficulty distribution
5. Good coverage of topics
6. Professional and accurate content

Provide validation results with any issues found.
"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "create_sheet":
            return self.create_interview_sheet(**kwargs)
        elif content_type == "generate_questions":
            return self.generate_questions_list(**kwargs)
        elif content_type == "generate_answers":
            return self.generate_answers_for_questions(**kwargs)
        elif content_type == "validate_sheet":
            return self.validate_sheet_for_publication(**kwargs)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def create_interview_sheet(self, topic: str, roadmap: str = "Tech") -> Dict[str, Any]:
        """Phase 1: Create initial interview sheet structure."""
        console.print(f"[green]Creating interview sheet for: {topic}[/green]")
        
        # Generate meta description
        meta_prompt = self._format_prompt("create_sheet_meta", topic=topic, roadmap=roadmap)
        meta_content = self._generate_with_prompt(meta_prompt)
        
        # Create sheet structure
        sheet_data = {
            "features": [],
            "name": f"{topic} Interview Questions",
            "slug": self._generate_slug(topic),
            "coverImageURL": self._generate_cover_image_url(topic),
            "description": f"Ace your {topic} Interview with Real Questions asked in Real Interviews.",
            "liveOn": datetime.now(timezone.utc).isoformat(),
            "roadmap": roadmap,
            "questions": [],
            "meta": meta_content.strip()
        }
        
        # Save to file
        filename = f"interview_sheet_{self._generate_slug(topic)}.json"
        filepath = os.path.join(config.output_dir, filename)
        save_json_file(sheet_data, filepath)
        
        console.print(f"[blue]Interview sheet created: {filepath}[/blue]")
        return {
            "status": "success",
            "sheet_data": sheet_data,
            "filepath": filepath
        }
    
    def generate_questions_list(self, topic: str, roadmap: str = "Tech", 
                              target_count: int = 50) -> Dict[str, Any]:
        """Phase 2: Generate list of questions and save to MDX."""
        console.print(f"[green]Generating {target_count} questions for: {topic}[/green]")
        
        # Generate questions
        questions_prompt = self._format_prompt("generate_questions_list", 
                                             topic=topic, roadmap=roadmap, target_count=target_count)
        questions_content = self._generate_with_prompt(questions_prompt)
        
        # Save to MDX file
        mdx_filename = f"questions_{self._generate_slug(topic)}.mdx"
        mdx_filepath = os.path.join(config.output_dir, mdx_filename)
        
        mdx_content = f"""# {topic} Interview Questions

## Generated Questions List

{questions_content}

## Instructions for Review
1. Review each question for accuracy and relevance
2. Add or remove questions as needed
3. Adjust difficulty levels if required
4. Ensure good coverage of topics
5. Save this file and run the next phase to generate answers

## Next Steps
Run: python main.py interview generate-answers --mdx-file {mdx_filepath}
"""
        
        with open(mdx_filepath, 'w', encoding='utf-8') as f:
            f.write(mdx_content)
        
        console.print(f"[blue]Questions list saved to: {mdx_filepath}[/blue]")
        return {
            "status": "success",
            "questions_content": questions_content,
            "mdx_filepath": mdx_filepath,
            "topic": topic,
            "roadmap": roadmap
        }
    
    def generate_answers_for_questions(self, mdx_filepath: str, 
                                     sheet_filepath: str = None) -> Dict[str, Any]:
        """Phase 3: Generate answers for questions from MDX file."""
        console.print(f"[green]Generating answers from: {mdx_filepath}[/green]")
        
        # Load questions from MDX
        with open(mdx_filepath, 'r', encoding='utf-8') as f:
            mdx_content = f.read()
        
        # Parse questions from MDX content
        questions = self._parse_questions_from_mdx(mdx_content)
        
        # Load existing sheet if provided
        sheet_data = None
        if sheet_filepath and os.path.exists(sheet_filepath):
            sheet_data = load_json_file(sheet_filepath)
        else:
            # Create new sheet data
            topic = self._extract_topic_from_mdx(mdx_content)
            sheet_data = self.create_interview_sheet(topic)["sheet_data"]
        
        # Generate answers for each question
        answered_questions = []
        for i, question_data in enumerate(questions):
            console.print(f"[yellow]Generating answer {i+1}/{len(questions)}: {question_data['question'][:50]}...[/yellow]")
            
            answer_prompt = self._format_prompt("generate_answer", 
                                              question=question_data['question'],
                                              topic=sheet_data['name'],
                                              difficulty=question_data.get('difficulty', 'Intermediate'))
            
            answer = self._generate_with_prompt(answer_prompt)
            
            # Create complete question object (including companyTypes for API)
            question_obj = {
                "question": question_data['question'],
                "answer": answer,
                "difficulty": question_data.get('difficulty', 'Intermediate'),
                "frequency": question_data.get('frequency', 'Asked Frequently'),
                "priority": question_data.get('priority', 'Medium'),
                "companyTypes": question_data.get('companyTypes', ['Startup', 'MidSize', 'MNC'])
            }
            
            answered_questions.append(question_obj)
        
        # Update sheet with questions
        sheet_data['questions'] = answered_questions
        
        # Save updated sheet
        filename = f"complete_sheet_{self._generate_slug(sheet_data['name'])}.json"
        filepath = os.path.join(config.output_dir, filename)
        save_json_file(sheet_data, filepath)
        
        console.print(f"[blue]Complete sheet with answers saved to: {filepath}[/blue]")
        return {
            "status": "success",
            "sheet_data": sheet_data,
            "filepath": filepath,
            "questions_count": len(answered_questions)
        }
    
    def validate_sheet_for_publication(self, sheet_filepath: str) -> Dict[str, Any]:
        """Phase 4: Validate sheet for database publication."""
        console.print(f"[green]Validating sheet for publication: {sheet_filepath}[/green]")
        
        # Load sheet data
        sheet_data = load_json_file(sheet_filepath)
        
        # Validate structure
        validation_result = self._validate_sheet_structure(sheet_data)
        
        if not validation_result["is_valid"]:
            return {
                "status": "error",
                "message": "Sheet validation failed",
                "errors": validation_result["errors"]
            }
        
        # Generate final sheet for database
        final_sheet = self._prepare_final_sheet(sheet_data)
        
        # Save final version
        filename = f"final_sheet_{self._generate_slug(sheet_data['name'])}.json"
        filepath = os.path.join(config.output_dir, filename)
        save_json_file(final_sheet, filepath)
        
        console.print(f"[blue]Final sheet ready for database: {filepath}[/blue]")
        return {
            "status": "success",
            "final_sheet": final_sheet,
            "filepath": filepath,
            "validation": validation_result
        }
    
    def publish_to_database(self, sheet_filepath: str, sheet_id: str = None) -> Dict[str, Any]:
        """Phase 5: Add questions to existing interview sheet."""
        console.print(f"[green]Adding questions to interview sheet: {sheet_filepath}[/green]")
        
        # Load final sheet
        sheet_data = load_json_file(sheet_filepath)
        
        try:
            import requests
            
            # Get sheet ID from parameter or prompt user
            if not sheet_id:
                sheet_id = click.prompt(
                    "Enter the interview sheet ID (e.g., 67345538bdf619907a005031)",
                    type=str
                )
            
            console.print(f"[blue]Using sheet ID: {sheet_id}[/blue]")
            
            # Verify sheet exists first
            console.print(f"[blue]Step 1: Verifying sheet exists...[/blue]")
            print(f"{config.api_v1_url}/interview-prep/{sheet_id}")
            sheet_response = requests.get(
                f"{config.api_v1_url}/interview-prep/{sheet_id}",
                headers={
                    "Content-Type": "application/json",
                    "x-admin-secret": "TBEAdmin"
                }
            )
            
            if sheet_response.status_code != 200:
                console.print(f"[red]❌ Sheet not found: {sheet_response.status_code}[/red]")
                console.print(f"[red]Response: {sheet_response.text}[/red]")
                return {
                    "status": "error",
                    "message": f"Sheet not found: {sheet_response.status_code}. Please create the sheet first."
                }
            
            console.print(f"[green]✅ Sheet verified: {sheet_data['name']}[/green]")
            
            # Step 2: Add questions one by one
            console.print(f"[blue]Step 2: Adding {len(sheet_data['questions'])} questions...[/blue]")
            
            successful_questions = 0
            failed_questions = 0
            
            for i, question in enumerate(sheet_data["questions"]):
                console.print(f"[yellow]Adding question {i+1}/{len(sheet_data['questions'])}: {question['question'][:50]}...[/yellow]")
                
                question_payload = {
                    "title": question["question"],
                    "question": question["question"],
                    "answer": question["answer"],
                    "frequency": question["frequency"],
                    "companyTypes": question.get("companyTypes", ["Startup", "MidSize", "MNC"])
                }
                
                # Add question API call
                question_response = requests.post(
                    f"{config.api_v1_url}/interview-prep/{sheet_id}/question",
                    headers={
                        "Content-Type": "application/json",
                        "x-admin-secret": "TBEAdmin"
                    },
                    json=question_payload
                )
                
                if question_response.status_code == 201:
                    successful_questions += 1
                    console.print(f"[green]✅ Question {i+1} added successfully[/green]")
                else:
                    failed_questions += 1
                    console.print(f"[red]❌ Failed to add question {i+1}: {question_response.status_code}[/red]")
                    console.print(f"[red]Response: {question_response.text}[/red]")
            
            console.print(f"\n[bold]📊 Publication Summary:[/bold]")
            console.print(f"[green]✅ Successful questions: {successful_questions}[/green]")
            if failed_questions > 0:
                console.print(f"[red]❌ Failed questions: {failed_questions}[/red]")
            
            return {
                "status": "success",
                "message": f"Questions added successfully to sheet with {successful_questions} questions",
                "sheet_id": sheet_id,
                "api_url": f"{config.api_v1_url}/interview-prep/{sheet_id}",
                "successful_questions": successful_questions,
                "failed_questions": failed_questions
            }
            
        except requests.exceptions.RequestException as e:
            console.print(f"[red]❌ Network error: {str(e)}[/red]")
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            console.print(f"[red]❌ Error adding questions to database: {str(e)}[/red]")
            return {
                "status": "error",
                "message": f"Error adding questions to database: {str(e)}"
            }
    
    def _parse_questions_from_mdx(self, mdx_content: str) -> List[Dict[str, Any]]:
        """Parse questions from MDX content."""
        questions = []
        lines = mdx_content.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            
            # Handle numbered format (1. Question: ...)
            if line.startswith('- Question:') or (line and line[0].isdigit() and '. Question:' in line):
                if current_question:
                    questions.append(current_question)
                # Extract question text, handling both formats
                if line.startswith('- Question:'):
                    question_text = line.replace('- Question:', '').strip()
                else:
                    # Handle numbered format: "1. Question: What is..."
                    question_text = line.split('. Question:', 1)[1].strip()
                current_question = {'question': question_text}
            elif line.startswith('- Category:') or (line and 'Category:' in line):
                if line.startswith('- Category:'):
                    current_question['category'] = line.replace('- Category:', '').strip()
                else:
                    current_question['category'] = line.split('Category:', 1)[1].strip()
            elif line.startswith('- Difficulty:') or (line and 'Difficulty:' in line):
                if line.startswith('- Difficulty:'):
                    current_question['difficulty'] = line.replace('- Difficulty:', '').strip()
                else:
                    current_question['difficulty'] = line.split('Difficulty:', 1)[1].strip()
            elif line.startswith('- Frequency:') or (line and 'Frequency:' in line):
                if line.startswith('- Frequency:'):
                    current_question['frequency'] = line.replace('- Frequency:', '').strip()
                else:
                    current_question['frequency'] = line.split('Frequency:', 1)[1].strip()
            elif line.startswith('- Priority:') or (line and 'Priority:' in line):
                if line.startswith('- Priority:'):
                    current_question['priority'] = line.replace('- Priority:', '').strip()
                else:
                    current_question['priority'] = line.split('Priority:', 1)[1].strip()
            elif line.startswith('- CompanyTypes:') or (line and 'CompanyTypes:' in line):
                if line.startswith('- CompanyTypes:'):
                    company_types = line.replace('- CompanyTypes:', '').strip()
                else:
                    company_types = line.split('CompanyTypes:', 1)[1].strip()
                current_question['companyTypes'] = [ct.strip() for ct in company_types.split(',')]
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _extract_topic_from_mdx(self, mdx_content: str) -> str:
        """Extract topic from MDX content."""
        lines = mdx_content.split('\n')
        for line in lines:
            if line.startswith('# ') and 'Interview Questions' in line:
                return line.replace('# ', '').replace(' Interview Questions', '').strip()
        return "Unknown Topic"
    
    def _validate_sheet_structure(self, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sheet structure for publication."""
        errors = []
        
        required_fields = ['name', 'slug', 'description', 'roadmap', 'questions']
        for field in required_fields:
            if field not in sheet_data:
                errors.append(f"Missing required field: {field}")
        
        if 'questions' in sheet_data:
            for i, question in enumerate(sheet_data['questions']):
                question_required = ['question', 'answer', 'difficulty', 'frequency', 'priority']
                for field in question_required:
                    if field not in question:
                        errors.append(f"Question {i+1} missing required field: {field}")
                
                # Check for unwanted fields (companyTypes is now allowed)
                unwanted_fields = ['category', 'roadmap']
                for field in unwanted_fields:
                    if field in question:
                        console.print(f"[yellow]⚠️  Question {i+1} contains unwanted field: {field}[/yellow]")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def _prepare_final_sheet(self, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare final sheet for database publication."""
        # Clean questions to remove unwanted fields but keep companyTypes
        cleaned_questions = []
        for question in sheet_data.get("questions", []):
            cleaned_question = {
                "question": question.get("question"),
                "answer": question.get("answer"),
                "difficulty": question.get("difficulty"),
                "frequency": question.get("frequency"),
                "priority": question.get("priority"),
                "companyTypes": question.get("companyTypes", ['Startup', 'MidSize', 'MNC'])
            }
            cleaned_questions.append(cleaned_question)
        
        # Ensure all required fields are present
        final_sheet = {
            "features": sheet_data.get("features", []),
            "name": sheet_data.get("name"),
            "slug": sheet_data.get("slug"),
            "coverImageURL": sheet_data.get("coverImageURL"),
            "description": sheet_data.get("description"),
            "liveOn": sheet_data.get("liveOn"),
            "roadmap": sheet_data.get("roadmap"),
            "questions": cleaned_questions,
            "meta": sheet_data.get("meta", "")
        }
        
        return final_sheet
    
    def _generate_id(self) -> str:
        """Generate a unique ID."""
        import uuid
        return str(uuid.uuid4()).replace('-', '')[:24]
    
    def _generate_slug(self, name: str) -> str:
        """Generate a slug from name."""
        return name.lower().replace(' ', '-').replace('_', '-').replace('.', '')
    
    def _generate_cover_image_url(self, topic: str) -> str:
        """Generate cover image URL."""
        slug = self._generate_slug(topic)
        return f"https://ik.imagekit.io/tbe/webapp/{slug}-interview-questions.svg" 