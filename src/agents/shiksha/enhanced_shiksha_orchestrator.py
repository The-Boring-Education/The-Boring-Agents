"""Enhanced Shiksha Course Orchestrator with Indian context and world-class instruction."""

from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime, timedelta
import uuid
import logging

from ...core.base_agent import BaseAgent
from .research_agent import ResearchAgent
from .instructor_agent import InstructorAgent
from .exercise_creator_agent import ExerciseCreatorAgent
from .course_planner_agent import CoursePlannerAgent
from .content_creator_agent import ContentCreatorAgent
from .quality_assurance_agent import QualityAssuranceAgent
from ..project.project_orchestrator_agent import ProjectOrchestratorAgent


class EnhancedShikshaOrchestrator(BaseAgent):
    """Enhanced orchestrator for creating world-class Shiksha courses with Indian context."""

    def __init__(self, **kwargs):
        """Initialize the enhanced orchestrator with all specialized agents."""
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize all specialized agents
        self.research_agent = ResearchAgent(**kwargs)
        self.instructor_agent = InstructorAgent(**kwargs)
        self.exercise_creator = ExerciseCreatorAgent(**kwargs)
        self.planner = CoursePlannerAgent(**kwargs)
        self.content_creator = ContentCreatorAgent(**kwargs)
        self.project_orchestrator = ProjectOrchestratorAgent(**kwargs)
        self.qa_agent = QualityAssuranceAgent(**kwargs)

        self.logger.info("Enhanced Shiksha Orchestrator initialized with all specialized agents")

    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Orchestrator doesn't need its own templates - it coordinates other agents."""
        return {}

    def generate_content(self, *args, **kwargs) -> dict:
        """Orchestrator does not generate content directly."""
        raise NotImplementedError("Enhanced orchestrator coordinates other agents")

    def create_world_class_course(self, course_name: str, description: str,
                                  difficulty_level: str = "Beginner",
                                  roadmap: str = "Backend",
                                  api_base_url: str = None) -> Dict[str, Any]:
        """Create a world-class Shiksha course with Indian context and humor.

        Args:
            course_name: Name of the course
            description: Course description
            difficulty_level: Beginner, Intermediate, or Advanced
            roadmap: Backend, Frontend, Full Stack, etc.
            api_base_url: API base URL for research

        Returns:
            Complete course JSON following Shiksha schema
        """
        self.logger.info(f"🚀 Starting world-class course creation for: {course_name}")

        try:
            # Step 1: Research Phase - Understand the landscape
            self.logger.info("📊 Step 1: Conducting comprehensive research...")
            research_report = self.research_agent.comprehensive_research(
                course_name, roadmap.lower(), difficulty_level, api_base_url or "https://tbe-dev-git-development-tbe.vercel.app/api/v1/shiksha"
            )

            # Step 2: Strategic Planning - Design unique course structure
            self.logger.info("🎯 Step 2: Strategic course planning...")
            course_plan = self.planner.create_course_structure(
                course_name, description, difficulty_level, roadmap
            )

            # Enhance course plan with research insights
            enhanced_plan = self._enhance_plan_with_research(course_plan, research_report)

            # Step 3: Generate engaging meta content
            self.logger.info("✨ Step 3: Creating engaging meta content...")
            meta_content = self._generate_enhanced_meta_content(
                course_name, description, difficulty_level, roadmap, research_report
            )

            # Step 4: Create world-class chapters with Indian context
            self.logger.info("📚 Step 4: Creating world-class chapter content...")
            chapters = self._create_engaging_chapters(enhanced_plan, course_name, difficulty_level)

            # Step 5: Create final course structure
            self.logger.info("🏗️ Step 5: Assembling final course structure...")
            course_data = self._create_course_structure(
                course_name, description, difficulty_level, roadmap, meta_content, chapters
            )

            # Step 5.5: Generate mini-projects leveraging project orchestrator
            self.logger.info("🛠️ Step 5.5: Generating mini-projects for world-class course...")
            mini_projects = []
            try:
                project_idea = f"{course_name} - Capstone Project"
                project_description = f"A capstone project to apply concepts from the {course_name} course with Indian context."
                proj = self.project_orchestrator.create_complete_project(project_idea, project_description)
                if isinstance(proj, dict) and proj.get('status'):
                    mini_projects.append(proj.get('data', proj))
                else:
                    mini_projects.append(proj)
            except Exception as e:
                self.logger.warning(f"Failed to generate mini-projects: {e}")

            try:
                course_data['data']['mini_projects'] = mini_projects
            except Exception:
                course_data['data'].update({'mini_projects': mini_projects})

            # Step 6: Enhanced quality assurance
            self.logger.info("🔍 Step 6: Enhanced quality assurance review...")
            review_results = self.qa_agent.review_course_structure(
                course_data, course_name, difficulty_level
            )

            # Step 7: Refinement based on feedback
            if review_results.get("overall_score", 0) < 8.0:  # Higher bar for world-class
                self.logger.info("🔧 Step 7: Refining course for world-class quality...")
                course_data = self._refine_course_for_excellence(
                    course_data, review_results, research_report
                )

            # Step 8: Final validation and polish
            self.logger.info("✅ Step 8: Final validation and polish...")
            validation_results = self.qa_agent.validate_final_course(course_data, course_name)

            if not validation_results.get("is_valid", True):
                self.logger.warning(f"Validation issues found: {validation_results.get('issues', [])}")

            # Add research metadata to course
            course_data["research_insights"] = {
                "research_date": research_report.get("research_date"),
                "key_recommendations": research_report.get("key_recommendations", [])[:5],
                "differentiation_strategy": research_report.get("competitor_analysis", {}).get("differentiation_opportunities", [])[:3]
            }

            self.logger.info(f"🎉 World-class course creation completed for: {course_name}")
            return course_data

        except Exception as e:
            self.logger.error(f"❌ Error creating world-class course: {str(e)}")
            raise

    def _enhance_plan_with_research(self, course_plan: Dict[str, Any],
                                    research_report: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance course plan with research insights."""
        enhanced_plan = course_plan.copy()

        # Add research-based recommendations to chapter planning
        recommendations = research_report.get("key_recommendations", [])
        market_trends = research_report.get("market_trends", {})

        # Enhance chapter descriptions with market insights
        chapters = enhanced_plan.get("chapters", [])
        for chapter in chapters:
            chapter["market_relevance"] = self._extract_chapter_relevance(
                chapter.get("name", ""), recommendations
            )
            chapter["indian_context_focus"] = True

        enhanced_plan["research_enhanced"] = True
        enhanced_plan["market_insights"] = market_trends.get("key_insights", [])[:3]

        return enhanced_plan

    def _generate_enhanced_meta_content(self, course_name: str, description: str,
                                        difficulty_level: str, roadmap: str,
                                        research_report: Dict[str, Any]) -> str:
        """Generate enhanced meta content with research insights and Indian context."""

        # Extract key insights from research
        market_insights = research_report.get("market_trends", {}).get("key_insights", [])
        opportunities = research_report.get("competitor_analysis", {}).get("differentiation_opportunities", [])

        # Use instructor agent to create engaging introduction
        meta_prompt = f"""
        Create an incredibly engaging course introduction for "{course_name}" that will make Indian students excited to learn.

        Course Description: {description}
        Difficulty Level: {difficulty_level}
        Roadmap: {roadmap}

        Market Insights: {market_insights[:3] if market_insights else ['Growing demand in Indian tech industry']}
        Unique Opportunities: {opportunities[:2] if opportunities else ['Stand out from existing courses']}

        Your introduction should:

        1. **Hook with Indian Success Stories**
           - Start with inspiring stories of Indian developers/entrepreneurs
           - Reference recent success stories from Indian tech ecosystem
           - Show the real career impact in Indian context

        2. **Address Indian Learner Concerns**
           - Acknowledge common challenges faced by Indian students
           - Address concerns about job market and career prospects
           - Build confidence and motivation

        3. **Set Ambitious but Achievable Goals**
           - Clear career outcomes and salary expectations in India
           - Portfolio projects that will impress Indian recruiters
           - Skills that are in high demand in Indian companies

        4. **Cultural Connection**
           - Use examples from popular Indian apps and companies
           - Reference Indian festivals, cities, or cultural context
           - Make them feel this course is made specifically for them

        5. **Community and Journey**
           - Emphasize the learning community and support
           - Show this is a journey, not just a course
           - Encourage learning in public and sharing progress

        Write like the most inspiring tech mentor in India. Be warm, encouraging, and incredibly motivating!
        """

        meta_content = self._generate_with_prompt(meta_prompt)
        return meta_content

    def _create_engaging_chapters(self, enhanced_plan: Dict[str, Any], course_name: str,
                                  difficulty_level: str) -> List[Dict[str, Any]]:
        """Create engaging chapters with world-class instruction and Indian context."""
        chapters = []
        course_chapters = enhanced_plan.get("chapters", [])
        total_chapters = len(course_chapters)

        for i, chapter_info in enumerate(course_chapters, 1):
            chapter_name = chapter_info.get("name", f"Chapter {i}")
            self.logger.info(f"🎨 Creating engaging chapter {i}/{total_chapters}: {chapter_name}")

            # Get detailed chapter breakdown
            chapter_breakdown = self.planner.create_chapter_breakdown(
                chapter_name, course_name, i, total_chapters, difficulty_level
            )

            # Create instructor-led content with Indian context
            instructor_content = self.instructor_agent.create_comprehensive_content(
                chapter_name, course_name, difficulty_level,
                chapter_breakdown.get("key_concepts", []),
                [chapter_name]  # Main topics
            )

            # Create comprehensive exercises
            exercises = self.exercise_creator.create_comprehensive_exercise_suite(
                chapter_name, chapter_name, difficulty_level,
                chapter_breakdown.get("learning_objectives", [])
            )

            # Combine all content into engaging chapter
            chapter_content = self._combine_chapter_content(
                chapter_name, instructor_content, exercises, chapter_breakdown
            )

            # Enhance with curated videos (keeping existing functionality)
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

            # --- Generate assignment for the chapter ---
            try:
                assignment_text = self.exercise_creator.design_practical_assignment(
                    chapter_name, chapter_breakdown.get("learning_objectives", []),
                    assessment_criteria="Auto-generated assignment criteria",
                    collaboration_level="Individual"
                )
            except Exception as e:
                self.logger.warning(f"Failed to generate assignment for {chapter_name}: {e}")
                assignment_text = ""

            chapters.append({
                "name": chapter_name,
                "content": chapter_content,
                "assignments": [
                    {
                        "id": self._generate_chapter_id(),
                        "title": f"Assignment: {chapter_name}",
                        "description": assignment_text,
                        "type": "practical",
                        "expected_time": "1-3 hours",
                        "grading": {
                            "rubric": "Manual review",
                            "passing_criteria": "Completes core requirements"
                        }
                    }
                ],
                "_id": self._generate_chapter_id(),
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "enhanced_features": {
                    "indian_context": True,
                    "humor_integrated": True,
                    "hands_on_exercises": True,
                    "career_focused": True
                }
            })

        return chapters

    def _combine_chapter_content(self, chapter_name: str, instructor_content: Dict[str, str],
                                 exercises: Dict[str, str], chapter_breakdown: Dict[str, Any]) -> str:
        """Combine instructor content and exercises into engaging chapter."""

        # Start with engaging introduction
        content = f"# {chapter_name}\n\n"
        content += instructor_content.get("introduction", "") + "\n\n"

        # Add concept explanations with humor
        content += "## Understanding the Concepts\n\n"
        concept_explanations = instructor_content.get("concept_explanations", {})
        if isinstance(concept_explanations, dict):
            for topic, explanation in concept_explanations.items():
                content += f"### {topic}\n\n{explanation}\n\n"
        else:
            content += str(concept_explanations) + "\n\n"

        # Add Indian examples
        content += "## Real-world Examples (Indian Context)\n\n"
        content += instructor_content.get("indian_examples", "") + "\n\n"

        # Add humor section
        content += "## Fun Learning Corner 😄\n\n"
        content += instructor_content.get("humor_content", "") + "\n\n"

        # Add hands-on exercises
        content += "## Hands-on Practice\n\n"
        content += exercises.get("hands_on_exercises", "") + "\n\n"

        # Add coding project
        content += "## Build Something Amazing\n\n"
        content += exercises.get("coding_project", "") + "\n\n"

        # Add interview preparation
        content += "## Interview Readiness\n\n"
        content += exercises.get("interview_problems", "") + "\n\n"

        # Add motivational content
        content += "## You're Doing Great! 🎉\n\n"
        content += instructor_content.get("motivation", "") + "\n\n"

        return content

    def _refine_course_for_excellence(self, course_data: Dict[str, Any],
                                     review_results: Dict[str, Any],
                                     research_report: Dict[str, Any]) -> Dict[str, Any]:
        """Refine course based on review feedback for world-class quality."""

        recommendations = review_results.get("recommendations", [])
        if not recommendations:
            return course_data

        self.logger.info(f"Applying {len(recommendations)} refinements for excellence")

        # Apply specific refinements based on feedback
        refined_data = course_data.copy()

        # Enhance course description if needed
        if any("description" in rec.lower() for rec in recommendations):
            enhanced_description = self._enhance_course_description(
                course_data, research_report
            )
            refined_data["data"]["description"] = enhanced_description

        # Enhance chapter content if needed
        if any("content" in rec.lower() or "chapter" in rec.lower() for rec in recommendations):
            refined_data = self._enhance_chapter_quality(refined_data, recommendations)

        return refined_data

    def _enhance_course_description(self, course_data: Dict[str, Any],
                                    research_report: Dict[str, Any]) -> str:
        """Enhance course description with research insights."""
        current_desc = course_data.get("data", {}).get("description", "")
        course_name = course_data.get("data", {}).get("name", "")

        enhancement_prompt = f"""
        Enhance this course description to make it more compelling for Indian students:

        Current Description: {current_desc}
        Course Name: {course_name}

        Market Insights: {research_report.get("key_recommendations", [])[:3]}

        Make it:
        - More specific about career outcomes in India
        - Include salary expectations and job opportunities
        - Reference popular Indian companies and startups
        - Add excitement and urgency
        - Keep it concise but powerful (2-3 sentences max)
        """

        enhanced_description = self._generate_with_prompt(enhancement_prompt)
        return enhanced_description.strip()

    def _enhance_chapter_quality(self, course_data: Dict[str, Any],
                                recommendations: List[str]) -> Dict[str, Any]:
        """Enhance chapter quality based on recommendations."""
        # For now, return as is - in full implementation, would apply specific enhancements
        return course_data

    def _extract_chapter_relevance(self, chapter_name: str, recommendations: List[str]) -> str:
        """Extract market relevance for a chapter based on recommendations."""
        for rec in recommendations:
            if any(keyword in rec.lower() for keyword in chapter_name.lower().split()):
                return rec
        return "Highly relevant to current Indian tech market demands"

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
                "features": [
                    "Indian Context Examples",
                    "Humor and Analogies",
                    "Hands-on Exercises",
                    "Career-focused Content",
                    "Interview Preparation"
                ],
                "isEnrolled": False,
                "enhanced_quality": {
                    "world_class_instruction": True,
                    "indian_context": True,
                    "research_based": True,
                    "career_focused": True
                }
            }
        }

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

    def save_course(self, course_data: Dict[str, Any], filename: Optional[str] = None) -> str:
        """Save the generated course to a JSON file."""
        if filename is None:
            course_name = course_data.get("data", {}).get("name", "course")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_shiksha_course_{self._generate_slug(course_name)}_{timestamp}"

        # Ensure output directory exists
        output_path = "./output"
        os.makedirs(output_path, exist_ok=True)
        filepath = os.path.join(output_path, f"{filename}.json")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(course_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"World-class course saved to {filepath}")
        return filepath
