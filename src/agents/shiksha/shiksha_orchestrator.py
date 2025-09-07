"""Shiksha Course Orchestrator - Main coordinator for course creation."""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import uuid

from ...core.base_agent import BaseAgent
from .course_planner_agent import CoursePlannerAgent
from .content_creator_agent import ContentCreatorAgent
from .quality_assurance_agent import QualityAssuranceAgent
from .google_research_agent import QualityAssuranceAgent


class ShikshaOrchestrator(BaseAgent):
    """Main orchestrator for creating complete Shiksha courses."""
    
    def __init__(self, **kwargs):
        """Initialize the orchestrator with specialized agents."""
        super().__init__(**kwargs)
        
        # Initialize specialized agents
        self.planner = CoursePlannerAgent(**kwargs)
        self.content_creator = ContentCreatorAgent(**kwargs)
        self.qa_agent = QualityAssuranceAgent(**kwargs)
        
        self.logger.info("Shiksha Orchestrator initialized with specialized agents")
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Orchestrator doesn't need its own templates - it coordinates other agents."""
        return {}
    
    def generate_content(self, *args, **kwargs) -> dict:
        """Orchestrator does not generate content directly."""
        raise NotImplementedError("Orchestrator coordinates other agents, doesn't generate content directly")
    
    def create_complete_course(self, course_name: str, description: str, 
                           difficulty_level: str = "Beginner", 
                           roadmap: str = "Backend") -> Dict[str, Any]:
        """Create a complete Shiksha course using the multi-agent system.
    
        Args:
            course_name: Name of the course
            description: Course description
            difficulty_level: Beginner, Intermediate, or Advanced
            roadmap: Backend, Frontend, Full Stack, etc.
        
        Returns:
            Complete course JSON following Shiksha schema
        """
        self.logger.info(f"Starting complete course creation for: {course_name}")
    
        try:
            # Step 1: Plan the course structure
            self.logger.info("Step 1: Planning course structure...")
            course_plan = self.planner.create_course_structure(
                course_name, description, difficulty_level, roadmap
            )
        
            # Step 2: Generate meta content
            self.logger.info("Step 2: Generating meta content...")
            meta_content = self._generate_meta_content(course_name, description, difficulty_level, roadmap)
        
            # Step 3: Generate chapters with content
            self.logger.info("Step 3: Generating chapter content...")
            chapters = self._generate_chapters_with_content(course_plan, course_name, difficulty_level)
        
            # Step 3a: Enhance each chapter with quizzes, explanations, practice problems, and summary
            self.logger.info("Step 3a: Adding quizzes, practice problems, and summaries...")
            for chapter in chapters:
                # Generate practice problems
                practice_content = self.content_creator.create_practice_problems(
                    chapter_name=chapter["title"],
                    course_name=course_name,
                    difficulty_level=difficulty_level,
                    key_concepts=chapter.get("key_concepts", [])
                )
            
                # Generate chapter summary
                summary_content = self.content_creator.generate_chapter_summary(chapter["content"])
            
                # Generate quiz with explanations
                quiz_content = []
                for question in chapter.get("quiz_questions", []):
                    explanation = self.content_creator.generate_explanation(
                        question=question["question"],
                        answer=question["answer"]
                    )
                    quiz_item = {
                        "question": question["question"],
                        "options": question.get("options", []),
                        "answer": question["answer"],
                        "explanation": explanation
                    }
                    quiz_content.append(quiz_item)

                # Update chapter content
                chapter["content"] = self.content_creator.enhance_content_with_practice_problems(
                    chapter["content"], practice_content
                )
                chapter["content"] += f"\n\n## Quiz\n\n{json.dumps(quiz_content, indent=2)}"
                chapter["content"] += f"\n\n## Summary\n\n{summary_content}"
        
            # Step 4: Create final course structure
            self.logger.info("Step 4: Creating final course structure...")
            course_data = self._create_course_structure(
                course_name, description, difficulty_level, roadmap, meta_content, chapters
            )
        
            # Step 5: Quality assurance review
            self.logger.info("Step 5: Performing quality assurance review...")
            review_results = self.qa_agent.review_course_structure(
                course_data, course_name, difficulty_level
            )
        
            # Step 6: Refine based on feedback if needed
            if review_results.get("overall_score", 0) < 7.0:
                self.logger.info("Step 6: Refining course based on feedback...")
                course_data = self._refine_course(course_data, review_results, course_name, difficulty_level)

            # Step 7: Final validation
            self.logger.info("Step 7: Final validation...")
            validation_results = self.qa_agent.validate_final_course(course_data, course_name)
        
            if not validation_results.get("is_valid", True):
                self.logger.warning(f"Validation issues found: {validation_results.get('issues', [])}")

            self.logger.info(f"Course creation completed successfully for: {course_name}")
            return course_data
        
        except Exception as e:
            self.logger.error(f"Error creating course: {str(e)}")
            raise


    
    def _generate_meta_content(self, course_name: str, description: str, 
                             difficulty_level: str, roadmap: str) -> str:
        """Generate meta content (introduction) for the course."""
        meta_prompt = f"""
        Create an engaging introduction for the "{course_name}" course.
        
        Course Description: {description}
        Difficulty Level: {difficulty_level}
        Roadmap: {roadmap}
        
        The introduction should:
        1. Explain what learners will gain from this course
        2. Highlight the real-world applications and career benefits
        3. Set expectations for the learning journey
        4. Motivate learners to start the course
        5. Explain the course structure and approach
        
        Write in an engaging, conversational tone that inspires learners.
        Focus on practical benefits and career impact.
        """
        
        result = self._generate_with_prompt(meta_prompt)
        return result
    
    def _generate_chapters_with_content(self, course_plan: Dict[str, Any], course_name: str, 
                                      difficulty_level: str) -> List[Dict[str, Any]]:
        """Generate all chapters with comprehensive content."""
        chapters = []
        course_chapters = course_plan.get("chapters", [])
        total_chapters = len(course_chapters)
        
        for i, chapter_info in enumerate(course_chapters, 1):
            chapter_name = chapter_info.get("name", f"Chapter {i}")
            self.logger.info(f"Generating chapter {i}/{total_chapters}: {chapter_name}")
            
            # Get chapter breakdown for better content generation
            chapter_breakdown = self.planner.create_chapter_breakdown(
                chapter_name, course_name, i, total_chapters, difficulty_level
            )
            
            # Generate base chapter content
            chapter_content = self.content_creator.create_chapter_content(
                chapter_name=chapter_name,
                course_name=course_name,
                chapter_number=i,
                total_chapters=total_chapters,
                difficulty_level=difficulty_level,
                learning_objectives=chapter_breakdown.get("learning_objectives", []),
                key_concepts=chapter_breakdown.get("key_concepts", [])
            )
            
            # Enhance with curated videos
            videos_content = self.content_creator.curate_videos(
                chapter_name, course_name, difficulty_level, 
                chapter_breakdown.get("key_concepts", [])
            )
            chapter_content = self.content_creator.enhance_content_with_videos(
                chapter_content, videos_content
            )
            
            # Enhance with social media templates
            learning_points = chapter_breakdown.get("learning_objectives", [])
            social_media_content = self.content_creator.create_social_media_templates(
                chapter_name, course_name, learning_points, difficulty_level
            )
            chapter_content = self.content_creator.enhance_content_with_social_media(
                chapter_content, social_media_content
            )
            
            # Enhance with practice problems
            practice_content = self.content_creator.create_practice_problems(
                chapter_name, course_name, difficulty_level,
                chapter_breakdown.get("key_concepts", [])
            )
            chapter_content = self.content_creator.enhance_content_with_practice_problems(
                chapter_content, practice_content
            )
            
            # Review and refine chapter content
            chapter_review = self.qa_agent.review_chapter_content(
                chapter_content, chapter_name, course_name, difficulty_level
            )
            
            if chapter_review.get("feedback"):
                # Refine based on feedback
                feedback_text = "\n".join(chapter_review.get("feedback", []))
                chapter_content = self.qa_agent.refine_content(
                    chapter_content, feedback_text, chapter_name, difficulty_level
                )
            
            chapters.append({
                "name": chapter_name,
                "content": chapter_content,
                "_id": self._generate_chapter_id(),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            })
        
        return chapters
    
    def _create_course_structure(self, course_name: str, description: str, 
                               difficulty_level: str, roadmap: str, 
                               meta_content: str, chapters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create the final course structure following Shiksha schema."""
        
        # Generate slug from course name
        slug = self._generate_slug(course_name)
        
        # Generate cover image URL
        cover_image_url = self._generate_cover_image_url(course_name)
        
        # Set live date (1 month from now)
        live_date = (datetime.now() + timedelta(days=30)).isoformat()
        
        return {
            "status": True,
            "data": {
                "_id": self._generate_course_id(),
                "name": course_name,
                "slug": slug,
                "coverImageURL": cover_image_url,
                "description": description,
                "liveOn": live_date,
                "roadmap": roadmap,
                "difficultyLevel": difficulty_level,
                "chapters": chapters,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "__v": 0,
                "meta": meta_content,
                "isPremium": True,
                "price": 1,
                "features": [],
                "isEnrolled": False
            }
        }
    
    def _refine_course(self, course_data: Dict[str, Any], review_results: Dict[str, Any],
                      course_name: str, difficulty_level: str) -> Dict[str, Any]:
        """Refine the course based on quality assurance feedback."""
        
        recommendations = review_results.get("recommendations", [])
        if not recommendations:
            return course_data
        
        # Apply recommendations to improve the course
        self.logger.info(f"Applying {len(recommendations)} recommendations to improve course quality")
        
        # For now, return the original data - in a full implementation,
        # you would apply specific refinements based on the recommendations
        return course_data
    
    def _generate_slug(self, course_name: str) -> str:
        """Generate URL-friendly slug from course name."""
        import re
        slug = re.sub(r'[^\w\s-]', '', course_name.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug.strip('-')
    
    def _generate_cover_image_url(self, course_name: str) -> str:
        """Generate cover image URL."""
        slug = self._generate_slug(course_name)
        return f"https://ik.imagekit.io/tbe/webapp/shiksha-{slug}-cover.svg"
    
    def _generate_course_id(self) -> str:
        """Generate a unique course ID."""
        return str(uuid.uuid4()).replace("-", "")[:24]
    
    def _generate_chapter_id(self) -> str:
        """Generate a unique chapter ID."""
        return str(uuid.uuid4()).replace("-", "")[:24]
    
    def save_course(self, course_data: Dict[str, Any], filename: str = None) -> str:
        """Save the generated course to a JSON file.
        
        Args:
            course_data: The complete course data
            filename: Optional filename (without extension)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            course_name = course_data.get("data", {}).get("name", "course")
            filename = f"shiksha_course_{self._generate_slug(course_name)}"
        
        # Ensure output directory exists
        output_dir = getattr(self, 'config', None)
        if output_dir and hasattr(output_dir, 'output_dir'):
            output_path = output_dir.output_dir
        else:
            output_path = "./output"
        
        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, f"{filename}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Course saved to {filepath}")
        return filepath 