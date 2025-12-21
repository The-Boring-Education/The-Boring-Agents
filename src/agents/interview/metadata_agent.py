"""Metadata Agent - Adds metadata to questions from MDX files."""

import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from langchain_core.prompts import PromptTemplate
from rich.console import Console

from ...core.base_agent import BaseAgent
from ...core.config import config
from ...utils.helpers import generate_filename, save_json_file, load_json_file
from ...utils.validation import InterviewQuestionValidator

console = Console()


class MetadataAgent(BaseAgent):
    """Agent for adding metadata to questions from MDX files."""
    
    def __init__(self, **kwargs):
        """Initialize the metadata agent with enhanced logging."""
        super().__init__(**kwargs)
        
        # Log agent initialization with model and temperature info
        self.logger.info(f"🤖 MetadataAgent initialized with:")
        self.logger.info(f"   Model: {self.model_name}")
        self.logger.info(f"   Temperature: {config.temperature}")
        self.logger.info(f"   Max Tokens: {config.max_tokens}")
        
        console.print(f"[blue]🤖 MetadataAgent initialized - Model: {self.model_name}, Temperature: {config.temperature}[/blue]")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for metadata generation."""
        return {
            "analyze_question": PromptTemplate(
                input_variables=["question", "topic", "context"],
                template="""
You are an expert interview question analyst with 20+ years of experience in tech hiring. Analyze the following interview question and provide appropriate metadata.

Question: {question}
Topic: {topic}
Context: {context}

Based on your extensive experience, determine:

1. **Frequency**: How often this question is asked in interviews
   - "Most Asked" (asked in 80%+ of interviews)
   - "Asked Frequently" (asked in 50-80% of interviews) 
   - "Asked Sometimes" (asked in 20-50% of interviews)

2. **Priority**: How important this question is for interview success
   - "High" (critical for passing the interview)
   - "Medium" (important but not critical)
   - "Low" (nice to know but not essential)

3. **Company Types**: Which types of companies typically ask this question (can select multiple)
   - "Startup" (early-stage companies, fast-paced)
   - "MidSize" (growing companies, established processes)
   - "MNC" (multinational corporations, formal processes)
   - "FAANG" (top tech companies, high standards)

4. **Difficulty**: How challenging this question is
   - "Easy" (basic concepts, entry-level)
   - "Medium" (intermediate concepts, mid-level)
   - "Hard" (advanced concepts, senior-level)

Provide your analysis in this exact format:
Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
Priority: [High/Medium/Low]
Company Types: [Startup, MidSize, MNC, FAANG] (select relevant ones)
Difficulty: [Easy/Medium/Hard]
"""
            ),
            "batch_analyze": PromptTemplate(
                input_variables=["questions", "topic", "context"],
                template="""
You are an expert interview question analyst. Analyze these questions and provide metadata for each.

Topic: {topic}
Context: {context}

Questions:
{questions}

For each question, provide metadata in this exact format:

Question: [question text]
- Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
- Priority: [High/Medium/Low] 
- Company Types: [Startup, MidSize, MNC, FAANG]
- Difficulty: [Easy/Medium/Hard]

