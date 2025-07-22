"""Interview preparation agent for generating question sheets."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate
import random

from ...core.base_agent import BaseAgent


class InterviewAgent(BaseAgent):
    """Agent for generating interview preparation content in sheet format."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for interview content generation."""
        
        question_sheet_template = PromptTemplate(
            input_variables=["topic"],
            template="""
            You are a senior tech interviewer with 20+ years of experience who has conducted 300+ interviews. 
            You have deep knowledge of the Indian tech industry and understand what companies actually ask in interviews.
            
            Create a comprehensive interview question sheet for {topic}. Generate 30-50 high-quality questions that cover:
            
            1. **Core Fundamentals** - Basic concepts, syntax, and principles
            2. **Practical Implementation** - Real-world scenarios and problem-solving
            3. **Advanced Concepts** - Complex topics and edge cases
            4. **Best Practices** - Industry standards and optimization
            5. **System Design** - Architecture and scalability considerations
            
            For each question, provide:
            - A clear, concise question title
            - The actual question text
            - A comprehensive answer with:
              * Quick answer summary
              * Detailed explanation with code examples
              * Good vs bad code examples
              * Why this concept matters
              * Different ways interviewers ask this
              * Related concepts to revise
              * Memory tricks and tips
              * Interview pro tips
              * Practice problems
              * Companies that ask this
            
            Format each answer in markdown with proper sections and emojis for readability.
            
            Think like an experienced interviewer who knows exactly what companies ask and how to evaluate candidates effectively.
            Focus on questions that actually come up in Indian tech interviews, not just theoretical concepts.
            """
        )
        
        return {
            "question_sheet": question_sheet_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate interview content based on the specified type.
        
        Args:
            content_type: Type of content to generate
            **kwargs: Parameters specific to the content type
            
        Returns:
            Generated interview content with metadata
        """
        if content_type not in self.prompt_templates:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Generate the prompt
        prompt = self._format_prompt(content_type, **kwargs)
        
        # Generate content
        generated_text = self._generate_with_prompt(prompt)
        
        # Structure the response
        result = {
            "content_type": content_type,
            "parameters": kwargs,
            "generated_content": generated_text,
            "metadata": {
                "model": self.model_name,
                "timestamp": self._get_timestamp(),
                "question_count": self._estimate_question_count(generated_text),
                "estimated_prep_time": self._estimate_prep_time(generated_text)
            }
        }
        
        return result
    
    def create_question_sheet(self, topic: str) -> Dict[str, Any]:
        """Create a comprehensive question sheet for a technology topic.
        
        Args:
            topic: The technology/topic to focus on (e.g., "JavaScript", "React", "Python")
            
        Returns:
            Complete question sheet with structured questions and answers
        """
        result = self.generate_content("question_sheet", topic=topic)
        
        # Parse the generated content into structured format
        structured_questions = self._parse_questions_from_content(result['generated_content'])
        
        # Determine roadmap based on topic
        roadmap = self._determine_roadmap(topic)
        
        return {
            "topic": topic,
            "roadmap": roadmap,
            "questions": structured_questions,
            "metadata": {
                "total_questions": len(structured_questions),
                "created_at": self._get_timestamp(),
                "roadmap": roadmap
            }
        }
    
    def _parse_questions_from_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse the generated content into structured question format."""
        questions = []
        
        # Split content by question markers (## headers)
        sections = content.split('##')
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            if len(lines) < 2:
                continue
            
            # Extract title (first line after ##)
            title_line = lines[0].strip()
            if not title_line or title_line.startswith('#'):
                continue
            
            # Find the question text and answer
            question_text = ""
            answer_text = ""
            in_answer = False
            
            for line in lines[1:]:
                line = line.strip()
                
                # Check for answer section markers
                if any(marker in line for marker in ['🎯', '📖', '💻', '❌', '✅', '🤔', '🎭', '🔗', '😄', '💡', '💼', '🧠', '🏢']):
                    in_answer = True
                    answer_text += line + '\n'
                    continue
                
                if in_answer:
                    answer_text += line + '\n'
                else:
                    # If we haven't found answer markers yet, this is question text
                    if line and not line.startswith('---'):
                        question_text += line + '\n'
            
            # If we have both question and answer, create the question
            if question_text.strip() and answer_text.strip():
                # Determine frequency, company types, and priority
                frequency = self._determine_frequency(title_line, question_text)
                company_types = self._determine_company_types(title_line, question_text)
                priority = self._determine_priority(title_line, question_text)
                
                questions.append({
                    "title": title_line,
                    "question": question_text.strip(),
                    "answer": answer_text.strip(),
                    "frequency": frequency,
                    "companyTypes": company_types,
                    "priority": priority
                })
        
        # If no questions were parsed, create a fallback structure
        if not questions:
            # Create a simple question structure from the content
            questions.append({
                "title": "Sample Question",
                "question": "What are the key concepts in this technology?",
                "answer": content[:500] + "..." if len(content) > 500 else content,
                "frequency": "Asked Frequently",
                "companyTypes": ["MidSize", "MNC"],
                "priority": "Medium"
            })
        
        return questions
    
    def _determine_frequency(self, title: str, question: str) -> str:
        """Determine how frequently this question is asked."""
        # Keywords that indicate high frequency
        high_freq_keywords = [
            'difference between', 'what is', 'explain', 'how does', 'basic',
            'fundamental', 'core', 'syntax', 'variable', 'function', 'loop',
            'array', 'object', 'class', 'method', 'property', 'event'
        ]
        
        # Keywords that indicate medium frequency
        medium_freq_keywords = [
            'advanced', 'optimization', 'performance', 'memory', 'async',
            'promise', 'callback', 'closure', 'hoisting', 'prototype',
            'inheritance', 'polymorphism', 'design pattern', 'algorithm'
        ]
        
        # Keywords that indicate low frequency
        low_freq_keywords = [
            'edge case', 'rare', 'complex', 'expert', 'senior level',
            'system design', 'architecture', 'scalability', 'microservices',
            'distributed', 'concurrent', 'threading', 'advanced algorithm'
        ]
        
        text = (title + ' ' + question).lower()
        
        if any(keyword in text for keyword in high_freq_keywords):
            return 'Most Asked'
        elif any(keyword in text for keyword in medium_freq_keywords):
            return 'Asked Frequently'
        elif any(keyword in text for keyword in low_freq_keywords):
            return 'Asked Sometimes'
        else:
            return 'Asked Frequently'  # Default
    
    def _determine_company_types(self, title: str, question: str) -> List[str]:
        """Determine which company types ask this question."""
        text = (title + ' ' + question).lower()
        
        company_types = []
        
        # Startup questions (practical, hands-on, fast-paced)
        startup_keywords = [
            'practical', 'implementation', 'real-world', 'quick', 'fast',
            'startup', 'mvp', 'prototype', 'hands-on', 'coding', 'debug'
        ]
        
        # Midsize questions (balanced, established practices)
        midsize_keywords = [
            'best practice', 'standard', 'convention', 'maintainable',
            'readable', 'documentation', 'testing', 'quality', 'process'
        ]
        
        # MNC questions (formal, enterprise, large-scale)
        mnc_keywords = [
            'enterprise', 'large scale', 'distributed', 'security',
            'compliance', 'standardization', 'governance', 'architecture'
        ]
        
        # FAANG questions (advanced, algorithmic, system design)
        faang_keywords = [
            'algorithm', 'complexity', 'optimization', 'system design',
            'scalability', 'performance', 'advanced', 'senior level',
            'data structure', 'leetcode', 'competitive programming'
        ]
        
        if any(keyword in text for keyword in startup_keywords):
            company_types.append('Startup')
        
        if any(keyword in text for keyword in midsize_keywords):
            company_types.append('MidSize')
        
        if any(keyword in text for keyword in mnc_keywords):
            company_types.append('MNC')
        
        if any(keyword in text for keyword in faang_keywords):
            company_types.append('FAANG')
        
        # If no specific type detected, assign based on question complexity
        if not company_types:
            if 'basic' in text or 'fundamental' in text:
                company_types = ['Startup', 'MidSize']
            elif 'advanced' in text or 'complex' in text:
                company_types = ['MNC', 'FAANG']
            else:
                company_types = ['MidSize', 'MNC']
        
        return company_types
    
    def _determine_priority(self, title: str, question: str) -> str:
        """Determine the priority level of this question."""
        text = (title + ' ' + question).lower()
        
        # High priority keywords
        high_priority_keywords = [
            'fundamental', 'core', 'basic', 'essential', 'must know',
            'critical', 'important', 'key concept', 'foundation'
        ]
        
        # Medium priority keywords
        medium_priority_keywords = [
            'common', 'frequently', 'often', 'typical', 'standard',
            'regular', 'usual', 'normal', 'average'
        ]
        
        # Low priority keywords
        low_priority_keywords = [
            'advanced', 'complex', 'rare', 'edge case', 'expert',
            'senior', 'specialized', 'niche', 'optional'
        ]
        
        if any(keyword in text for keyword in high_priority_keywords):
            return 'High'
        elif any(keyword in text for keyword in low_priority_keywords):
            return 'Low'
        else:
            return 'Medium'  # Default
    
    def _determine_roadmap(self, topic: str) -> str:
        """Determine the roadmap category based on the topic."""
        topic_lower = topic.lower()
        
        # Frontend technologies
        frontend_techs = [
            'javascript', 'react', 'vue', 'angular', 'html', 'css',
            'typescript', 'svelte', 'nextjs', 'nuxt', 'frontend',
            'ui', 'ux', 'web', 'browser', 'dom'
        ]
        
        # Backend technologies
        backend_techs = [
            'python', 'java', 'nodejs', 'node.js', 'express', 'django', 'flask',
            'spring', 'php', 'ruby', 'go', 'rust', 'backend', 'api',
            'server', 'database', 'sql', 'nosql', 'mongodb', 'mysql'
        ]
        
        # Fullstack technologies
        fullstack_techs = [
            'mern', 'mean', 'fullstack', 'full stack', 'full-stack',
            'web development', 'full stack development'
        ]
        
        # General tech topics
        general_techs = [
            'dsa', 'data structures', 'algorithms', 'system design',
            'computer science', 'programming', 'coding', 'software',
            'development', 'engineering'
        ]
        
        if any(tech in topic_lower for tech in frontend_techs):
            return 'Frontend'
        elif any(tech in topic_lower for tech in backend_techs):
            return 'Backend'
        elif any(tech in topic_lower for tech in fullstack_techs):
            return 'Fullstack'
        else:
            return 'Tech'  # Default for general topics
    
    def _estimate_question_count(self, content: str) -> int:
        """Estimate number of questions in generated content."""
        # Count markdown headers that likely indicate questions
        question_headers = content.count('## ')
        return max(question_headers, 30)  # Minimum 30 questions
    
    def _estimate_prep_time(self, content: str) -> str:
        """Estimate preparation time for the content."""
        word_count = len(content.split())
        if word_count < 5000:
            return "2-3 hours"
        elif word_count < 10000:
            return "4-6 hours"
        else:
            return "6-8 hours"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()