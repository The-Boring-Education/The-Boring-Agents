import logging
import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any

# Import existing agents (names consistent with your repo)
from .course_planner_agent import CoursePlannerAgent
from .content_creator_agent import ContentCreatorAgent
from .quality_assurance_agent import QualityAssuranceAgent
from .exercise_creator_agent import ExerciseCreatorAgent
from ..project.project_orchestrator_agent import ProjectOrchestratorAgent


class ShikshaOrchestrator:
    """
    Main orchestrator for Shiksha course creation.

    Pipeline:
      1. Plan course (fallback-safe if planner agent has missing methods)
      2. Generate chapters + content + assignments
      3. Add mini-projects at course level
      4. QA review
      5. Save / push support
    """

    def __init__(self, **kwargs):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.planner = CoursePlannerAgent(**kwargs)
        self.content_creator = ContentCreatorAgent(**kwargs)
        self.exercise_creator = ExerciseCreatorAgent(**kwargs)
        self.project_orchestrator = ProjectOrchestratorAgent(**kwargs)
        self.qa_agent = QualityAssuranceAgent(**kwargs)

        self.logger.info("✅ Shiksha Orchestrator initialized with specialized agents")

    # ---------- Helpers ----------

    def _generate_chapter_id(self) -> str:
        return f"chap_{random.randint(1000, 9999)}"

    def _create_course_structure(
        self,
        course_name: str,
        description: str,
        difficulty_level: str,
        roadmap: str,
        meta_content: Dict[str, Any],
        chapters: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Wrap final course into standard JSON structure."""
        return {
            "status": True,
            "message": "Course created successfully",
            "data": {
                "name": course_name,
                "description": description,
                "difficulty": difficulty_level,
                "roadmap": roadmap,
                "meta_content": meta_content,
                "chapters": chapters,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat()
            }
        }

    # ---------- Chapter Generation ----------

    def _generate_chapters(
        self, course_name: str, description: str, difficulty_level: str, roadmap: str
    ) -> List[Dict[str, Any]]:
        """Generate chapters with content and assignments."""

        # ---- Call planner safely ----
        if hasattr(self.planner, "plan_course"):
            plan = self.planner.plan_course(course_name, description, difficulty_level, roadmap)
        elif hasattr(self.planner, "plan_course_metadata"):
            plan = self.planner.plan_course_metadata(course_name, description, difficulty_level, roadmap)
        else:
            self.logger.warning("⚠️ No plan_course or plan_course_metadata in CoursePlannerAgent. Using fallback empty plan.")
            plan = {"chapters": []}

        chapters = []

        for chapter_breakdown in plan.get("chapters", []):
            chapter_name = chapter_breakdown.get("name", "Untitled Chapter")

            # ---- Content ----
            try:
                chapter_content = self.content_creator.create_chapter_content(
                    chapter_name, chapter_breakdown.get("topics", [])
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to generate content for {chapter_name}: {e}")
                chapter_content = "Content unavailable."

            # ---- Assignment ----
            try:
                assignment_text = self.exercise_creator.design_practical_assignment(
                    chapter_name,
                    chapter_breakdown.get("learning_objectives", []),
                    assessment_criteria="Auto-generated assignment criteria",
                    collaboration_level="Individual"
                )
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to generate assignment for {chapter_name}: {e}")
                assignment_text = "Assignment unavailable."

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
                "updatedAt": datetime.now().isoformat()
            })

        return chapters

    # ---------- Main Course Creation ----------

    def create_complete_course(
        self,
        course_name: str,
        description: str,
        difficulty_level: str,
        roadmap: str
    ) -> Dict[str, Any]:
        """Full pipeline: plan → generate content → add assignments/projects → QA."""

        # ---- Step 1: Metadata planning ----
        self.logger.info("Step 1: Planning course metadata...")

        if hasattr(self.planner, "plan_course_metadata"):
            meta_content = self.planner.plan_course_metadata(course_name, description, difficulty_level, roadmap)
        elif hasattr(self.planner, "plan_course"):
            meta_content = self.planner.plan_course(course_name, description, difficulty_level, roadmap)
        else:
            self.logger.warning("⚠️ No planner method available. Using fallback metadata.")
            meta_content = {
                "overview": f"Auto-generated course for {course_name}",
                "difficulty": difficulty_level,
                "roadmap": roadmap,
                "chapters": []
            }

        # ---- Step 2: Chapters ----
        self.logger.info("Step 2: Generating chapters...")
        chapters = self._generate_chapters(course_name, description, difficulty_level, roadmap)

        # ---- Step 3: Assemble base course ----
        self.logger.info("Step 3: Building course structure...")
        course_data = self._create_course_structure(
            course_name, description, difficulty_level, roadmap, meta_content, chapters
        )

        # ---- Step 4: Mini projects ----
        self.logger.info("Step 4: Adding mini-projects...")
        mini_projects = []
        try:
            project_idea = f"{course_name} - Capstone Project"
            project_description = f"A capstone project to apply concepts from the {course_name} course."
            proj = self.project_orchestrator.create_complete_project(project_idea, project_description)
            if isinstance(proj, dict) and proj.get("status"):
                mini_projects.append(proj.get("data", proj))
            else:
                mini_projects.append(proj)
        except Exception as e:
            self.logger.warning(f"⚠️ Mini-project generation failed: {e}")

        course_data["data"]["mini_projects"] = mini_projects

        # ---- Step 5: QA ----
        self.logger.info("Step 5: Running QA review...")
        try:
            review_results = self.qa_agent.review_course_structure(course_data, course_name, difficulty_level)
        except Exception as e:
            self.logger.warning(f"⚠️ QA review failed: {e}")
            review_results = {"status": "warning", "message": "QA not available"}
        course_data["data"]["qa_review"] = review_results

        return course_data

    # ---------- Persistence ----------

    def save_course(self, course: Dict[str, Any], filename: str = None) -> str:
        """Save course JSON to disk."""
        output_dir = os.environ.get("OUTPUT_DIR", "./outputs/shiksha")
        os.makedirs(output_dir, exist_ok=True)
        if not filename:
            filename = f"course_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(course, f, indent=2, ensure_ascii=False)
        return filepath
