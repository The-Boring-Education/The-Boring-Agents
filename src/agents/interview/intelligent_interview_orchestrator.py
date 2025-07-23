"""
Intelligent Interview Orchestrator - Advanced agentic system for adaptive interview content generation.
Supports different interview types (DSA, Python, Java, etc.) with MDX-based workflow and human review.
"""

import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from langchain.prompts import PromptTemplate
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import click

from ...core.base_agent import BaseAgent
from ...core.config import config
from ...utils.helpers import generate_filename, save_json_file, load_json_file
from .interview_sheet_creator import InterviewSheetCreator
from .mdx_styling_agent import MDXStylingAgent
from .database_integration_agent import DatabaseIntegrationAgent

console = Console()


class IntelligentInterviewOrchestrator(BaseAgent):
    """Advanced orchestrator for intelligent interview content generation with MDX workflow."""
    
    def __init__(self, **kwargs):
        """Initialize the intelligent orchestrator."""
        super().__init__(**kwargs)
        
        # Initialize specialized agents
        self.sheet_creator = InterviewSheetCreator(**kwargs)
        self.mdx_styler = MDXStylingAgent(**kwargs)
        self.db_agent = DatabaseIntegrationAgent(**kwargs)
        
        self.logger.info("Intelligent Interview Orchestrator initialized")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for intelligent interview orchestration."""
        return {
            "analyze_mdx_requirements": PromptTemplate(
                input_variables=["mdx_content"],
                template="""
You are an expert interview content strategist with 20+ years of experience in tech education.

Analyze this MDX file content and determine the interview sheet requirements:

{mdx_content}

Extract and provide the following information in a structured format:

**Interview Sheet Type:** [DSA, Python, Java, Golang, Aptitude, System Design, General Tech]
**Target Audience:** [College students, Experienced developers, Data scientists, etc.]
**Content Style Requirements:** [Explain like 10-year-old for DSA, Technical depth for Python, etc.]
**Question Categories:** [Fundamentals, Advanced, Practical, System Design, etc.]
**Special Requirements:** [Coding examples, Real-world scenarios, Memory tricks, etc.]
**Heading Structure:** [Standard, DSA-specific, Python-specific, etc.]
**Content Tone:** [Educational, Technical, Interview-focused, etc.]

IMPORTANT: 
- For DSA: Focus on "Explain like teaching a 10-year-old", use analogies, memory tricks, step-by-step solutions
- For Python/Java: Focus on technical depth, best practices, real-world examples
- For System Design: Focus on architecture thinking, scalability, trade-offs
- For Aptitude: Focus on problem-solving approach, step-by-step methods

Return ONLY the structured format above with the actual values filled in.
"""
            ),
            "generate_adaptive_questions": PromptTemplate(
                input_variables=["sheet_type", "target_audience", "content_style", "question_categories", "special_requirements", "heading_structure", "content_tone", "topic", "count"],
                template="""
You are a world-class interview content creator specializing in {sheet_type} interviews.

**Sheet Type:** {sheet_type}
**Target Audience:** {target_audience}
**Content Style:** {content_style}
**Question Categories:** {question_categories}
**Special Requirements:** {special_requirements}
**Heading Structure:** {heading_structure}
**Content Tone:** {content_tone}
**Topic:** {topic}
**Target Count:** {count} questions

Generate {count} high-quality interview questions that:

1. **Match the Sheet Type** - Questions appropriate for {sheet_type}
2. **Target the Audience** - Suitable for {target_audience}
3. **Follow Content Style** - {content_style}
4. **Cover All Categories** - {question_categories}
5. **Include Special Requirements** - {special_requirements}
6. **Use Proper Headings** - {heading_structure}
7. **Maintain Tone** - {content_tone}

For each question, provide:
- Question: [The actual question]
- Category: [Appropriate category for this sheet type]
- Difficulty: [Beginner/Intermediate/Advanced]
- Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
- Priority: [High/Medium/Low]
- CompanyTypes: [Startup, MidSize, MNC, FAANG] (select 2-3 most relevant)
- SpecialNotes: [Any special considerations for this sheet type]

Generate exactly {count} questions that would make a {sheet_type} expert proud.
"""
            ),
            "generate_adaptive_answers": PromptTemplate(
                input_variables=["question", "sheet_type", "target_audience", "content_style", "heading_structure", "content_tone", "topic"],
                template="""
