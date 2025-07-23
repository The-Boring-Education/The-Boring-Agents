"""Question Creator Agent - Generates high-quality interview questions with strict count adherence."""

from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate
import random

from ...core.base_agent import BaseAgent


class QuestionCreator(BaseAgent):
    """Agent for creating high-quality interview questions with strict count adherence."""
    
    def __init__(self, **kwargs):
        """Initialize with higher temperature for creativity and strict count adherence."""
        super().__init__(temperature=0.9, **kwargs)  # Higher temperature for creativity
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for question generation."""
        
        generate_questions_template = PromptTemplate(
            input_variables=["topic", "requirements", "target_count", "question_categories"],
            template="""
You are India's TOP tech interviewer with 20+ years of experience who has conducted 500+ interviews at:
- FAANG companies (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**Topic:** {topic}
**Target Count:** EXACTLY {target_count} questions (no more, no less)
**Requirements:** {requirements}
**Question Categories:** {question_categories}

Create EXACTLY {target_count} high-quality interview questions that will help Indian students ACE their interviews.

## CRITICAL REQUIREMENTS:
- Generate EXACTLY {target_count} questions - NO MORE, NO LESS
- Each question must be unique and high-quality
- Follow the exact format specified below
- Ensure proper distribution across difficulty levels

## Question Distribution Guidelines:
- **Easy Questions (30%):** Basic concepts, fundamentals, syntax
- **Medium Questions (50%):** Practical implementation, real-world scenarios
- **Hard Questions (20%):** Advanced concepts, optimization, edge cases

## Question Categories to Cover:
{question_categories}

## Question Format:
For each question, provide:
1. **Question Title:** Clear, concise title
2. **Question Text:** The actual question
3. **Difficulty Level:** Easy/Medium/Hard
4. **Frequency:** Most Asked/Asked Frequently/Asked Sometimes
5. **Priority:** High/Medium/Low
6. **Company Types:** Startup, MNC, FAANG, MidSize

## Quality Requirements:
- Questions should be practical and relevant to Indian tech industry
- Include real-world scenarios and problem-solving
- Cover both theoretical and practical aspects
- Questions should test both knowledge and problem-solving skills
- Include follow-up questions and variations
- Focus on what companies actually ask in interviews

## STRICT OUTPUT FORMAT:
Generate EXACTLY {target_count} questions in this format:

### Question 1
- Question: [Your question here]
  - Difficulty: [Easy/Medium/Hard]
  - Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
  - Priority: [High/Medium/Low]
  - Company Types: [Startup, MNC, FAANG, MidSize]

### Question 2
- Question: [Your question here]
  - Difficulty: [Easy/Medium/Hard]
  - Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
  - Priority: [High/Medium/Low]
  - Company Types: [Startup, MNC, FAANG, MidSize]

[Continue for exactly {target_count} questions]

## FINAL CHECK:
Before submitting, count your questions. You must have EXACTLY {target_count} questions.
If you have fewer than {target_count}, generate more.
If you have more than {target_count}, remove the extra ones.

Remember: Generate EXACTLY {target_count} questions - no more, no less. Each question should be unique and high-quality.
"""
        )
        
        return {
            "generate_questions": generate_questions_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "generate_questions":
            return self.generate_questions(
                topic=kwargs.get("topic"),
                requirements=kwargs.get("requirements"),
                target_count=kwargs.get("target_count", 50)
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def generate_questions(self, topic: str, requirements: Dict[str, Any], target_count: int = 50) -> List[Dict[str, Any]]:
        """Generate exactly the specified number of questions with strict count adherence."""
        self.logger.info(f"Generating exactly {target_count} questions for {topic}")
        
        # Prepare question categories based on requirements
        question_categories = self._get_question_categories(topic, requirements)
        
        # Generate questions with strict count
        prompt = self._format_prompt("generate_questions",
                                   topic=topic,
                                   requirements=str(requirements),
                                   target_count=target_count,
                                   question_categories=question_categories)
        
        response = self._generate_with_prompt(prompt)
        
        # Parse questions from response
        questions = self._parse_questions_from_response(response, target_count)
        
        # Ensure exact count with retry logic
        max_retries = 3
        retry_count = 0
        
        while len(questions) != target_count and retry_count < max_retries:
            self.logger.warning(f"Generated {len(questions)} questions, expected {target_count}. Retry {retry_count + 1}/{max_retries}")
            
            if len(questions) < target_count:
                # Generate additional questions
                additional_needed = target_count - len(questions)
                additional_questions = self._generate_additional_questions(topic, additional_needed)
                questions.extend(additional_questions)
            else:
                # Trim to exact count
                questions = questions[:target_count]
            
            retry_count += 1
        
        # Final validation and cleaning
        questions = self._validate_questions(questions)
        
        # Final count check
        if len(questions) != target_count:
            self.logger.error(f"Failed to generate exactly {target_count} questions after {max_retries} retries. Got {len(questions)} questions.")
            # Force exact count by trimming or padding
            if len(questions) > target_count:
                questions = questions[:target_count]
            else:
                # Generate filler questions if needed
                while len(questions) < target_count:
                    filler_question = {
                        "question": f"Additional {topic} question {len(questions) + 1}",
                        "difficulty": "Medium",
                        "frequency": "Asked Sometimes",
                        "priority": "Low",
                        "company_types": ["Startup"]
                    }
                    questions.append(filler_question)
        
        self.logger.info(f"Successfully generated exactly {len(questions)} questions")
        return questions
    
    def _get_question_categories(self, topic: str, requirements: Dict[str, Any]) -> str:
        """Get question categories based on topic and requirements."""
        base_categories = [
            "Core Fundamentals",
            "Practical Implementation", 
            "Advanced Concepts",
            "Best Practices",
            "System Design",
            "Performance & Optimization",
            "Real-world Scenarios",
            "Problem Solving",
            "Code Review & Debugging",
            "Industry Trends"
        ]
        
        # Add topic-specific categories
        if "DSA" in topic or "Data Structures" in topic:
            base_categories.extend([
                "Time & Space Complexity",
                "Algorithm Design",
                "Data Structure Implementation",
                "Optimization Techniques"
            ])
        elif "Python" in topic:
            base_categories.extend([
                "Python Internals",
                "Advanced Python Features",
                "Frameworks & Libraries",
                "Testing & Debugging"
            ])
        elif "JavaScript" in topic or "React" in topic:
            base_categories.extend([
                "JavaScript Fundamentals",
                "Modern JavaScript Features",
                "Frontend Frameworks",
                "State Management"
            ])
        
        return ", ".join(base_categories)
    
    def _parse_questions_from_response(self, response: str, target_count: int) -> List[Dict[str, Any]]:
        """Parse questions from AI response."""
        questions = []
        lines = response.split('\n')
        
        current_question = None
        question_number = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('### Question') or line.startswith('## Question'):
                if current_question:
                    questions.append(current_question)
                
                question_number += 1
                current_question = {
                    "question": "",
                    "difficulty": "Medium",
                    "frequency": "Asked Frequently",
                    "priority": "Medium",
                    "company_types": ["Startup", "MNC"]
                }
            
            elif line.startswith('- Question:') and current_question:
                question_text = line.replace('- Question:', '').strip()
                current_question["question"] = question_text
            
            elif line.startswith('  - Difficulty:') and current_question:
                difficulty = line.replace('  - Difficulty:', '').strip()
                current_question["difficulty"] = difficulty
            
            elif line.startswith('  - Frequency:') and current_question:
                frequency = line.replace('  - Frequency:', '').strip()
                current_question["frequency"] = frequency
            
            elif line.startswith('  - Priority:') and current_question:
                priority = line.replace('  - Priority:', '').strip()
                current_question["priority"] = priority
            
            elif line.startswith('  - Company Types:') and current_question:
                company_types = line.replace('  - Company Types:', '').strip()
                current_question["company_types"] = [ct.strip() for ct in company_types.split(',')]
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def _generate_additional_questions(self, topic: str, count: int) -> List[Dict[str, Any]]:
        """Generate additional questions to meet target count."""
        additional_prompt = f"""
Generate exactly {count} additional high-quality interview questions for {topic}.

Focus on:
- Different aspects not covered in previous questions
- Varying difficulty levels
- Real-world scenarios
- Industry-relevant topics

Format each question as:
- Question: [question text]
  - Difficulty: [Easy/Medium/Hard]
  - Frequency: [Most Asked/Asked Frequently/Asked Sometimes]
  - Priority: [High/Medium/Low]
  - Company Types: [Startup, MNC, FAANG, MidSize]
"""
        
        response = self._generate_with_prompt(additional_prompt)
        return self._parse_questions_from_response(response, count)
    
    def _validate_questions(self, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and clean questions."""
        validated_questions = []
        
        for q in questions:
            # Ensure required fields
            if not q.get("question"):
                continue
            
            # Set defaults for missing fields
            q.setdefault("difficulty", "Medium")
            q.setdefault("frequency", "Asked Frequently")
            q.setdefault("priority", "Medium")
            q.setdefault("company_types", ["Startup", "MNC"])
            
            # Clean question text
            q["question"] = q["question"].strip()
            
            # Ensure question is not empty
            if q["question"]:
                validated_questions.append(q)
        
        return validated_questions 