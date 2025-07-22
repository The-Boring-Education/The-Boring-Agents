"""Data validation utilities for interview questions."""

from typing import Dict, Any, List, Optional
from enum import Enum


class FrequencyType(Enum):
    """Valid frequency types for interview questions."""
    MOST_ASKED = "Most Asked"
    ASKED_FREQUENTLY = "Asked Frequently"
    ASKED_SOMETIMES = "Asked Sometimes"


class CompanyType(Enum):
    """Valid company types for interview questions."""
    STARTUP = "Startup"
    MIDSIZE = "MidSize"
    MNC = "MNC"
    FAANG = "FAANG"


class PriorityType(Enum):
    """Valid priority types for interview questions."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class RoadmapType(Enum):
    """Valid roadmap types."""
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    FULLSTACK = "Fullstack"
    TECH = "Tech"


class InterviewQuestionValidator:
    """Validator for interview question data format."""
    
    @staticmethod
    def validate_question_data(question_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and fix interview question data format.
        
        Args:
            question_data: Raw question data
            
        Returns:
            Validated and fixed question data
        """
        errors = []
        warnings = []
        
        # Required fields validation
        required_fields = ["title", "question", "answer"]
        for field in required_fields:
            if field not in question_data or not question_data[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate frequency
        frequency = question_data.get("frequency", "")
        if not frequency or frequency not in [f.value for f in FrequencyType]:
            warnings.append(f"Invalid frequency: {frequency}. Setting to 'Asked Frequently'")
            question_data["frequency"] = "Asked Frequently"
        
        # Validate company types - CRITICAL: Never allow empty company types
        company_types = question_data.get("companyTypes", [])
        if not company_types:
            errors.append("CRITICAL: Empty companyTypes detected. This is not allowed.")
            # Auto-fix with intelligent defaults based on question content
            question_text = question_data.get("question", "").lower()
            title_text = question_data.get("title", "").lower()
            
            # Determine intelligent defaults based on question content
            if any(word in (question_text + title_text) for word in ['basic', 'fundamental', 'syntax', 'variable', 'function']):
                question_data["companyTypes"] = ["Startup", "MidSize"]
            elif any(word in (question_text + title_text) for word in ['advanced', 'complex', 'algorithm', 'system design']):
                question_data["companyTypes"] = ["MNC", "FAANG"]
            else:
                question_data["companyTypes"] = ["MidSize", "MNC"]
            
            warnings.append(f"Auto-fixed empty companyTypes to: {question_data['companyTypes']}")
        else:
            valid_company_types = [ct.value for ct in CompanyType]
            invalid_types = [ct for ct in company_types if ct not in valid_company_types]
            if invalid_types:
                warnings.append(f"Invalid company types: {invalid_types}. Removing invalid types.")
                question_data["companyTypes"] = [ct for ct in company_types if ct in valid_company_types]
        
        # Validate priority
        priority = question_data.get("priority", "")
        if not priority or priority not in [p.value for p in PriorityType]:
            warnings.append(f"Invalid priority: {priority}. Setting to 'Medium'")
            question_data["priority"] = "Medium"
        
        # Validate roadmap
        roadmap = question_data.get("roadmap", "")
        if not roadmap or roadmap not in [r.value for r in RoadmapType]:
            warnings.append(f"Invalid roadmap: {roadmap}. Setting to 'Tech'")
            question_data["roadmap"] = "Tech"
        
        # Ensure answer has proper structure
        answer = question_data.get("answer", "")
        if answer:
            question_data["answer"] = InterviewQuestionValidator._clean_answer_format(answer)
        
        return {
            "data": question_data,
            "errors": errors,
            "warnings": warnings,
            "is_valid": len(errors) == 0
        }
    
    @staticmethod
    def validate_sheet_data(sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete interview sheet data.
        
        Args:
            sheet_data: Complete sheet data
            
        Returns:
            Validation results
        """
        errors = []
        warnings = []
        
        # Validate sheet metadata
        required_sheet_fields = ["name", "description", "roadmap"]
        for field in required_sheet_fields:
            if field not in sheet_data or not sheet_data[field]:
                errors.append(f"Missing required sheet field: {field}")
        
        # Validate questions
        questions = sheet_data.get("questions", [])
        if not questions:
            errors.append("No questions found in sheet")
        else:
            validated_questions = []
            for i, question in enumerate(questions):
                validation_result = InterviewQuestionValidator.validate_question_data(question)
                if validation_result["is_valid"]:
                    validated_questions.append(validation_result["data"])
                else:
                    errors.extend([f"Question {i+1}: {error}" for error in validation_result["errors"]])
                    warnings.extend([f"Question {i+1}: {warning}" for warning in validation_result["warnings"]])
            
            sheet_data["questions"] = validated_questions
        
        return {
            "data": sheet_data,
            "errors": errors,
            "warnings": warnings,
            "is_valid": len(errors) == 0
        }
    
    @staticmethod
    def _clean_answer_format(answer: str) -> str:
        """
        Clean and format the answer to ensure proper structure.
        
        Args:
            answer: Raw answer text
            
        Returns:
            Cleaned answer text
        """
        # Remove any critical formatting requirements section
        if "CRITICAL FORMATTING REQUIREMENTS:" in answer:
            parts = answer.split("CRITICAL FORMATTING REQUIREMENTS:")
            answer = parts[0].strip()
        
        # Ensure proper section headers
        sections = [
            "🎯 Quick Answer",
            "📖 Introduction", 
            "💻 Code Example",
            "❌ Bad Code Example",
            "✅ Good Code Example",
            "🤔 Why This Concept Matters",
            "🎭 Different Ways Interviewers Ask This",
            "😄 How will you remember it?",
            "💡 Tip",
            "💼 Interview Pro Tips",
            "🧠 Practice Problems",
            "🤖 Ask AI these questions",
            "🏢 Companies That Ask This"
        ]
        
        # Ensure all sections are present
        for section in sections:
            if section not in answer:
                answer += f"\n\n#### {section}\n\n[Content for {section}]"
        
        return answer
    
    @staticmethod
    def can_publish_to_db(sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if sheet data can be published to database.
        
        Args:
            sheet_data: Sheet data to validate
            
        Returns:
            Publication readiness status
        """
        validation_result = InterviewQuestionValidator.validate_sheet_data(sheet_data)
        
        if not validation_result["is_valid"]:
            return {
                "can_publish": False,
                "reason": "Validation failed",
                "errors": validation_result["errors"],
                "warnings": validation_result["warnings"]
            }
        
        # CRITICAL: Check for empty company types or invalid data
        questions = validation_result["data"].get("questions", [])
        for i, question in enumerate(questions):
            company_types = question.get("companyTypes", [])
            if not company_types:
                return {
                    "can_publish": False,
                    "reason": f"Question {i+1} has empty companyTypes - CRITICAL ERROR",
                    "errors": [f"Question {i+1}: companyTypes cannot be empty. This indicates the AI failed to properly analyze the question."],
                    "warnings": validation_result["warnings"]
                }
            
            priority = question.get("priority", "")
            frequency = question.get("frequency", "")
            
            # Check for invalid or missing critical data
            if not priority or not frequency:
                return {
                    "can_publish": False,
                    "reason": f"Question {i+1} has missing critical data (priority: {priority}, frequency: {frequency})",
                    "errors": [f"Question {i+1}: Missing priority or frequency data"],
                    "warnings": validation_result["warnings"]
                }
            
            # Check for default values that indicate AI didn't think properly
            if priority == "Medium" and frequency == "Asked Frequently" and len(company_types) <= 1:
                return {
                    "can_publish": False,
                    "reason": f"Question {i+1} has generic default values - AI needs to analyze this question more carefully",
                    "errors": [f"Question {i+1}: Generic defaults detected. AI should provide specific analysis."],
                    "warnings": validation_result["warnings"]
                }
        
        return {
            "can_publish": True,
            "reason": "All validations passed",
            "errors": [],
            "warnings": validation_result["warnings"],
            "validated_data": validation_result["data"]
        } 