You are an expert {sheet_type} instructor and interviewer with 20+ years of experience.

Generate a comprehensive answer for this interview question:

**Question:** {question}
**Sheet Type:** {sheet_type}
**Target Audience:** {target_audience}
**Content Style:** {content_style}
**Heading Structure:** {heading_structure}
**Content Tone:** {content_tone}
**Topic:** {topic}

Create an answer that:

1. **Follows the Sheet Type Style** - {sheet_type} appropriate explanations
2. **Targets the Audience** - Suitable for {target_audience}
3. **Uses Content Style** - {content_style}
4. **Follows Heading Structure** - {heading_structure}
5. **Maintains Tone** - {content_tone}

For DSA: Explain concepts like teaching a 10-year-old, use analogies, focus on understanding
For Python/Java: Technical depth with practical examples, best practices, real-world usage
For Aptitude: Clear problem-solving approach, step-by-step methods, practice scenarios
For System Design: Architecture thinking, scalability considerations, trade-offs
For General Tech: Industry context, current trends, practical applications

Include:
- Clear explanations with examples
- Code snippets where appropriate
- Real-world scenarios
- Common pitfalls and best practices
- Interview tips and tricks
- Practice problems or follow-up questions

Write a comprehensive answer that would help a {target_audience} ace this {sheet_type} question.
"""
            ),
            "validate_adaptive_content": PromptTemplate(
                input_variables=["sheet_data", "sheet_type", "target_audience", "content_style"],
                template="""
You are a quality assurance expert for {sheet_type} interview content.

Review this interview sheet data for {sheet_type} targeting {target_audience}:

{sheet_data}

Content Style Requirements: {content_style}

Validate for:
1. **Sheet Type Appropriateness** - Content suitable for {sheet_type}
2. **Audience Targeting** - Appropriate for {target_audience}
3. **Content Style Compliance** - Follows {content_style}
4. **Question Quality** - Comprehensive and accurate
5. **Answer Completeness** - Detailed and helpful
6. **Technical Accuracy** - Correct information
7. **Interview Relevance** - Actually asked in interviews

