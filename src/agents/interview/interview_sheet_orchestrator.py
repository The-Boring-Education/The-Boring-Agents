"""Interview Sheet Orchestrator - Main coordinator for revamping and creating interview sheets."""

from typing import Dict, Any, List, Optional
import json
import os
import requests
from datetime import datetime

from ...core.base_agent import BaseAgent
from .interview_research_agent import InterviewResearchAgent
from .question_generator_agent import QuestionGeneratorAgent
from .answer_enhancement_agent import AnswerEnhancementAgent
from .quality_review_agent import QualityReviewAgent
from .frequency_analysis_agent import FrequencyAnalysisAgent
from .database_integration_agent import DatabaseIntegrationAgent


class InterviewSheetOrchestrator(BaseAgent):
    """Main orchestrator for creating world-class interview sheets with Indian context and humor."""
    
    def __init__(self, **kwargs):
        """Initialize the orchestrator with all specialized agents."""
        super().__init__(**kwargs)
        
        # Initialize all specialized agents
        self.research_agent = InterviewResearchAgent(**kwargs)
        self.question_generator = QuestionGeneratorAgent(**kwargs)
        self.answer_enhancer = AnswerEnhancementAgent(**kwargs)
        self.quality_reviewer = QualityReviewAgent(**kwargs)
        self.frequency_analyzer = FrequencyAnalysisAgent(**kwargs)
        self.db_agent = DatabaseIntegrationAgent(**kwargs)
        
        self.logger.info("Interview Sheet Orchestrator initialized with all specialized agents")
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Orchestrator doesn't need its own templates - it coordinates other agents."""
        return {}
    
    def generate_content(self, *args, **kwargs) -> dict:
        """Orchestrator does not generate content directly."""
        raise NotImplementedError("Orchestrator coordinates other agents")
    
    def revamp_existing_sheet(self, sheet_id: str) -> Dict[str, Any]:
        """Revamp an existing interview sheet with world-class quality.
        
        Args:
            sheet_id: ID of the sheet to revamp
            
        Returns:
            Revamping results with statistics
        """
        self.logger.info(f"🚀 Starting world-class revamping for sheet: {sheet_id}")
        
        try:
            # Step 1: Fetch existing sheet and questions
            self.logger.info("📊 Step 1: Fetching existing sheet data...")
            sheet_data = self.db_agent.fetch_interview_sheet(sheet_id)
            questions_data = self.db_agent.fetch_sheet_questions(sheet_id)
            
            if not sheet_data or not questions_data:
                raise ValueError(f"Could not fetch data for sheet {sheet_id}")
            
            sheet_name = sheet_data.get('name', 'Unknown Sheet')
            self.logger.info(f"📋 Found sheet: {sheet_name} with {len(questions_data)} questions")
            
            # Step 2: Research the topic for better context
            self.logger.info("🔍 Step 2: Researching topic for enhanced context...")
            research_insights = self.research_agent.analyze_interview_topic(
                sheet_name, sheet_data.get('description', ''), questions_data
            )
            
            # Step 3: Analyze and potentially add new questions
            self.logger.info("💡 Step 3: Analyzing gaps and generating additional questions...")
            new_questions = self.question_generator.identify_missing_questions(
                sheet_name, questions_data, research_insights
            )
            
            revamped_questions = []
            update_stats = {"enhanced": 0, "added": 0, "failed": 0}
            
            # Step 4: Revamp existing questions
            self.logger.info("✨ Step 4: Revamping existing questions with world-class quality...")
            for i, question_data in enumerate(questions_data, 1):
                self.logger.info(f"🎯 Revamping question {i}/{len(questions_data)}")
                
                try:
                    # Enhance the answer with Indian context, humor, and expert insights
                    enhanced_answer = self.answer_enhancer.create_world_class_answer(
                        question_data.get('question', ''),
                        question_data.get('answer', ''),
                        sheet_name,
                        research_insights
                    )
                    
                    # Analyze frequency and company context
                    frequency_analysis = self.frequency_analyzer.analyze_question_frequency(
                        question_data.get('question', ''), sheet_name
                    )
                    
                    # Review quality
                    quality_review = self.quality_reviewer.review_qa_pair(
                        question_data.get('question', ''),
                        enhanced_answer,
                        sheet_name
                    )
                    
                    # Apply improvements if needed
                    if quality_review.get('score', 0) < 8.0:
                        enhanced_answer = self.answer_enhancer.apply_quality_improvements(
                            enhanced_answer, quality_review.get('suggestions', [])
                        )
                    
                    # Update in database
                    success = self.db_agent.update_question_answer(
                        sheet_id, 
                        question_data.get('_id'),
                        enhanced_answer,
                        frequency_analysis
                    )
                    
                    if success:
                        update_stats["enhanced"] += 1
                        revamped_questions.append({
                            "question": question_data.get('question', ''),
                            "enhanced_answer": enhanced_answer,
                            "frequency_analysis": frequency_analysis,
                            "quality_score": quality_review.get('score', 0)
                        })
                    else:
                        update_stats["failed"] += 1
                        self.logger.warning(f"Failed to update question {i}")
                
                except Exception as e:
                    self.logger.error(f"Error revamping question {i}: {str(e)}")
                    update_stats["failed"] += 1
            
            # Step 5: Add new questions if any were identified
            if new_questions:
                self.logger.info(f"➕ Step 5: Adding {len(new_questions)} new questions...")
                for new_q in new_questions:
                    try:
                        enhanced_answer = self.answer_enhancer.create_world_class_answer(
                            new_q['question'], '', sheet_name, research_insights
                        )
                        
                        frequency_analysis = self.frequency_analyzer.analyze_question_frequency(
                            new_q['question'], sheet_name
                        )
                        
                        # Add to database (you'll need to implement this API)
                        success = self.db_agent.add_question_to_sheet(
                            sheet_id, new_q['question'], enhanced_answer, frequency_analysis
                        )
                        
                        if success:
                            update_stats["added"] += 1
                    except Exception as e:
                        self.logger.error(f"Error adding new question: {str(e)}")
                        update_stats["failed"] += 1
            
            # Step 6: Final quality review of the entire sheet
            self.logger.info("🔍 Step 6: Final quality review...")
            final_review = self.quality_reviewer.review_complete_sheet(
                sheet_name, revamped_questions, research_insights
            )
            
            self.logger.info(f"🎉 Revamping completed! Enhanced: {update_stats['enhanced']}, Added: {update_stats['added']}, Failed: {update_stats['failed']}")
            
            return {
                "sheet_id": sheet_id,
                "sheet_name": sheet_name,
                "statistics": update_stats,
                "revamped_questions": revamped_questions,
                "research_insights": research_insights,
                "final_review": final_review,
                "completion_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error revamping sheet: {str(e)}")
            raise
    
    def create_new_sheet(self, sheet_name: str, description: str, 
                        target_questions: int = 50) -> Dict[str, Any]:
        """Create a brand new interview sheet from scratch.
        
        Args:
            sheet_name: Name of the new sheet
            description: Description of the sheet
            target_questions: Number of questions to generate
            
        Returns:
            Complete new sheet data
        """
        self.logger.info(f"🚀 Creating new world-class interview sheet: {sheet_name}")
        
        try:
            # Step 1: Research the topic comprehensively
            self.logger.info("🔍 Step 1: Comprehensive topic research...")
            research_insights = self.research_agent.comprehensive_topic_research(
                sheet_name, description
            )
            
            # Step 2: Generate comprehensive question list
            self.logger.info(f"💡 Step 2: Generating {target_questions} world-class questions...")
            questions = self.question_generator.generate_comprehensive_questions(
                sheet_name, description, research_insights, target_questions
            )
            
            # Step 3: Create world-class answers for each question
            self.logger.info("✨ Step 3: Creating world-class answers...")
            complete_qa_pairs = []
            
            for i, question in enumerate(questions, 1):
                self.logger.info(f"🎯 Creating answer {i}/{len(questions)}")
                
                try:
                    # Create comprehensive answer
                    answer = self.answer_enhancer.create_world_class_answer(
                        question['question'], '', sheet_name, research_insights
                    )
                    
                    # Analyze frequency and context
                    frequency_analysis = self.frequency_analyzer.analyze_question_frequency(
                        question['question'], sheet_name
                    )
                    
                    # Quality review
                    quality_review = self.quality_reviewer.review_qa_pair(
                        question['question'], answer, sheet_name
                    )
                    
                    # Apply improvements if needed
                    if quality_review.get('score', 0) < 8.0:
                        answer = self.answer_enhancer.apply_quality_improvements(
                            answer, quality_review.get('suggestions', [])
                        )
                    
                    complete_qa_pairs.append({
                        "question": question['question'],
                        "answer": answer,
                        "difficulty": question.get('difficulty', 'Medium'),
                        "category": question.get('category', 'General'),
                        "frequency_analysis": frequency_analysis,
                        "quality_score": quality_review.get('score', 0)
                    })
                    
                except Exception as e:
                    self.logger.error(f"Error creating answer for question {i}: {str(e)}")
            
            # Step 4: Final quality review and organization
            self.logger.info("🔍 Step 4: Final organization and quality review...")
            final_review = self.quality_reviewer.review_complete_sheet(
                sheet_name, complete_qa_pairs, research_insights
            )
            
            # Step 5: Create final sheet structure
            sheet_data = {
                "name": sheet_name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "total_questions": len(complete_qa_pairs),
                "estimated_prep_time": f"{len(complete_qa_pairs) * 2} hours",
                "difficulty_distribution": self._analyze_difficulty_distribution(complete_qa_pairs),
                "research_insights": research_insights,
                "final_review": final_review,
                "questions": complete_qa_pairs,
                "metadata": {
                    "version": "2.0",
                    "created_by": "Interview Sheet AI Orchestrator",
                    "quality_assured": True,
                    "indian_context": True,
                    "humor_integrated": True,
                    "expert_reviewed": True
                }
            }
            
            # Step 6: Save to file
            filepath = self._save_sheet_to_file(sheet_data)
            
            self.logger.info(f"🎉 New sheet created successfully: {filepath}")
            
            return {
                "sheet_data": sheet_data,
                "filepath": filepath,
                "statistics": {
                    "total_questions": len(complete_qa_pairs),
                    "average_quality_score": sum(qa.get('quality_score', 0) for qa in complete_qa_pairs) / len(complete_qa_pairs),
                    "completion_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error creating new sheet: {str(e)}")
            raise
    
    def batch_revamp_all_sheets(self) -> Dict[str, Any]:
        """Revamp all existing interview sheets in the database.
        
        Returns:
            Batch processing results
        """
        self.logger.info("🚀 Starting batch revamping of all interview sheets...")
        
        try:
            # Fetch all sheets
            all_sheets = self.db_agent.fetch_all_interview_sheets()
            
            if not all_sheets:
                self.logger.warning("No sheets found in database")
                return {"message": "No sheets found"}
            
            batch_results = []
            total_sheets = len(all_sheets)
            
            for i, sheet in enumerate(all_sheets, 1):
                sheet_id = sheet.get('_id')
                sheet_name = sheet.get('name', 'Unknown')
                
                self.logger.info(f"📋 Processing sheet {i}/{total_sheets}: {sheet_name}")
                
                try:
                    result = self.revamp_existing_sheet(sheet_id)
                    batch_results.append({
                        "sheet_id": sheet_id,
                        "sheet_name": sheet_name,
                        "status": "success",
                        "result": result
                    })
                except Exception as e:
                    self.logger.error(f"Failed to revamp sheet {sheet_name}: {str(e)}")
                    batch_results.append({
                        "sheet_id": sheet_id,
                        "sheet_name": sheet_name,
                        "status": "failed",
                        "error": str(e)
                    })
            
            return {
                "total_sheets": total_sheets,
                "successful": len([r for r in batch_results if r["status"] == "success"]),
                "failed": len([r for r in batch_results if r["status"] == "failed"]),
                "results": batch_results,
                "completion_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error in batch revamping: {str(e)}")
            raise
    
    def _analyze_difficulty_distribution(self, qa_pairs: List[Dict]) -> Dict[str, int]:
        """Analyze the difficulty distribution of questions."""
        distribution = {"Easy": 0, "Medium": 0, "Hard": 0}
        for qa in qa_pairs:
            difficulty = qa.get('difficulty', 'Medium')
            distribution[difficulty] = distribution.get(difficulty, 0) + 1
        return distribution
    
    def _save_sheet_to_file(self, sheet_data: Dict[str, Any]) -> str:
        """Save sheet data to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sheet_name_clean = sheet_data['name'].replace(' ', '_').replace('/', '_')
        filename = f"interview_sheet_{sheet_name_clean}_{timestamp}.json"
        
        output_dir = "./output"
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(sheet_data, f, indent=2, ensure_ascii=False)
        
        return filepath