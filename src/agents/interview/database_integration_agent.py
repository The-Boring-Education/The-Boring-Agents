"""Database Integration Agent - Handles saving interview sheets and questions to the database."""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from langchain.prompts import PromptTemplate
from rich.console import Console

from ...core.base_agent import BaseAgent
from ...core.config import config
from ...utils.helpers import generate_filename, save_json_file, load_json_file
from ...utils.validation import InterviewQuestionValidator

console = Console()


class DatabaseIntegrationAgent(BaseAgent):
    """Agent responsible for integrating with the database to save interview sheets and questions."""
    
    def __init__(self, **kwargs):
        """Initialize the database integration agent."""
        super().__init__(**kwargs)
        self.api_base_url = config.api_v1_url
        self.logger.info("Database Integration Agent initialized")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for database integration."""
        return {
            "validate_sheet_data": PromptTemplate(
                input_variables=["sheet_data"],
                template="""Validate the following interview sheet data for database compatibility:

Sheet Data:
{sheet_data}

Please check:
1. All required fields are present
2. Data types are correct
3. Question structure is valid
4. No sensitive information is exposed

Return a JSON response with:
- valid: boolean
- errors: list of error messages
- warnings: list of warning messages
- recommendations: list of improvement suggestions"""
            ),
            
            "format_sheet_for_db": PromptTemplate(
                input_variables=["sheet_data", "sheet_id"],
                template="""Format the following interview sheet data for database insertion:

Original Sheet Data:
{sheet_data}

Target Sheet ID: {sheet_id}

Please format the data according to the database schema:
- Ensure all required fields are present
- Convert data types as needed
- Structure questions properly
- Add any missing metadata