Provide validation results with specific feedback for improvement.
"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "create_sheet_from_mdx":
            return self.create_sheet_from_mdx(**kwargs)
        elif content_type == "generate_questions_from_mdx":
            return self.generate_questions_from_mdx(**kwargs)
        elif content_type == "generate_answers_from_mdx":
            return self.generate_answers_from_mdx(**kwargs)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def create_sheet_from_mdx(self, mdx_filepath: str) -> Dict[str, Any]:
        """Step 1: Create sheet JSON from MDX file for database creation."""
        console.print(f"[green]🎯 Step 1: Creating sheet JSON from MDX file...[/green]")
        
        # Load MDX content
        with open(mdx_filepath, 'r', encoding='utf-8') as f:
            mdx_content = f.read()
        
        # Extract topic from MDX
        topic = self._extract_topic_from_mdx(mdx_content)
        
        # Analyze MDX content for meta information
        analysis_prompt = self._format_prompt("analyze_mdx_requirements", mdx_content=mdx_content)
        analysis_result = self._generate_with_prompt(analysis_prompt)
        requirements = self._parse_analysis_result(analysis_result)
        
        # Create sheet structure for database
        sheet_data = {
            "features": [],
            "name": f"{topic} Interview Questions",
            "slug": self._generate_slug(topic),
            "coverImageURL": self._generate_cover_image_url(topic),
            "description": f"Ace your {topic} Interview with Real Questions asked in Real Interviews.",
            "liveOn": datetime.now(timezone.utc).isoformat(),
            "roadmap": self._determine_roadmap_from_type(requirements.get("sheet_type", "General Tech")),
            "questions": [],
            "meta": self._generate_adaptive_meta_content(topic, requirements)
        }
        
        # Save sheet JSON
        sheet_filename = f"sheet_{self._generate_slug(topic)}.json"
        sheet_filepath = os.path.join(config.output_dir, sheet_filename)
        save_json_file(sheet_data, sheet_filepath)
        
        console.print(f"[blue]📁 Sheet JSON created: {sheet_filepath}[/blue]")
        console.print(f"[green]✅ Step 1 Complete! Sheet ready for database creation[/green]")
        
        return {
            "status": "success",
            "topic": topic,
            "sheet_data": sheet_data,
            "sheet_filepath": sheet_filepath,
            "requirements": requirements
        }
    
    def generate_questions_from_mdx(self, mdx_filepath: str, target_count: int = 50) -> Dict[str, Any]:
        """Step 2: Generate questions list in MDX file based on MDX requirements."""
        console.print(f"[green]🎯 Step 2: Generating {target_count} questions from MDX requirements...[/green]")
        
        # Load MDX content
        with open(mdx_filepath, 'r', encoding='utf-8') as f:
            mdx_content = f.read()
        
        # Analyze MDX requirements
        analysis_prompt = self._format_prompt("analyze_mdx_requirements", mdx_content=mdx_content)
        analysis_result = self._generate_with_prompt(analysis_prompt)
        requirements = self._parse_analysis_result(analysis_result)
        
        # Extract topic from MDX
        topic = self._extract_topic_from_mdx(mdx_content)
        
        # Generate questions based on MDX requirements
        questions_prompt = self._format_prompt("generate_adaptive_questions",
                                             sheet_type=requirements.get("sheet_type", "General Tech"),
                                             target_audience=requirements.get("target_audience", "Developers"),
                                             content_style=requirements.get("content_style", "Technical"),
                                             question_categories=requirements.get("question_categories", "Fundamentals, Advanced"),
                                             special_requirements=requirements.get("special_requirements", ""),
                                             heading_structure=requirements.get("heading_structure", "Standard"),
                                             content_tone=requirements.get("content_tone", "Professional"),
                                             topic=topic,
                                             count=target_count)
        
        questions_content = self._generate_with_prompt(questions_prompt)
        
        # Create questions MDX file
        questions_filename = f"questions_{self._generate_slug(topic)}.mdx"
        questions_filepath = os.path.join(config.output_dir, questions_filename)
        
        mdx_content = f"""# {topic} Interview Questions

## 📋 Generated Questions List

{questions_content}

## 📝 Instructions for Review
1. **Review each question** for accuracy and relevance
2. **Add or remove questions** as needed
3. **Adjust difficulty levels** if required
4. **Modify frequency, priority, and company types** as needed
5. **Save this file** and run Step 3 to generate answers

## 🚀 Next Step
Run: python main.py interview generate-answers-from-mdx --mdx-file {questions_filepath}
"""
        
        with open(questions_filepath, 'w', encoding='utf-8') as f:
            f.write(mdx_content)
        
        console.print(f"[blue]📁 Questions saved to: {questions_filepath}[/blue]")
        console.print(f"[green]✅ Step 2 Complete! Review and edit questions in MDX file[/green]")
        
        return {
            "status": "success",
            "questions_content": questions_content,
            "mdx_filepath": questions_filepath,
            "topic": topic,
            "requirements": requirements
        }
    
    def generate_answers_from_mdx(self, mdx_filepath: str) -> Dict[str, Any]:
        """Step 3: Generate answers for questions from MDX file."""
        console.print(f"[green]🎯 Step 3: Generating answers from MDX questions...[/green]")
        
        # Load MDX content
        with open(mdx_filepath, 'r', encoding='utf-8') as f:
            mdx_content = f.read()
        
        # Parse questions from MDX
        questions = self._parse_questions_from_mdx(mdx_content)
        topic = self._extract_topic_from_mdx(mdx_content)
        
        # Analyze MDX requirements for answer generation
        analysis_prompt = self._format_prompt("analyze_mdx_requirements", mdx_content=mdx_content)
        analysis_result = self._generate_with_prompt(analysis_prompt)
        requirements = self._parse_analysis_result(analysis_result)
        
        # Generate answers for each question
        answered_questions = []
        for i, question_data in enumerate(questions):
            console.print(f"[yellow]Generating answer {i+1}/{len(questions)}: {question_data['question'][:50]}...[/yellow]")
            
            answer_prompt = self._format_prompt("generate_adaptive_answers",
                                              question=question_data['question'],
                                              sheet_type=requirements.get("sheet_type", "General Tech"),
                                              target_audience=requirements.get("target_audience", "Developers"),
                                              content_style=requirements.get("content_style", "Technical"),
                                              heading_structure=requirements.get("heading_structure", "Standard"),
                                              content_tone=requirements.get("content_tone", "Professional"),
                                              topic=topic)
            
            answer = self._generate_with_prompt(answer_prompt)
            
            # Apply MDX styling
            styled_answer = self.mdx_styler.format_mdx_content(answer, "interview_answer")
            
            # Create complete question object
            question_obj = {
                "question": question_data['question'],
                "answer": styled_answer,
                "difficulty": question_data.get('difficulty', 'Intermediate'),
                "frequency": question_data.get('frequency', 'Asked Frequently'),
                "priority": question_data.get('priority', 'Medium'),
                "companyTypes": question_data.get('companyTypes', ['Startup', 'MidSize', 'MNC']),
                "category": question_data.get('category', 'General'),
                "specialNotes": question_data.get('specialNotes', '')
            }
            
            answered_questions.append(question_obj)
        
        # Create complete sheet with answers
        sheet_data = {
            "features": [],
            "name": f"{topic} Interview Questions",
            "slug": self._generate_slug(topic),
            "coverImageURL": self._generate_cover_image_url(topic),
            "description": f"Ace your {topic} Interview with Real Questions asked in Real Interviews.",
            "liveOn": datetime.now(timezone.utc).isoformat(),
            "roadmap": self._determine_roadmap_from_type(requirements.get("sheet_type", "General Tech")),
            "questions": answered_questions,
            "meta": self._generate_adaptive_meta_content(topic, requirements)
        }
        
        # Save complete sheet
        filename = f"complete_sheet_{self._generate_slug(topic)}.json"
        filepath = os.path.join(config.output_dir, filename)
        save_json_file(sheet_data, filepath)
        
        console.print(f"[blue]📁 Complete sheet with answers saved to: {filepath}[/blue]")
        console.print(f"[green]✅ Step 3 Complete! Ready for database publication[/green]")
        
        return {
            "status": "success",
            "sheet_data": sheet_data,
            "filepath": filepath,
            "questions_count": len(answered_questions),
            "topic": topic
        }
    

    
    def _parse_analysis_result(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the analysis result into structured requirements."""
        requirements = {
            "sheet_type": "General Tech",
            "target_audience": "Developers",
            "content_style": "Technical",
            "question_categories": "Fundamentals, Advanced",
            "special_requirements": "",
            "heading_structure": "Standard",
            "content_tone": "Professional"
        }
        
        # Extract information from analysis text using multiple strategies
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Handle structured format with **key:** value
            if '**' in line and ':**' in line:
                try:
                    key_part = line.split(':**')[0]
                    value_part = line.split(':**')[1]
                    key = key_part.replace('**', '').strip().lower().replace(' ', '_')
                    value = value_part.strip()
                    
                    if key in requirements:
                        requirements[key] = value
                except:
                    continue
            
            # Handle simple key: value format
            elif ':' in line and not line.startswith('#'):
                try:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if key in requirements:
                        requirements[key] = value
                except:
                    continue
        
        # Special handling for DSA requirements
        if "dsa" in analysis_text.lower() or "data structure" in analysis_text.lower():
            requirements["sheet_type"] = "DSA"
            requirements["content_style"] = "Explain like teaching a 10-year-old"
            requirements["heading_structure"] = "DSA-specific"
            requirements["content_tone"] = "Educational"
            
            # Extract specific DSA requirements
            if "analogies" in analysis_text.lower():
                requirements["special_requirements"] += "Use real-world analogies, "
            if "memory tricks" in analysis_text.lower():
                requirements["special_requirements"] += "Include memory tricks and mnemonics, "
            if "step-by-step" in analysis_text.lower():
                requirements["special_requirements"] += "Provide step-by-step solutions, "
            if "practice problems" in analysis_text.lower():
                requirements["special_requirements"] += "Include practice problems, "
        
        return requirements
    

    
    def _display_analysis_results(self, topic: str, requirements: Dict[str, Any]):
        """Display analysis results in a formatted table."""
        table = Table(title=f"📊 Analysis Results for {topic}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Sheet Type", requirements.get("sheet_type", "General Tech"))
        table.add_row("Target Audience", requirements.get("target_audience", "Developers"))
        table.add_row("Content Style", requirements.get("content_style", "Technical"))
        table.add_row("Question Categories", requirements.get("question_categories", "Fundamentals, Advanced"))
        table.add_row("Heading Structure", requirements.get("heading_structure", "Standard"))
        table.add_row("Content Tone", requirements.get("content_tone", "Professional"))
        
        console.print(table)
        
        # Display special requirements if any
        special_reqs = requirements.get("special_requirements", "")
        if special_reqs:
            console.print(Panel(special_reqs, title="🎯 Special Requirements", border_style="yellow"))
    
    def _extract_topic_from_mdx(self, mdx_content: str) -> str:
        """Extract topic from MDX content."""
        lines = mdx_content.split('\n')
        for line in lines:
            if line.startswith('# ') and 'Interview Questions' in line:
                return line.replace('# ', '').replace(' Interview Questions', '').strip()
        return "Unknown Topic"
    
    def _parse_questions_from_mdx(self, mdx_content: str) -> List[Dict[str, Any]]:
        """Parse questions from MDX content with enhanced parsing."""
        questions = []
        lines = mdx_content.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            
            # Handle various question formats
            if line.startswith('- Question:') or (line and line[0].isdigit() and '. Question:' in line):
                if current_question:
                    questions.append(current_question)
                
                if line.startswith('- Question:'):
                    question_text = line.replace('- Question:', '').strip()
                else:
                    question_text = line.split('. Question:', 1)[1].strip()
                current_question = {'question': question_text}
            
            elif 'Category:' in line:
                if line.startswith('- Category:'):
                    current_question['category'] = line.replace('- Category:', '').strip()
                else:
                    current_question['category'] = line.split('Category:', 1)[1].strip()
            
            elif 'Difficulty:' in line:
                if line.startswith('- Difficulty:'):
                    current_question['difficulty'] = line.replace('- Difficulty:', '').strip()
                else:
                    current_question['difficulty'] = line.split('Difficulty:', 1)[1].strip()
            
            elif 'Frequency:' in line:
                if line.startswith('- Frequency:'):
                    current_question['frequency'] = line.replace('- Frequency:', '').strip()
                else:
                    current_question['frequency'] = line.split('Frequency:', 1)[1].strip()
            
            elif 'Priority:' in line:
                if line.startswith('- Priority:'):
                    current_question['priority'] = line.replace('- Priority:', '').strip()
                else:
                    current_question['priority'] = line.split('Priority:', 1)[1].strip()
            
            elif 'CompanyTypes:' in line:
                if line.startswith('- CompanyTypes:'):
                    company_types = line.replace('- CompanyTypes:', '').strip()
                else:
                    company_types = line.split('CompanyTypes:', 1)[1].strip()
                current_question['companyTypes'] = [ct.strip() for ct in company_types.split(',')]
            
            elif 'SpecialNotes:' in line:
                if line.startswith('- SpecialNotes:'):
                    current_question['specialNotes'] = line.replace('- SpecialNotes:', '').strip()
                else:
                    current_question['specialNotes'] = line.split('SpecialNotes:', 1)[1].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _determine_roadmap_from_type(self, sheet_type: str) -> str:
        """Determine roadmap based on sheet type."""
        roadmap_mapping = {
            "DSA": "Tech",
            "Python": "Backend",
            "Java": "Backend", 
            "Golang": "Backend",
            "JavaScript": "Frontend",
            "React": "Frontend",
            "Aptitude": "Tech",
            "System Design": "Tech",
            "General Tech": "Tech"
        }
        return roadmap_mapping.get(sheet_type, "Tech")
    
    def _generate_adaptive_meta_content(self, topic: str, requirements: Dict[str, Any]) -> str:
        """Generate adaptive meta content based on requirements."""
        sheet_type = requirements.get("sheet_type", "General Tech")
        target_audience = requirements.get("target_audience", "Developers")
        content_style = requirements.get("content_style", "Technical")
        
        meta_content = f"""
This comprehensive {sheet_type} interview preparation guide is designed specifically for {target_audience}. 
Our {content_style} approach ensures you understand both the theoretical concepts and practical applications.

Key features:
• Real interview questions from top companies
• {content_style} explanations tailored for {target_audience}
• Comprehensive coverage of {requirements.get("question_categories", "fundamentals and advanced topics")}
• Practical examples and code snippets
• Interview tips and best practices

Perfect for {target_audience} preparing for {sheet_type} interviews at startups, mid-size companies, MNCs, and FAANG companies.
"""
        return meta_content.strip()
    

    
    def _generate_slug(self, name: str) -> str:
        """Generate a slug from name."""
        return name.lower().replace(' ', '-').replace('_', '-').replace('.', '')
    
    def _generate_cover_image_url(self, topic: str) -> str:
        """Generate cover image URL."""
        slug = self._generate_slug(topic)
        return f"https://ik.imagekit.io/tbe/webapp/{slug}-interview-questions.svg" 