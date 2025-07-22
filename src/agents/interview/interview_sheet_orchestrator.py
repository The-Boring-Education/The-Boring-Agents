"""Interview Sheet Orchestrator for managing the complete interview sheet revamping and creation process."""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

from ...core.base_agent import BaseAgent
from ...utils.validation import InterviewQuestionValidator
from .database_integration_agent import DatabaseIntegrationAgent
from .answer_enhancement_agent import AnswerEnhancementAgent
from .frequency_analysis_agent import FrequencyAnalysisAgent
from .question_generator_agent import QuestionGeneratorAgent
from .interview_research_agent import InterviewResearchAgent
from .quality_review_agent import QualityReviewAgent
from .mdx_styling_agent import MDXStylingAgent


class InterviewSheetOrchestrator(BaseAgent):
    """Main orchestrator for managing interview sheet revamping and creation."""
    
    def __init__(self, **kwargs):
        """Initialize the orchestrator with all required agents."""
        super().__init__(**kwargs)
        
        # Initialize all specialized agents
        self.database_agent = DatabaseIntegrationAgent()
        self.answer_enhancement_agent = AnswerEnhancementAgent()
        self.frequency_analysis_agent = FrequencyAnalysisAgent()
        self.question_generator_agent = QuestionGeneratorAgent()
        self.research_agent = InterviewResearchAgent()
        self.quality_agent = QualityReviewAgent()
        self.mdx_styling_agent = MDXStylingAgent()
        
        self.logger.info("Interview Sheet Orchestrator initialized with all agents")
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Orchestrator doesn't need prompt templates."""
        return {}
    
    def generate_content(self, *args, **kwargs) -> dict:
        """Orchestrator doesn't generate content directly."""
        raise NotImplementedError("Orchestrator coordinates other agents, doesn't generate content")
    
    def revamp_existing_sheet(self, sheet_id: str) -> Dict[str, Any]:
        """Revamp an existing interview sheet with world-class quality.
        
        Args:
            sheet_id: ID of the sheet to revamp
            
        Returns:
            Comprehensive revamping results
        """
        self.logger.info(f"Starting revamp process for sheet: {sheet_id}")
        
        try:
            # Step 1: Fetch sheet data
            sheet_data = self.database_agent.fetch_interview_sheet(sheet_id)
            if not sheet_data:
                raise ValueError(f"Sheet with ID {sheet_id} not found")
            
            sheet_name = sheet_data.get('name', 'Unknown Sheet')
            self.logger.info(f"Fetched sheet: {sheet_name}")
            
            # Step 2: Fetch all questions
            questions = self.database_agent.fetch_sheet_questions(sheet_id)
            if not questions:
                self.logger.warning(f"No questions found for sheet {sheet_id}")
                return {"error": "No questions found", "sheet_id": sheet_id}
            
            self.logger.info(f"Found {len(questions)} questions to revamp")
            
            # Step 3: Research phase
            self.logger.info("Starting research phase...")
            research_insights = self.research_agent.analyze_interview_topic(
                sheet_name, 
                sheet_data.get('description', ''), 
                questions
            )
            
            # Step 4: Process each question
            enhanced_questions = []
            failed_updates = []
            statistics = {
                "total_questions": len(questions),
                "enhanced": 0,
                "failed": 0,
                "added": 0
            }
            
            for i, question_data in enumerate(questions):
                try:
                    self.logger.info(f"Processing question {i+1}/{len(questions)}")
                    
                    question_id = question_data.get('_id', '')
                    question_text = question_data.get('question', '')
                    existing_answer = question_data.get('answer', '')
                    
                    # Step 4a: Analyze frequency
                    frequency_analysis = self.frequency_analysis_agent.analyze_question_frequency(
                        question_text, sheet_name
                    )
                    
                    # Step 4b: Create enhanced answer
                    enhanced_answer = self.answer_enhancement_agent.create_world_class_answer(
                        question_text, existing_answer, sheet_name, research_insights
                    )
                    
                    # Step 4c: Apply MDX styling
                    styled_answer = self.mdx_styling_agent.format_mdx_content(
                        enhanced_answer, "interview_answer"
                    )
                    
                    # Step 4d: Quality review
                    quality_review = self.quality_agent.review_qa_pair(
                        question_text, styled_answer, sheet_name
                    )
                    
                    # Step 4e: Validate question data before updating
                    question_data = {
                        "title": f"Question: {question_text[:50]}...",
                        "question": question_text,
                        "answer": styled_answer,
                        "frequency": frequency_analysis.get("overall_frequency", "Asked Frequently"),
                        "companyTypes": self._extract_company_types_from_analysis(frequency_analysis),
                        "priority": "High" if frequency_analysis.get("overall_frequency") in ["Most Asked", "Very High"] else "Medium"
                    }
                    
                    validation_result = InterviewQuestionValidator.validate_question_data(question_data)
                    
                    if not validation_result["is_valid"]:
                        self.logger.error(f"Question validation failed: {validation_result['errors']}")
                        statistics["failed"] += 1
                        failed_updates.append({
                            "question_id": question_id,
                            "question": question_text,
                            "error": f"Validation failed: {validation_result['errors']}"
                        })
                        continue
                    
                    # Step 4f: Update database with validated data
                    update_success = self.database_agent.update_question_answer(
                        sheet_id, question_id, validation_result["data"]["answer"], frequency_analysis
                    )
                    
                    if update_success:
                        statistics["enhanced"] += 1
                        enhanced_questions.append({
                            "question_id": question_id,
                            "question": question_text,
                            "enhanced_answer": validation_result["data"]["answer"],
                            "quality_score": quality_review.get("overall_score", 0),
                            "frequency_analysis": frequency_analysis,
                            "validation_data": validation_result["data"]
                        })
                    else:
                        statistics["failed"] += 1
                        failed_updates.append({
                            "question_id": question_id,
                            "question": question_text,
                            "error": "Database update failed"
                        })
                    
                except Exception as e:
                    self.logger.error(f"Error processing question {i+1}: {str(e)}")
                    statistics["failed"] += 1
                    failed_updates.append({
                        "question_id": question_data.get('_id', ''),
                        "question": question_data.get('question', ''),
                        "error": str(e)
                    })
            
            # Step 5: Generate completion report
            completion_report = {
                "sheet_id": sheet_id,
                "sheet_name": sheet_name,
                "statistics": statistics,
                "research_insights": research_insights,
                "enhanced_questions": enhanced_questions,
                "failed_updates": failed_updates,
                "completion_time": datetime.now().isoformat()
            }
            
            self.logger.info(f"Revamp completed. Enhanced: {statistics['enhanced']}, Failed: {statistics['failed']}")
            
            return completion_report
            
        except Exception as e:
            self.logger.error(f"Error in revamp process: {str(e)}")
            return {
                "error": str(e),
                "sheet_id": sheet_id,
                "completion_time": datetime.now().isoformat()
            }
    
    def create_new_sheet(self, sheet_name: str, description: str, 
                        target_questions: int = 50) -> Dict[str, Any]:
        """Create a new world-class interview sheet from scratch.
        
        Args:
            sheet_name: Name of the new sheet
            description: Description of the sheet topic
            target_questions: Number of questions to generate
            
        Returns:
            Complete sheet data with metadata
        """
        self.logger.info(f"Creating new world-class sheet: {sheet_name}")
        
        try:
            # Step 1: Comprehensive research
            self.logger.info("Starting comprehensive research...")
            research_insights = self.research_agent.comprehensive_topic_research(sheet_name, description)
            
            # Step 2: Generate questions
            self.logger.info(f"Generating {target_questions} questions...")
            questions = self.question_generator_agent.generate_comprehensive_questions(
                sheet_name, description, research_insights, target_questions
            )
            
            # Step 3: Create enhanced answers for each question
            enhanced_qa_pairs = []
            total_quality_score = 0
            
            for i, question_data in enumerate(questions):
                try:
                    self.logger.info(f"Creating answer for question {i+1}/{len(questions)}")
                    
                    question_text = question_data.get('question', '')
                    
                    # Create enhanced answer
                    enhanced_answer = self.answer_enhancement_agent.create_world_class_answer(
                        question_text, "", sheet_name, research_insights
                    )
                    
                    # Apply MDX styling
                    styled_answer = self.mdx_styling_agent.format_mdx_content(
                        enhanced_answer, "interview_answer"
                    )
                    
                    # Quality review
                    quality_review = self.quality_agent.review_qa_pair(
                        question_text, styled_answer, sheet_name
                    )
                    
                    quality_score = quality_review.get("overall_score", 0)
                    total_quality_score += quality_score
                    
                    # Frequency analysis
                    frequency_analysis = self.frequency_analysis_agent.analyze_question_frequency(
                        question_text, sheet_name
                    )
                    
                    enhanced_qa_pairs.append({
                        "question": question_text,
                        "answer": styled_answer,
                        "quality_score": quality_score,
                        "frequency_analysis": frequency_analysis,
                        "difficulty": frequency_analysis.get("overall_frequency", "Medium")
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error creating answer for question {i+1}: {str(e)}")
                    continue
            
            # Step 4: Analyze difficulty distribution
            difficulty_distribution = self._analyze_difficulty_distribution(enhanced_qa_pairs)
            
            # Step 5: Create sheet data
            average_quality_score = total_quality_score / len(enhanced_qa_pairs) if enhanced_qa_pairs else 0
            
            # Convert enhanced_qa_pairs to proper question format for validation
            validated_questions = []
            for qa_pair in enhanced_qa_pairs:
                # Extract frequency and company types from frequency analysis
                frequency_analysis = qa_pair.get("frequency_analysis", {})
                frequency = frequency_analysis.get("overall_frequency", "Asked Frequently")
                companies = frequency_analysis.get("company_breakdown", {})
                
                # Determine company types from analysis
                company_types = []
                if companies.get("FAANG", {}).get("Frequency", "Low") in ["Very High", "High"]:
                    company_types.append("FAANG")
                if companies.get("Indian Unicorns", {}).get("Frequency", "Low") in ["Very High", "High"]:
                    company_types.append("Startup")
                if companies.get("Mid-size Startups", {}).get("Frequency", "Low") in ["Very High", "High"]:
                    company_types.append("MidSize")
                if companies.get("Service Companies", {}).get("Frequency", "Low") in ["Very High", "High"]:
                    company_types.append("MNC")
                
                # Fallback if no company types determined
                if not company_types:
                    company_types = ["MidSize", "MNC"]
                
                # Determine priority based on frequency
                priority = "High" if frequency in ["Most Asked", "Very High"] else "Medium"
                
                validated_question = {
                    "title": f"Question: {qa_pair['question'][:50]}...",
                    "question": qa_pair["question"],
                    "answer": qa_pair["answer"],
                    "frequency": frequency,
                    "companyTypes": company_types,
                    "priority": priority
                }
                validated_questions.append(validated_question)
            
            sheet_data = {
                "name": sheet_name,
                "description": description,
                "roadmap": "Tech",  # Default roadmap
                "total_questions": len(enhanced_qa_pairs),
                "average_quality_score": round(average_quality_score, 2),
                "difficulty_distribution": difficulty_distribution,
                "estimated_prep_time": f"{len(enhanced_qa_pairs) * 2} hours",
                "metadata": {
                    "indian_context": True,
                    "humor_integrated": True,
                    "quality_assured": True,
                    "research_based": True,
                    "created_at": datetime.now().isoformat()
                },
                "questions": validated_questions
            }
            
            # Step 5a: Validate sheet data before saving
            self.logger.info("Validating sheet data before saving...")
            validation_result = InterviewQuestionValidator.validate_sheet_data(sheet_data)
            
            if not validation_result["is_valid"]:
                self.logger.error(f"Sheet validation failed: {validation_result['errors']}")
                raise ValueError(f"Sheet validation failed: {validation_result['errors']}")
            
            if validation_result["warnings"]:
                self.logger.warning(f"Sheet validation warnings: {validation_result['warnings']}")
            
            # Step 5b: Check if sheet can be published
            publication_check = InterviewQuestionValidator.can_publish_to_db(sheet_data)
            
            if not publication_check["can_publish"]:
                self.logger.error(f"Sheet cannot be published: {publication_check['reason']}")
                raise ValueError(f"Sheet cannot be published: {publication_check['reason']}")
            
            self.logger.info("✅ Sheet validation passed - ready for publication")
            
            # Step 6: Save to file
            filepath = self._save_sheet_to_file(sheet_data)
            
            completion_report = {
                "sheet_data": sheet_data,
                "statistics": {
                    "total_questions": len(enhanced_qa_pairs),
                    "average_quality_score": average_quality_score,
                    "difficulty_distribution": difficulty_distribution
                },
                "research_insights": research_insights,
                "filepath": filepath,
                "completion_time": datetime.now().isoformat()
            }
            
            self.logger.info(f"New sheet created successfully: {len(enhanced_qa_pairs)} questions")
            
            return completion_report
            
        except Exception as e:
            self.logger.error(f"Error creating new sheet: {str(e)}")
            return {
                "error": str(e),
                "sheet_name": sheet_name,
                "completion_time": datetime.now().isoformat()
            }
    
    def batch_revamp_all_sheets(self) -> Dict[str, Any]:
        """Revamp all existing interview sheets in the database.
        
        Returns:
            Batch processing results
        """
        self.logger.info("Starting batch revamp of all interview sheets")
        
        try:
            # Fetch all sheets
            all_sheets = self.database_agent.fetch_all_interview_sheets()
            
            if not all_sheets:
                return {
                    "error": "No sheets found in database",
                    "total_sheets": 0,
                    "successful": 0,
                    "failed": 0
                }
            
            self.logger.info(f"Found {len(all_sheets)} sheets to revamp")
            
            # Process each sheet
            results = []
            successful = 0
            failed = 0
            
            for i, sheet in enumerate(all_sheets):
                try:
                    sheet_id = sheet.get('_id', '')
                    sheet_name = sheet.get('name', 'Unknown')
                    
                    self.logger.info(f"Processing sheet {i+1}/{len(all_sheets)}: {sheet_name}")
                    
                    # Revamp the sheet
                    result = self.revamp_existing_sheet(sheet_id)
                    
                    if "error" not in result:
                        successful += 1
                        result["status"] = "success"
                    else:
                        failed += 1
                        result["status"] = "failed"
                    
                    result["sheet_name"] = sheet_name
                    result["sheet_id"] = sheet_id
                    results.append(result)
                    
                except Exception as e:
                    self.logger.error(f"Error processing sheet {i+1}: {str(e)}")
                    failed += 1
                    results.append({
                        "sheet_name": sheet.get('name', 'Unknown'),
                        "sheet_id": sheet.get('_id', ''),
                        "status": "failed",
                        "error": str(e)
                    })
            
            batch_results = {
                "total_sheets": len(all_sheets),
                "successful": successful,
                "failed": failed,
                "results": results,
                "completion_time": datetime.now().isoformat()
            }
            
            self.logger.info(f"Batch revamp completed. Successful: {successful}, Failed: {failed}")
            
            return batch_results
            
        except Exception as e:
            self.logger.error(f"Error in batch revamp: {str(e)}")
            return {
                "error": str(e),
                "total_sheets": 0,
                "successful": 0,
                "failed": 0,
                "completion_time": datetime.now().isoformat()
            }
    
    def _analyze_difficulty_distribution(self, qa_pairs: List[Dict]) -> Dict[str, int]:
        """Analyze the difficulty distribution of questions."""
        distribution = {"Easy": 0, "Medium": 0, "Hard": 0}
        
        for qa_pair in qa_pairs:
            difficulty = qa_pair.get("difficulty", "Medium")
            if difficulty in distribution:
                distribution[difficulty] += 1
        
        return distribution
    
    def _extract_company_types_from_analysis(self, frequency_analysis: Dict[str, Any]) -> List[str]:
        """Extract company types from frequency analysis data."""
        company_types = []
        companies = frequency_analysis.get("company_breakdown", {})
        
        # Check each company category
        if companies.get("FAANG", {}).get("Frequency", "Low") in ["Very High", "High"]:
            company_types.append("FAANG")
        if companies.get("Indian Unicorns", {}).get("Frequency", "Low") in ["Very High", "High"]:
            company_types.append("Startup")
        if companies.get("Mid-size Startups", {}).get("Frequency", "Low") in ["Very High", "High"]:
            company_types.append("MidSize")
        if companies.get("Service Companies", {}).get("Frequency", "Low") in ["Very High", "High"]:
            company_types.append("MNC")
        
        # Fallback if no company types determined
        if not company_types:
            company_types = ["MidSize", "MNC"]
        
        return company_types
    
    def _save_sheet_to_file(self, sheet_data: Dict[str, Any]) -> str:
        """Save sheet data to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_sheet_{sheet_data['name'].replace(' ', '_').lower()}_{timestamp}.json"
        filepath = os.path.join("output", filename)
        
        # Ensure output directory exists
        os.makedirs("output", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sheet_data, f, indent=2, ensure_ascii=False)
        
        return filepath