"""Database Integration Agent for managing interview sheet API operations."""

from typing import Dict, Any, List, Optional
import requests
import json
from datetime import datetime

from ...core.base_agent import BaseAgent


class DatabaseIntegrationAgent(BaseAgent):
    """Agent for managing all database operations for interview sheets."""
    
    def __init__(self, api_base_url: str = None, **kwargs):
        """Initialize the database agent.
        
        Args:
            api_base_url: Base URL for the API
            **kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.api_base_url = api_base_url or "https://tbe-dev-git-development-tbe.vercel.app/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Interview-Sheet-AI-Agent/1.0'
        })
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Database agent doesn't need prompt templates."""
        return {}
    
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        """Database agent doesn't generate content directly."""
        raise NotImplementedError("Database agent handles API operations, not content generation")
    
    def fetch_all_interview_sheets(self) -> List[Dict[str, Any]]:
        """Fetch all interview sheets from the database.
        
        Returns:
            List of interview sheet data
        """
        try:
            url = f"{self.api_base_url}/interview-prep"
            self.logger.info(f"Fetching all interview sheets from: {url}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            sheets = data if isinstance(data, list) else data.get('data', [])
            
            self.logger.info(f"Successfully fetched {len(sheets)} interview sheets")
            return sheets
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching interview sheets: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching sheets: {str(e)}")
            return []
    
    def fetch_interview_sheet(self, sheet_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a specific interview sheet by ID.
        
        Args:
            sheet_id: ID of the sheet to fetch
            
        Returns:
            Sheet data or None if not found
        """
        try:
            # First, get all sheets and find the one with matching ID
            all_sheets = self.fetch_all_interview_sheets()
            
            for sheet in all_sheets:
                if sheet.get('_id') == sheet_id:
                    self.logger.info(f"Found sheet: {sheet.get('name', 'Unknown')}")
                    return sheet
            
            self.logger.warning(f"Sheet with ID {sheet_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error fetching sheet {sheet_id}: {str(e)}")
            return None
    
    def fetch_sheet_questions(self, sheet_id: str) -> List[Dict[str, Any]]:
        """Fetch all questions for a specific sheet.
        
        Args:
            sheet_id: ID of the sheet
            
        Returns:
            List of question data
        """
        try:
            url = f"{self.api_base_url}/interview-prep/{sheet_id}"
            self.logger.info(f"Fetching questions for sheet {sheet_id}")
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract questions from the response
            questions = []
            if isinstance(data, dict):
                if 'questions' in data:
                    questions = data['questions']
                elif 'data' in data and isinstance(data['data'], dict) and 'questions' in data['data']:
                    questions = data['data']['questions']
                elif 'data' in data and isinstance(data['data'], list):
                    questions = data['data']
                else:
                    # Try to extract questions from the response structure
                    questions = self._extract_questions_from_response(data)
            elif isinstance(data, list):
                questions = data
            
            self.logger.info(f"Successfully fetched {len(questions)} questions for sheet {sheet_id}")
            return questions
            
        except requests.RequestException as e:
            self.logger.error(f"Error fetching questions for sheet {sheet_id}: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error fetching questions: {str(e)}")
            return []
    
    def update_question_answer(self, sheet_id: str, question_id: str, 
                             new_answer: str, frequency_analysis: Dict[str, Any] = None) -> bool:
        """Update a question's answer in the database.
        
        Args:
            sheet_id: ID of the sheet
            question_id: ID of the question
            new_answer: New answer content
            frequency_analysis: Frequency analysis data (optional)
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            url = f"{self.api_base_url}/interview-prep/{sheet_id}/question/{question_id}"
            
            payload = {
                "answer": new_answer
            }
            
            # Add frequency analysis if provided
            if frequency_analysis:
                payload.update({
                    "frequency": frequency_analysis.get("frequency", "Medium"),
                    "companies": frequency_analysis.get("companies", []),
                    "difficulty": frequency_analysis.get("difficulty", "Medium")
                })
            
            self.logger.info(f"Updating question {question_id} in sheet {sheet_id}")
            
            response = self.session.patch(url, json=payload, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"Successfully updated question {question_id}")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Error updating question {question_id}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating question: {str(e)}")
            return False
    
    def add_question_to_sheet(self, sheet_id: str, question: str, 
                            answer: str, frequency_analysis: Dict[str, Any] = None) -> bool:
        """Add a new question to an existing sheet.
        
        Args:
            sheet_id: ID of the sheet
            question: Question text
            answer: Answer text
            frequency_analysis: Frequency analysis data (optional)
            
        Returns:
            True if addition was successful, False otherwise
        """
        try:
            # Note: This endpoint might need to be implemented on the backend
            url = f"{self.api_base_url}/interview-prep/{sheet_id}/question"
            
            payload = {
                "question": question,
                "answer": answer
            }
            
            # Add frequency analysis if provided
            if frequency_analysis:
                payload.update({
                    "frequency": frequency_analysis.get("frequency", "Medium"),
                    "companies": frequency_analysis.get("companies", []),
                    "difficulty": frequency_analysis.get("difficulty", "Medium")
                })
            
            self.logger.info(f"Adding new question to sheet {sheet_id}")
            
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            self.logger.info(f"Successfully added new question to sheet {sheet_id}")
            return True
            
        except requests.RequestException as e:
            self.logger.error(f"Error adding question to sheet {sheet_id}: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response status: {e.response.status_code}")
                self.logger.error(f"Response text: {e.response.text}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error adding question: {str(e)}")
            return False
    
    def create_new_sheet(self, sheet_data: Dict[str, Any]) -> Optional[str]:
        """Create a new interview sheet in the database.
        
        Args:
            sheet_data: Complete sheet data
            
        Returns:
            Sheet ID if creation was successful, None otherwise
        """
        try:
            url = f"{self.api_base_url}/interview-prep"
            
            self.logger.info(f"Creating new sheet: {sheet_data.get('name', 'Unknown')}")
            
            response = self.session.post(url, json=sheet_data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            sheet_id = result.get('_id') or result.get('id') or result.get('data', {}).get('_id')
            
            if sheet_id:
                self.logger.info(f"Successfully created new sheet with ID: {sheet_id}")
                return sheet_id
            else:
                self.logger.warning("Sheet created but no ID returned")
                return None
            
        except requests.RequestException as e:
            self.logger.error(f"Error creating new sheet: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating sheet: {str(e)}")
            return None
    
    def validate_api_connection(self) -> bool:
        """Validate that we can connect to the API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            url = f"{self.api_base_url}/interview-prep"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.logger.info("API connection validated successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"API connection validation failed: {str(e)}")
            return False
    
    def _extract_questions_from_response(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract questions from various response formats.
        
        Args:
            data: Response data
            
        Returns:
            List of questions
        """
        questions = []
        
        # Try different possible structures
        possible_paths = [
            ['questions'],
            ['data', 'questions'],
            ['result', 'questions'],
            ['data'],
            ['items'],
            ['content']
        ]
        
        for path in possible_paths:
            current = data
            try:
                for key in path:
                    current = current[key]
                
                if isinstance(current, list):
                    questions = current
                    break
            except (KeyError, TypeError):
                continue
        
        return questions
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status and connectivity information.
        
        Returns:
            Status information
        """
        status = {
            "api_base_url": self.api_base_url,
            "connection_ok": False,
            "sheets_available": 0,
            "last_check": None
        }
        
        try:
            status["connection_ok"] = self.validate_api_connection()
            if status["connection_ok"]:
                sheets = self.fetch_all_interview_sheets()
                status["sheets_available"] = len(sheets)
            
            status["last_check"] = datetime.now().isoformat()
            
        except Exception as e:
            self.logger.error(f"Error getting API status: {str(e)}")
        
        return status