Return the formatted data as JSON."""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content for database integration."""
        if content_type == "validate_sheet":
            return self.validate_sheet_data(kwargs.get("sheet_data", {}))
        elif content_type == "format_sheet":
            return self.format_sheet_for_database(kwargs.get("sheet_data", {}), kwargs.get("sheet_id", ""))
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}
    
    def validate_sheet_data(self, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate sheet data before database insertion."""
        try:
            # Transform the data format to match validation expectations
            transformed_data = self._transform_sheet_data_for_validation(sheet_data)
            
            # Use the validator from utils
            validator = InterviewQuestionValidator()
            validation_result = validator.can_publish_to_db(transformed_data)
            
            if validation_result.get("can_publish", False):
                return {
                    "status": "success",
                    "valid": True,
                    "message": "Sheet data is valid for database insertion",
                    "warnings": validation_result.get("warnings", []),
                    "recommendations": validation_result.get("recommendations", [])
                }
            else:
                return {
                    "status": "error",
                    "valid": False,
                    "message": validation_result.get("reason", "Sheet data validation failed"),
                    "errors": validation_result.get("errors", []),
                    "warnings": validation_result.get("warnings", [])
                }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error validating sheet data: {str(e)}",
                "valid": False
            }
    
    def format_sheet_for_database(self, sheet_data: Dict[str, Any], sheet_id: str) -> Dict[str, Any]:
        """Format sheet data for database insertion."""
        try:
            # Format the sheet data according to the database schema
            formatted_data = {
                "id": sheet_id,
                "name": sheet_data.get("name", ""),
                "slug": sheet_data.get("slug", ""),
                "description": sheet_data.get("description", ""),
                "roadmap": sheet_data.get("roadmap", "Tech"),
                "difficulty": sheet_data.get("difficulty", "Intermediate"),
                "target_audience": sheet_data.get("target_audience", "Developers"),
                "question_count": sheet_data.get("question_count", 0),
                "questions": [],
                "created_at": sheet_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "cover_image_url": sheet_data.get("cover_image_url", ""),
                "meta_content": sheet_data.get("meta_content", ""),
                "is_premium": False,
                "price": 0,
                "live_on": datetime.now(timezone.utc).isoformat(),
                "features": []
            }
            
            # Format questions
            for question in sheet_data.get("questions", []):
                formatted_question = {
                    "question": question.get("question", ""),
                    "answer": question.get("answer", ""),
                    "difficulty": question.get("difficulty", "Medium"),
                    "frequency": question.get("frequency", "Medium"),
                    "priority": question.get("priority", "Medium"),
                    "company_types": question.get("company_types", ["Startup", "MNC"]),
                    "created_at": question.get("created_at", datetime.now(timezone.utc).isoformat())
                }
                formatted_data["questions"].append(formatted_question)
            
            return {
                "status": "success",
                "data": formatted_data,
                "message": "Sheet data formatted successfully for database"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error formatting sheet data: {str(e)}"
            }
    
    def add_questions_to_sheet(self, sheet_id: str, questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add questions to an existing sheet in the database."""
        try:
            # Validate that the sheet exists first
            sheet_exists = self._check_sheet_exists(sheet_id)
            if not sheet_exists:
                return {
                    "status": "error",
                    "message": f"Sheet with ID {sheet_id} does not exist in the database"
                }
            
            # Add each question to the sheet
            added_questions = []
            for question in questions:
                question_data = {
                    "question": question.get("question", ""),
                    "answer": question.get("answer", ""),
                    "difficulty": question.get("difficulty", "Medium"),
                    "frequency": question.get("frequency", "Medium"),
                    "priority": question.get("priority", "Medium"),
                    "company_types": question.get("company_types", ["Startup", "MNC"])
                }
                
                # Make API call to add question
                response = self._add_question_to_sheet(sheet_id, question_data)
                if response.get("status") == "success":
                    added_questions.append(question_data)
                else:
                    console.print(f"[red]Failed to add question: {response.get('message', 'Unknown error')}[/red]")
            
            return {
                "status": "success",
                "message": f"Successfully added {len(added_questions)} questions to sheet {sheet_id}",
                "added_questions": len(added_questions),
                "total_questions": len(questions)
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding questions to sheet: {str(e)}"
            }
    
    def _check_sheet_exists(self, sheet_id: str) -> bool:
        """Check if a sheet exists in the database."""
        try:
            url = f"{self.api_base_url}/interview-prep/{sheet_id}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            console.print(f"[yellow]Warning: Could not check if sheet exists: {str(e)}[/yellow]")
            return True  # Assume it exists if we can't check
    
    def _add_question_to_sheet(self, sheet_id: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a single question to a sheet via API."""
        try:
            url = f"{self.api_base_url}/interview-prep/{sheet_id}/question"
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=question_data, headers=headers, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                return {
                    "status": "success",
                    "message": "Question added successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to add question: {response.status_code} - {response.text}"
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error adding question: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error adding question: {str(e)}"
            }
    
    def _transform_sheet_data_for_validation(self, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform sheet data to match validation expectations."""
        transformed_data = sheet_data.copy()
        
        # Transform questions to match validation format
        transformed_questions = []
        for question in sheet_data.get("questions", []):
            transformed_question = {
                "title": question.get("question", "")[:100] + "...",  # Use question as title
                "question": question.get("question", ""),
                "answer": question.get("answer", ""),
                "difficulty": question.get("difficulty", "Medium"),
                "frequency": question.get("frequency", "Medium"),
                "priority": question.get("priority", "Medium"),
                "companyTypes": question.get("company_types", ["Startup", "MNC"]),  # Transform field name
                "roadmap": sheet_data.get("roadmap", "Tech")
            }
            transformed_questions.append(transformed_question)
        
        transformed_data["questions"] = transformed_questions
        return transformed_data
    
    def create_new_sheet(self, sheet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sheet in the database."""
        try:
            url = f"{self.api_base_url}/interview-prep"
            headers = {
                "Content-Type": "application/json"
            }
            
            # Format sheet data for creation
            formatted_sheet = {
                "name": sheet_data.get("name", ""),
                "description": sheet_data.get("description", ""),
                "roadmap": sheet_data.get("roadmap", "Tech"),
                "difficulty": sheet_data.get("difficulty", "Intermediate"),
                "target_audience": sheet_data.get("target_audience", "Developers"),
                "cover_image_url": sheet_data.get("cover_image_url", ""),
                "meta_content": sheet_data.get("meta_content", ""),
                "is_premium": False,
                "price": 0,
                "features": []
            }
            
            response = requests.post(url, json=formatted_sheet, headers=headers, timeout=30)
            
            if response.status_code == 200 or response.status_code == 201:
                result = response.json()
                return {
                    "status": "success",
                    "message": "Sheet created successfully",
                    "sheet_id": result.get("data", {}).get("_id", ""),
                    "data": result
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to create sheet: {response.status_code} - {response.text}"
                }
        
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error creating sheet: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error creating sheet: {str(e)}"
            } 