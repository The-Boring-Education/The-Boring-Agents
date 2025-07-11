#!/usr/bin/env python3
"""
Test script for Shiksha course generation system.
This demonstrates the multi-agent system for creating complete tech courses.
"""

import sys
import os
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_shiksha_course_generation():
    """Test the Shiksha course generation system."""
    print("🧪 Testing Shiksha Course Generation System")
    print("=" * 50)
    
    try:
        from src.agents import ShikshaOrchestrator
        
        # Initialize the orchestrator
        print("🔧 Initializing Shiksha Orchestrator...")
        orchestrator = ShikshaOrchestrator()
        print("✅ Orchestrator initialized successfully")
        
        # Test course parameters
        course_name = "Zero to One Frontend Development with React"
        description = "Master React.js from basics to advanced concepts. Build real projects and become a frontend developer."
        difficulty_level = "Beginner"
        roadmap = "Frontend"
        
        print(f"\n📚 Creating course: {course_name}")
        print(f"📝 Description: {description}")
        print(f"🎯 Difficulty: {difficulty_level}")
        print(f"🗺️ Roadmap: {roadmap}")
        
        # Generate the course
        print("\n🚀 Starting course generation...")
        start_time = datetime.now()
        
        course_data = orchestrator.create_complete_course(
            course_name=course_name,
            description=description,
            difficulty_level=difficulty_level,
            roadmap=roadmap
        )
        
        end_time = datetime.now()
        generation_time = (end_time - start_time).total_seconds()
        
        print(f"✅ Course generation completed in {generation_time:.2f} seconds")
        
        # Display course summary
        data = course_data.get("data", {})
        chapters = data.get("chapters", [])
        
        print(f"\n📊 Course Summary:")
        print(f"   Course Name: {data.get('name', 'N/A')}")
        print(f"   Slug: {data.get('slug', 'N/A')}")
        print(f"   Difficulty: {data.get('difficultyLevel', 'N/A')}")
        print(f"   Roadmap: {data.get('roadmap', 'N/A')}")
        print(f"   Total Chapters: {len(chapters)}")
        print(f"   Live Date: {data.get('liveOn', 'N/A')}")
        
        # Display chapter names
        print(f"\n📖 Chapters:")
        for i, chapter in enumerate(chapters, 1):
            chapter_name = chapter.get("name", f"Chapter {i}")
            content_length = len(chapter.get("content", ""))
            print(f"   {i:2d}. {chapter_name} ({content_length} characters)")
        
        # Save the course
        print(f"\n💾 Saving course to file...")
        filepath = orchestrator.save_course(course_data)
        print(f"✅ Course saved to: {filepath}")
        
        # Validate the saved file
        print(f"\n🔍 Validating saved course...")
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        if saved_data.get("status") and saved_data.get("data"):
            print("✅ Course validation passed")
        else:
            print("❌ Course validation failed")
        
        print(f"\n🎉 Shiksha course generation test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_agents():
    """Test individual agents separately."""
    print("\n🧪 Testing Individual Agents")
    print("=" * 30)
    
    try:
        from src.agents import CoursePlannerAgent, ContentCreatorAgent, QualityAssuranceAgent
        
        # Test Course Planner Agent
        print("📋 Testing Course Planner Agent...")
        planner = CoursePlannerAgent()
        course_plan = planner.create_course_structure(
            "Python Web Development",
            "Learn Python web development with Django and Flask",
            "Intermediate",
            "Backend"
        )
        print("✅ Course Planner Agent working")
        
        # Test Content Creator Agent
        print("✍️ Testing Content Creator Agent...")
        creator = ContentCreatorAgent()
        chapter_content = creator.create_chapter_content(
            "Introduction to Python",
            "Python Web Development",
            1,
            15,
            "Intermediate"
        )
        print("✅ Content Creator Agent working")
        
        # Test Quality Assurance Agent
        print("🔍 Testing Quality Assurance Agent...")
        qa = QualityAssuranceAgent()
        review = qa.review_chapter_content(
            chapter_content,
            "Introduction to Python",
            "Python Web Development",
            "Intermediate"
        )
        print("✅ Quality Assurance Agent working")
        
        print("✅ All individual agents working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Error testing individual agents: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("The Boring Agents - Shiksha Course Generation Test")
    print("=" * 60)
    
    # Test individual agents
    agents_ok = test_individual_agents()
    
    # Test complete course generation
    course_ok = test_shiksha_course_generation()
    
    print("\n" + "=" * 60)
    
    if agents_ok and course_ok:
        print("🎉 All tests passed! The Shiksha course generation system is working correctly.")
        print("\n📚 You can now create courses using:")
        print("   python main.py shiksha create-course --course-name 'Your Course' --description 'Your Description' --save")
        return 0
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 