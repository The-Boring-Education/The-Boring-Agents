"""API routes for Shiksha course generation and management."""

import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from .models import (
    CreateCourseRequest, 
    CreateCourseResponse, 
    Course,
    ListCoursesResponse,
    SimpleStatus
)
from ..agents.shiksha import EnhancedShikshaOrchestrator, ShikshaOrchestrator
from ..core.config import config
from ..utils import generate_filename

router = APIRouter(tags=["shiksha"])

# Simple file-based storage for courses
COURSES_DIR = os.path.join(config.output_dir, "courses")
os.makedirs(COURSES_DIR, exist_ok=True)


def load_course(course_id: str) -> Optional[dict]:
    """Load a course from storage."""
    course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
    if os.path.exists(course_file):
        with open(course_file, 'r') as f:
            return json.load(f)
    return None


def save_course(course_data: dict) -> str:
    """Save a course to storage and return course ID."""
    course_id = str(uuid.uuid4())
    course_data["id"] = course_id
    course_data["created_at"] = datetime.now().isoformat()
    course_data["status"] = "completed"
    
    course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
    with open(course_file, 'w') as f:
        json.dump(course_data, f, indent=2)
    
    return course_id


def list_all_courses() -> List[dict]:
    """List all courses from storage."""
    courses = []
    if os.path.exists(COURSES_DIR):
        for filename in os.listdir(COURSES_DIR):
            if filename.endswith('.json'):
                course_file = os.path.join(COURSES_DIR, filename)
                try:
                    with open(course_file, 'r') as f:
                        course_data = json.load(f)
                        courses.append(course_data)
                except Exception as e:
                    continue  # Skip corrupted files
    return courses


async def create_course_background(request: CreateCourseRequest, course_id: str):
    """Background task to create course."""
    try:
        if request.enhanced:
            orchestrator = EnhancedShikshaOrchestrator()
            result = orchestrator.create_world_class_course(
                course_name=request.course_name,
                description=request.description,
                difficulty_level=request.difficulty_level,
                roadmap=request.roadmap,
                api_base_url=request.api_base_url
            )
        else:
            orchestrator = ShikshaOrchestrator()
            result = orchestrator.create_complete_course(
                course_name=request.course_name,
                description=request.description,
                difficulty_level=request.difficulty_level,
                roadmap=request.roadmap
            )
        
        if result.get("status") == "success":
            course_data = result.get("data", {})
            course_data["id"] = course_id
            course_data["created_at"] = datetime.now().isoformat()
            course_data["status"] = "completed"
            
            # Save the completed course
            course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
            with open(course_file, 'w') as f:
                json.dump(course_data, f, indent=2)
        else:
            # Mark as failed
            error_data = {
                "id": course_id,
                "name": request.course_name,
                "description": request.description,
                "difficulty_level": request.difficulty_level,
                "roadmap": request.roadmap,
                "chapters": [],
                "created_at": datetime.now().isoformat(),
                "status": "failed",
                "error": result.get("message", "Unknown error")
            }
            course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
            with open(course_file, 'w') as f:
                json.dump(error_data, f, indent=2)
                
    except Exception as e:
        # Mark as failed
        error_data = {
            "id": course_id,
            "name": request.course_name,
            "description": request.description,
            "difficulty_level": request.difficulty_level,
            "roadmap": request.roadmap,
            "chapters": [],
            "created_at": datetime.now().isoformat(),
            "status": "failed",
            "error": str(e)
        }
        course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
        with open(course_file, 'w') as f:
            json.dump(error_data, f, indent=2)


@router.post("/shiksha/courses", response_model=CreateCourseResponse)
async def create_course(request: CreateCourseRequest, background_tasks: BackgroundTasks):
    """Create a new Shiksha course."""
    try:
        # Generate course ID and create initial placeholder
        course_id = str(uuid.uuid4())
        
        # Create initial course record
        initial_course = {
            "id": course_id,
            "name": request.course_name,
            "description": request.description,
            "difficulty_level": request.difficulty_level,
            "roadmap": request.roadmap,
            "chapters": [],
            "created_at": datetime.now().isoformat(),
            "status": "creating"
        }
        
        # Save initial record
        course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
        with open(course_file, 'w') as f:
            json.dump(initial_course, f, indent=2)
        
        # Add background task to actually create the course
        background_tasks.add_task(create_course_background, request, course_id)
        
        return CreateCourseResponse(
            status="success",
            message="Course creation started. Use the course ID to check status.",
            course_id=course_id,
            course=Course(**initial_course)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating course: {str(e)}")


@router.get("/shiksha/courses/{course_id}", response_model=Course)
async def get_course(course_id: str):
    """Get details of a specific course."""
    course_data = load_course(course_id)
    if not course_data:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return Course(**course_data)


@router.get("/shiksha/courses", response_model=ListCoursesResponse)
async def list_courses():
    """List all courses."""
    try:
        courses_data = list_all_courses()
        courses = [Course(**course) for course in courses_data]
        
        return ListCoursesResponse(
            status="success",
            courses=courses,
            total=len(courses)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing courses: {str(e)}")


@router.delete("/shiksha/courses/{course_id}", response_model=SimpleStatus)
async def delete_course(course_id: str):
    """Delete a course."""
    course_file = os.path.join(COURSES_DIR, f"{course_id}.json")
    if not os.path.exists(course_file):
        raise HTTPException(status_code=404, detail="Course not found")
    
    try:
        os.remove(course_file)
        return SimpleStatus(ok=True, message="Course deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting course: {str(e)}")


@router.get("/shiksha/health", response_model=SimpleStatus)
async def shiksha_health():
    """Health check for Shiksha service."""
    return SimpleStatus(ok=True, message="Shiksha service is running")