"""Quiz Uploader Agent - Validates and uploads quizzes to the database."""

import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from langchain.prompts import PromptTemplate
from rich.console import Console
from rich.table import Table

from ...core.base_agent import BaseAgent
from ...core.config import config
from ...utils.helpers import load_json_file
from .types import QuizModel, QuizQuestionModel, QuizDifficulty

console = Console()


class QuizUploader(BaseAgent):
    """Agent responsible for validating and uploading quizzes to the database."""
    
    def __init__(self, api_url: str = None, admin_secret: str = "TBEAdmin", **kwargs):
        """Initialize the Quiz Uploader Agent.
        
        Args:
            api_url: API base URL (defaults to config.api_base_url)
            admin_secret: Admin secret for authentication
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(**kwargs)
        
        self.api_url = (api_url or config.api_base_url).rstrip('/')
        self.admin_secret = admin_secret
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'x-admin-secret': self.admin_secret,
            'Content-Type': 'application/json'
        })
        
        self.logger.info(f"Quiz Uploader Agent initialized with API URL: {self.api_url}")
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for quiz validation."""
        return {
            "validate_quiz_content": PromptTemplate(
                input_variables=["quiz_data"],
                template="""Validate the following quiz data for quality and correctness:

Quiz Data:
{quiz_data}

Please check:
1. **Question Quality**
   - Are all questions clear and unambiguous?
   - Do they have exactly 4 options?
   - Is the correct answer index valid (0-3)?
   - Are explanations helpful?

2. **Content Accuracy**
   - Are the questions technically correct?
   - Do the correct answers make sense?
   - Are the distractors plausible but wrong?

3. **Data Integrity**
   - All required fields present?
   - Proper data types?
   - No duplicate questions?

Return a JSON response with:
{{
    "valid": true/false,
    "errors": ["list of critical errors"],
    "warnings": ["list of warnings"],
    "suggestions": ["list of improvements"]
}}"""
            ),
            
            "prepare_quiz_for_api": PromptTemplate(
                input_variables=["quiz_data"],
                template="""Prepare the quiz data for API submission by ensuring all fields match the expected schema.

Original Quiz Data:
{quiz_data}

Expected Schema:
- categoryId: string (unique identifier)
- categoryName: string
- categoryDescription: string
- categoryIcon: string (emoji or icon name)
- questions: array of question objects
- isActive: boolean

Each question should have:
- question: string
- options: array of strings (exactly 4)
- correctAnswer: number (0-3)
- explanation: string
- detailedExplanation: string
- difficulty: string (easy/medium/hard)

Clean and format the data appropriately."""
            )
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content for quiz uploading."""
        if content_type == "validate_quiz":
            return self.validate_quiz(kwargs.get("quiz_data", {}))
        elif content_type == "upload_quiz":
            return self.upload_quiz(kwargs.get("quiz_data", {}))
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}
    
    def validate_quiz(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quiz data before uploading."""
        console.print("[blue]🔍 Validating quiz data...[/blue]")
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        try:
            # Basic structure validation
            required_fields = ["categoryName", "categoryDescription", "categoryIcon", "questions"]
            for field in required_fields:
                if field not in quiz_data:
                    validation_result["errors"].append(f"Missing required field: {field}")
                    validation_result["valid"] = False
            
            # Validate questions
            questions = quiz_data.get("questions", [])
            if not questions:
                validation_result["errors"].append("Quiz must have at least one question")
                validation_result["valid"] = False
            else:
                for i, question in enumerate(questions):
                    q_errors = self._validate_question(question, i)
                    validation_result["errors"].extend(q_errors)
                    if q_errors:
                        validation_result["valid"] = False
            

            
            # Additional quality checks
            if len(questions) < 10:
                validation_result["warnings"].append(f"Quiz has only {len(questions)} questions. Consider adding more for better assessment.")
            
            if len(questions) > 50:
                validation_result["warnings"].append(f"Quiz has {len(questions)} questions. Consider splitting into multiple quizzes.")
            
            # Check difficulty distribution
            difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
            for q in questions:
                diff = q.get("difficulty", "medium")
                if diff in difficulty_counts:
                    difficulty_counts[diff] += 1
            
            if difficulty_counts["easy"] == 0:
                validation_result["suggestions"].append("Consider adding some easy questions for beginners")
            if difficulty_counts["hard"] == 0:
                validation_result["suggestions"].append("Consider adding some hard questions for advanced users")
            
            # Display validation results
            self._display_validation_results(validation_result)
            
            return {
                "status": "success" if validation_result["valid"] else "error",
                "validation_result": validation_result
            }
            
        except Exception as e:
            self.logger.error(f"Error validating quiz: {str(e)}")
            return {
                "status": "error",
                "message": f"Validation failed: {str(e)}",
                "validation_result": validation_result
            }
    
    def upload_quiz(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Upload quiz to the database via API."""
        console.print("[green]🚀 Uploading quiz to database...[/green]")
        num_questions = len(quiz_data.get("questions", []))
        self.logger.info(f"Preparing upload - questions={num_questions}")
        
        # Validate first
        validation_result = self.validate_quiz(quiz_data)
        if validation_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Quiz validation failed. Please fix errors before uploading.",
                "validation_result": validation_result.get("validation_result")
            }
        
        try:

            # Prepare API endpoint for create
            url = f"{self.api_url}/api/v1/quiz"
            console.print(f"[blue]📡 Sending request to: {url}[/blue]")
            self.logger.info("POST /api/v1/quiz - creating new quiz")
            response = self.session.post(url, json=quiz_data, timeout=30)
            self.logger.info(f"POST response status={response.status_code}")
            if response.status_code in [200, 201]:
                console.print("[green]✅ Quiz uploaded successfully![/green]")
                return {
                    "status": "success",
                    "message": "Quiz uploaded successfully",
                    "response": response.json(),
                    "quiz_id": response.json().get("data", {}).get("_id") \
                        if isinstance(response.json(), dict) else None
                }

            # If creation failed, check if unique constraint caused it and then try update
            self.logger.warning(f"Create failed (status={response.status_code}). Body={response.text[:500]}")
            exists_after = self._get_quiz_by_category(category_id)
            if exists_after is not None:
                self.logger.info("Detected existing quiz after failed create. Attempting update...")
                return self.update_quiz(category_id, quiz_data)

            error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
            console.print(f"[red]❌ Upload failed: {error_msg}[/red]")
            return {
                "status": "error",
                "message": f"Upload failed: {error_msg}",
                "status_code": response.status_code
            }
                
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "message": "Request timeout - API server may be slow or down"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "error",
                "message": "Connection error - check if API server is running"
            }
        except Exception as e:
            self.logger.error(f"Error uploading quiz: {str(e)}")
            return {
                "status": "error",
                "message": f"Upload failed: {str(e)}"
            }
    
    def upload_quiz_from_file(self, file_path: str) -> Dict[str, Any]:
        """Upload quiz from a JSON file."""
        console.print(f"[blue]📄 Loading quiz from file: {file_path}[/blue]")
        
        try:
            # Load quiz data
            data = load_json_file(file_path)
            
            # Extract quiz data
            if "quiz" in data:
                quiz_data = data["quiz"]
            else:
                quiz_data = data
            
            # Upload the quiz
            return self.upload_quiz(quiz_data)
            
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"File not found: {file_path}"
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": f"Invalid JSON in file: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error loading file: {str(e)}"
            }
    
    def bulk_upload_quizzes(self, quiz_files: List[str]) -> Dict[str, Any]:
        """Upload multiple quizzes from files."""
        console.print(f"[green]📚 Bulk uploading {len(quiz_files)} quizzes...[/green]")
        
        results = {
            "total": len(quiz_files),
            "successful": 0,
            "failed": 0,
            "results": []
        }
        
        for i, file_path in enumerate(quiz_files):
            console.print(f"\n[blue]Processing {i+1}/{len(quiz_files)}: {file_path}[/blue]")
            
            result = self.upload_quiz_from_file(file_path)
            
            if result.get("status") == "success":
                results["successful"] += 1
                results["results"].append({
                    "file": file_path,
                    "status": "success",
                    "quiz_id": result.get("quiz_id")
                })
            else:
                results["failed"] += 1
                results["results"].append({
                    "file": file_path,
                    "status": "failed",
                    "error": result.get("message")
                })
        
        # Display summary
        self._display_bulk_upload_summary(results)
        
        return results
    
    def update_quiz(self, category_id: str, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing quiz by categoryId."""
        console.print(f"[blue]🔄 Updating quiz: {category_id}[/blue]")
        self.logger.info(f"PUT /api/v1/quiz/{category_id} - updating quiz")
        
        # Validate the updated data
        validation_result = self.validate_quiz(quiz_data)
        if validation_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Quiz validation failed. Please fix errors before updating.",
                "validation_result": validation_result.get("validation_result")
            }
        
        try:
            url = f"{self.api_url}/api/v1/quiz/{category_id}"
            response = self.session.put(url, json=quiz_data, timeout=30)
            self.logger.info(f"PUT response status={response.status_code}")
            
            if response.status_code == 200:
                console.print("[green]✅ Quiz updated successfully![/green]")
                return {
                    "status": "success",
                    "message": "Quiz updated successfully",
                    "response": response.json()
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                self.logger.warning(f"Update failed - {error_msg}")
                return {
                    "status": "error",
                    "message": f"Update failed: {error_msg}"
                }
                
        except Exception as e:
            self.logger.error(f"Update error: {str(e)}")
            return {
                "status": "error",
                "message": f"Update failed: {str(e)}"
            }
    
    def delete_quiz(self, quiz_id: str) -> Dict[str, Any]:
        """Delete a quiz from the database."""
        console.print(f"[red]🗑️ Deleting quiz: {quiz_id}[/red]")
        
        if not console.input("[yellow]Are you sure you want to delete this quiz? (y/N): [/yellow]").lower().startswith('y'):
            return {
                "status": "cancelled",
                "message": "Deletion cancelled by user"
            }
        
        try:
            url = f"{self.api_url}/api/v1/quiz/{quiz_id}"
            response = self.session.delete(url, timeout=30)
            
            if response.status_code in [200, 204]:
                console.print("[green]✅ Quiz deleted successfully![/green]")
                return {
                    "status": "success",
                    "message": "Quiz deleted successfully"
                }
            else:
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                return {
                    "status": "error",
                    "message": f"Deletion failed: {error_msg}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Deletion failed: {str(e)}"
            }
    
    def _validate_question(self, question: Dict[str, Any], index: int) -> List[str]:
        """Validate a single question."""
        errors = []
        prefix = f"Question {index + 1}"
        
        # Required fields
        required = ["question", "options", "correctAnswer", "explanation", "detailedExplanation", "difficulty"]
        for field in required:
            if field not in question:
                errors.append(f"{prefix}: Missing required field '{field}'")
        
        # Validate options
        options = question.get("options", [])
        if len(options) != 4:
            errors.append(f"{prefix}: Must have exactly 4 options (found {len(options)})")
        
        # Validate correct answer
        correct_answer = question.get("correctAnswer")
        if correct_answer is None:
            errors.append(f"{prefix}: Missing correctAnswer")
        elif not isinstance(correct_answer, int) or correct_answer < 0 or correct_answer > 3:
            errors.append(f"{prefix}: correctAnswer must be 0-3 (found {correct_answer})")
        
        # Validate difficulty
        difficulty = question.get("difficulty", "").lower()
        if difficulty not in ["easy", "medium", "hard"]:
            errors.append(f"{prefix}: Invalid difficulty '{difficulty}' (must be easy/medium/hard)")
        
        # Validate text fields
        if not question.get("question", "").strip():
            errors.append(f"{prefix}: Question text cannot be empty")
        
        if not question.get("explanation", "").strip():
            errors.append(f"{prefix}: Explanation cannot be empty")
        
        return errors
    
    def _display_validation_results(self, validation_result: Dict[str, Any]):
        """Display validation results in a formatted table."""
        table = Table(title="Quiz Validation Results")
        table.add_column("Type", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Details", style="white")
        
        # Add rows
        if validation_result["errors"]:
            table.add_row("❌ Errors", str(len(validation_result["errors"])), 
                         "\n".join(validation_result["errors"][:3]) + 
                         ("\n..." if len(validation_result["errors"]) > 3 else ""))
        
        if validation_result["warnings"]:
            table.add_row("⚠️  Warnings", str(len(validation_result["warnings"])), 
                         "\n".join(validation_result["warnings"]))
        
        if validation_result["suggestions"]:
            table.add_row("💡 Suggestions", str(len(validation_result["suggestions"])), 
                         "\n".join(validation_result["suggestions"]))
        
        # Overall status
        status = "✅ Valid" if validation_result["valid"] else "❌ Invalid"
        table.add_row("Status", status, "Ready for upload" if validation_result["valid"] else "Fix errors first")
        
        console.print(table)
    
    def _display_bulk_upload_summary(self, results: Dict[str, Any]):
        """Display bulk upload summary."""
        table = Table(title="Bulk Upload Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="green")
        
        table.add_row("Total Quizzes", str(results["total"]))
        table.add_row("✅ Successful", str(results["successful"]))
        table.add_row("❌ Failed", str(results["failed"]))
        table.add_row("Success Rate", f"{(results['successful'] / max(results['total'], 1)) * 100:.1f}%")
        
        console.print(table)
        
        # Show failed uploads
        if results["failed"] > 0:
            console.print("\n[red]Failed Uploads:[/red]")
            for result in results["results"]:
                if result["status"] == "failed":
                    console.print(f"  • {result['file']}: {result['error']}")
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to the API."""
        console.print(f"[blue]🔌 Testing connection to: {self.api_url}[/blue]")
        
        try:
            # Try a simple health check or GET request
            url = f"{self.api_url}/api/health"
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                console.print("[green]✅ Connection successful![/green]")
                return {"status": "success", "message": "API connection successful", "api_url": self.api_url}

            # Fallback to categories endpoint (exists in tbe-webapp)
            categories_url = f"{self.api_url}/api/v1/quiz"
            self.logger.info(f"Health check fallback: GET {categories_url}")
            resp2 = self.session.get(categories_url, timeout=10)
            if resp2.status_code == 200:
                console.print("[green]✅ Connection successful via /api/v1/quiz![/green]")
                return {"status": "success", "message": "API connection successful", "api_url": self.api_url}

            console.print(f"[yellow]⚠️  API responded with status: {response.status_code} (health), {resp2.status_code} (categories)[/yellow]")
            return {
                "status": "warning",
                "message": f"API accessible but returned status health={response.status_code} categories={resp2.status_code}",
                "api_url": self.api_url
            }
                
        except requests.exceptions.ConnectionError:
            console.print("[red]❌ Connection failed - API server not reachable[/red]")
            return {
                "status": "error",
                "message": "Cannot connect to API server",
                "api_url": self.api_url
            }
        except Exception as e:
            console.print(f"[red]❌ Connection test failed: {str(e)}[/red]")
            return {
                "status": "error",
                "message": f"Connection test failed: {str(e)}",
                "api_url": self.api_url
            } 

    def _get_quiz_by_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Fetch quiz by categoryId. Returns dict when found, None otherwise."""
        try:
            url = f"{self.api_url}/api/v1/quiz/{category_id}"
            self.logger.info(f"GET {url}")
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data") if isinstance(data, dict) else data
            return None
        except Exception as e:
            self.logger.warning(f"Failed to check existing quiz for categoryId={category_id}: {str(e)}")
            return None