Analyze based on:
- Real interview patterns from top companies
- Question complexity and depth
- Industry relevance and demand
- Career progression importance
"""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "add_metadata_to_mdx":
            return self.add_metadata_to_mdx(
                kwargs.get("mdx_filepath"),
                kwargs.get("topic", "General Tech")
            )
        elif content_type == "batch_add_metadata":
            return self.batch_add_metadata(
                kwargs.get("questions"),
                kwargs.get("topic", "General Tech"),
                kwargs.get("context", "")
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def add_metadata_to_mdx(self, mdx_filepath: str, topic: str = "General Tech") -> Dict[str, Any]:
        """Add metadata to questions in MDX file."""
        console.print(f"[green]🎯 Adding metadata to questions in: {mdx_filepath}[/green]")
        
        try:
            # Load MDX content
            with open(mdx_filepath, 'r', encoding='utf-8') as f:
                mdx_content = f.read()
            
            # Extract questions from MDX
            questions = self._extract_questions_from_mdx(mdx_content)
            
            if not questions:
                return {
                    "status": "error",
                    "message": "No questions found in MDX file"
                }
            
            console.print(f"[blue]📊 Found {len(questions)} questions to process[/blue]")
            
            # Add metadata to each question
            enhanced_questions = []
            for i, question in enumerate(questions):
                console.print(f"[yellow]Processing question {i+1}/{len(questions)}: {question[:50]}...[/yellow]")
                
                metadata = self._analyze_single_question(question, topic, mdx_content)
                enhanced_questions.append({
                    "question": question,
                    **metadata
                })
            
            # Create enhanced MDX content
            enhanced_mdx = self._create_enhanced_mdx(mdx_content, enhanced_questions)
            
            # Save enhanced MDX
            enhanced_filepath = mdx_filepath.replace('.mdx', '_with_metadata.mdx')
            with open(enhanced_filepath, 'w', encoding='utf-8') as f:
                f.write(enhanced_mdx)
            
            console.print(f"[green]✅ Metadata added successfully![/green]")
            console.print(f"[blue]📁 Enhanced MDX: {enhanced_filepath}[/blue]")
            
            return {
                "status": "success",
                "enhanced_filepath": enhanced_filepath,
                "questions_count": len(enhanced_questions),
                "enhanced_questions": enhanced_questions
            }
            
        except Exception as e:
            self.logger.error(f"Error adding metadata: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def batch_add_metadata(self, questions: List[str], topic: str = "General Tech", context: str = "") -> Dict[str, Any]:
        """Add metadata to a batch of questions."""
        console.print(f"[green]🎯 Adding metadata to {len(questions)} questions[/green]")
        
        try:
            # Format questions for batch analysis
            questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])
            
            # Generate batch analysis
            batch_prompt = self._format_prompt("batch_analyze", 
                                             questions=questions_text,
                                             topic=topic,
                                             context=context)
            batch_result = self._generate_with_prompt(batch_prompt)
            
            # Parse batch results
            enhanced_questions = self._parse_batch_results(batch_result, questions)
            
            console.print(f"[green]✅ Batch metadata generation completed![/green]")
            
            return {
                "status": "success",
                "enhanced_questions": enhanced_questions,
                "questions_count": len(enhanced_questions)
            }
            
        except Exception as e:
            self.logger.error(f"Error in batch metadata generation: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _analyze_single_question(self, question: str, topic: str, context: str) -> Dict[str, Any]:
        """Analyze a single question and return metadata."""
        # Extract difficulty from question if it has stars
        difficulty_from_stars = self._extract_difficulty_from_stars(question)
        
        prompt = self._format_prompt("analyze_question", 
                                   question=question,
                                   topic=topic,
                                   context=context)
        result = self._generate_with_prompt(prompt)
        
        metadata = self._parse_metadata_result(result)
        
        # Override difficulty if we found stars in the question
        if difficulty_from_stars:
            metadata["difficulty"] = difficulty_from_stars
        
        return metadata
    
    def _parse_metadata_result(self, result: str) -> Dict[str, Any]:
        """Parse metadata from AI response."""
        metadata = {
            "frequency": "Asked Sometimes",
            "priority": "Medium", 
            "company_types": ["Startup", "MNC"],
            "difficulty": "Medium"
        }
        
        lines = result.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key == "frequency":
                    metadata["frequency"] = value
                elif key == "priority":
                    metadata["priority"] = value
                elif key == "company types":
                    # Parse comma-separated company types
                    company_types = [ct.strip() for ct in value.split(',')]
                    metadata["company_types"] = company_types
                elif key == "difficulty":
                    metadata["difficulty"] = value
        
        return metadata
    
    def _parse_batch_results(self, result: str, original_questions: List[str]) -> List[Dict[str, Any]]:
        """Parse batch analysis results."""
        enhanced_questions = []
        
        # Split result into question blocks
        question_blocks = result.split('Question:')[1:]  # Skip first empty part
        
        for i, block in enumerate(question_blocks):
            if i >= len(original_questions):
                break
                
            metadata = self._parse_metadata_result(block)
            enhanced_questions.append({
                "question": original_questions[i],
                **metadata
            })
        
        return enhanced_questions
    
    def _extract_questions_from_mdx(self, mdx_content: str) -> List[str]:
        """Extract questions from MDX content."""
        questions = []
        
        # Look for question patterns - more specific to avoid duplicates
        patterns = [
            # Most specific patterns first
            r'\d+\.\s*★+\s*([^★\n]+)',  # Questions with difficulty stars
            r'\d+\.\s*([^★\n]+)',  # Questions without stars
            # Fallback patterns
            r'- Question:\s*(.+)',
            r'\d+\.\s*(.+\?)',
            r'###\s*(.+\?)',
            r'\*\*Question:\*\*\s*(.+)',
        ]
        
        # Use a set to track processed line numbers to avoid duplicates
        processed_lines = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, mdx_content, re.MULTILINE)
            for match in matches:
                # Get the line number to avoid duplicates
                line_start = mdx_content.rfind('\n', 0, match.start()) + 1
                line_end = mdx_content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(mdx_content)
                
                line_number = mdx_content.count('\n', 0, line_start)
                
                # Skip if we've already processed this line
                if line_number in processed_lines:
                    continue
                
                question_text = match.group(1).strip()
                if question_text and len(question_text) > 5:  # Basic validation
                    questions.append(question_text)
                    processed_lines.add(line_number)
        
        # Remove duplicates and filter out non-questions
        unique_questions = []
        seen_questions = set()
        
        for q in questions:
            # Clean the question text
            q = q.strip()
            
            # Skip if we've already seen this question
            if q in seen_questions:
                continue
            seen_questions.add(q)
            
            # Skip if it's just a number or section header
            if (len(q) < 10 or 
                q.isdigit() or 
                q.startswith('Phase') or 
                q.startswith('📘') or 
                q.startswith('📗') or 
                q.startswith('📙') or 
                q.startswith('📕') or
                q.startswith('🎯') or
                q.startswith('⸻') or
                q.startswith('📘') or
                q.startswith('📗') or
                q.startswith('📙') or
                q.startswith('📕') or
                'Target Audience' in q or
                'College students' in q or
                'DSA beginners' in q or
                'Entry-level' in q or
                'Working professionals' in q or
                'Instructions for Answer Generation' in q or
                'Provide detailed explanations' in q):
                continue
            
            # Skip if it's just a section number
            if re.match(r'^\d+\.\s*$', q):
                continue
                
            unique_questions.append(q)
        
        return unique_questions
    
    def _create_enhanced_mdx(self, original_mdx: str, enhanced_questions: List[Dict[str, Any]]) -> str:
        """Create enhanced MDX with metadata."""
        # Find the questions section and replace with enhanced version
        enhanced_section = "\n\n## 📋 Questions with Metadata\n\n"
        
        for i, q in enumerate(enhanced_questions, 1):
            enhanced_section += f"""### Question {i}

- Question: {q['question']}
  - Difficulty: {q.get('difficulty', 'Medium')}
  - Frequency: {q.get('frequency', 'Asked Sometimes')}
  - Priority: {q.get('priority', 'Medium')}
  - Company Types: {', '.join(q.get('company_types', ['Startup', 'MNC']))}

"""
        
        # Replace or append the enhanced section
        if "## 📋 Questions with Metadata" in original_mdx:
            # Replace existing section
            pattern = r'## 📋 Questions with Metadata.*?(?=##|\Z)'
            enhanced_mdx = re.sub(pattern, enhanced_section, original_mdx, flags=re.DOTALL)
        else:
            # Append new section
            enhanced_mdx = original_mdx + enhanced_section
        
        return enhanced_mdx
    
    def _extract_difficulty_from_stars(self, question: str) -> Optional[str]:
        """Extract difficulty level from star indicators in the question."""
        star_count = question.count('★')
        if star_count == 1:
            return "Easy"
        elif star_count == 2:
            return "Medium"
        elif star_count == 3:
            return "Hard"
        return None 