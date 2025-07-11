#!/usr/bin/env python3
"""
Test script for SHIKSHA course development functionality.
This script tests the new features without making actual API calls.
"""

import sys
import os
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents')
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents/src')

def test_shiksha_course_structure():
    """Test the SHIKSHA course structure generation."""
    print("Testing SHIKSHA course structure...")
    
    try:
        from src.agents.content_agent import ContentAgent
        
        # Mock the LLM to avoid API calls
        class MockLLM:
            def predict(self, prompt):
                return """
                # Complete Node.js Backend Development Course
                
                This course covers everything from basics to advanced Node.js development.
                
                ## Chapters:
                1. Introduction and Setup
                2. Node.js Fundamentals  
                3. Express.js Framework
                4. Database Integration
                5. Authentication & Security
                6. API Development
                7. Testing & Deployment
                8. Advanced Topics
                """
        
        # Create agent and mock the LLM
        agent = ContentAgent()
        agent._llm = MockLLM()
        
        # Test course generation
        result = agent.create_shiksha_course(
            topic="Node.js Backend Development",
            level="intermediate", 
            roadmap="Backend",
            description="Complete backend development with Node.js"
        )
        
        # Validate structure
        assert "generated_content" in result
        assert "data" in result["generated_content"]
        
        course_data = result["generated_content"]["data"]
        assert "name" in course_data
        assert "slug" in course_data
        assert "chapters" in course_data
        assert "difficultyLevel" in course_data
        assert "roadmap" in course_data
        
        print(f"✓ Course generated: {course_data['name']}")
        print(f"✓ Slug: {course_data['slug']}")
        print(f"✓ Chapters: {len(course_data['chapters'])}")
        print(f"✓ Level: {course_data['difficultyLevel']}")
        print(f"✓ Roadmap: {course_data['roadmap']}")
        
        return True
        
    except Exception as e:
        print(f"✗ SHIKSHA course structure test failed: {e}")
        return False

def test_prompt_templates():
    """Test that new prompt templates are available."""
    print("\nTesting prompt templates...")
    
    try:
        from src.agents.content_agent import ContentAgent
        
        agent = ContentAgent()
        templates = agent._get_prompt_templates()
        
        required_templates = [
            "shiksha_course",
            "shiksha_chapter", 
            "social_media",
            "course_outline",
            "video_suggestions",
            "text_content",
            "tricks_and_tips"
        ]
        
        for template_name in required_templates:
            assert template_name in templates, f"Missing template: {template_name}"
            print(f"✓ Template available: {template_name}")
        
        # Test template formatting
        shiksha_template = templates["shiksha_course"]
        formatted = shiksha_template.format(
            topic="React Development",
            level="beginner",
            roadmap="Frontend", 
            description="Learn React from basics"
        )
        
        assert "React Development" in formatted
        assert "beginner" in formatted
        assert "Frontend" in formatted
        
        print("✓ Template formatting works correctly")
        return True
        
    except Exception as e:
        print(f"✗ Prompt templates test failed: {e}")
        return False

def test_chapter_parsing():
    """Test chapter parsing functionality."""
    print("\nTesting chapter parsing...")
    
    try:
        from src.agents.content_agent import ContentAgent
        
        agent = ContentAgent()
        
        # Test chapter parsing
        sample_content = """
        This is a sample course with multiple chapters.
        We'll cover various topics in depth.
        """
        
        chapters = agent._parse_chapters_from_content(sample_content)
        
        assert isinstance(chapters, list)
        assert len(chapters) > 0
        
        # Validate chapter structure
        for chapter in chapters:
            assert "name" in chapter
            assert "content" in chapter
            assert "_id" in chapter
            assert "createdAt" in chapter
            assert "updatedAt" in chapter
        
        print(f"✓ Parsed {len(chapters)} chapters")
        print(f"✓ Chapter structure validated")
        
        return True
        
    except Exception as e:
        print(f"✗ Chapter parsing test failed: {e}")
        return False

def test_social_media_templates():
    """Test social media template generation."""
    print("\nTesting social media templates...")
    
    try:
        from src.agents.content_agent import ContentAgent
        
        class MockLLM:
            def predict(self, prompt):
                return """
                **LinkedIn Post:**
                🚀 Just completed Node.js Backend Development!
                
                Here's what I achieved:
                ✔ Built RESTful APIs
                ✔ Learned Express.js framework
                ✔ Implemented authentication
                
                Learning all this in Shiksha by The Boring Education 🎓
                
                **Twitter Post:**
                🚀 Completed Node.js backend course!
                ✔ APIs ✔ Express.js ✔ Auth
                Learning with Shiksha by The Boring Education! 
                #NodeJS #Backend #Shiksha
                """
        
        agent = ContentAgent()
        agent._llm = MockLLM()
        
        result = agent.generate_social_media_templates(
            topic="Node.js Backend",
            achievement="Built complete backend application",
            learning_points=["RESTful APIs", "Express.js", "Authentication"]
        )
        
        assert "generated_content" in result
        content = result["generated_content"]
        assert "LinkedIn" in content
        assert "Twitter" in content
        assert "Shiksha" in content
        
        print("✓ Social media templates generated")
        print("✓ Contains LinkedIn and Twitter templates")
        print("✓ Includes Shiksha branding")
        
        return True
        
    except Exception as e:
        print(f"✗ Social media templates test failed: {e}")
        return False

def test_json_schema_compliance():
    """Test that generated course matches expected JSON schema."""
    print("\nTesting JSON schema compliance...")
    
    try:
        from src.agents.content_agent import ContentAgent
        
        class MockLLM:
            def predict(self, prompt):
                return "Mock course content for testing"
        
        agent = ContentAgent()
        agent._llm = MockLLM()
        
        result = agent.create_shiksha_course(
            topic="Test Course",
            level="beginner",
            roadmap="Backend",
            description="Test description"
        )
        
        # Validate schema structure matches the example from the problem statement
        course_data = result["generated_content"]
        
        assert "status" in course_data
        assert "data" in course_data
        
        data = course_data["data"]
        required_fields = [
            "_id", "name", "slug", "coverImageURL", "description",
            "liveOn", "roadmap", "difficultyLevel", "chapters"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        # Validate chapters structure
        assert isinstance(data["chapters"], list)
        if data["chapters"]:
            chapter = data["chapters"][0]
            chapter_fields = ["name", "content", "_id", "createdAt", "updatedAt"]
            for field in chapter_fields:
                assert field in chapter, f"Missing chapter field: {field}"
        
        print("✓ JSON schema compliance validated")
        print("✓ All required fields present")
        print("✓ Chapter structure correct")
        
        return True
        
    except Exception as e:
        print(f"✗ JSON schema compliance test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("SHIKSHA Course Development - Functionality Test")
    print("=" * 60)
    
    tests = [
        test_prompt_templates,
        test_shiksha_course_structure,
        test_chapter_parsing,
        test_social_media_templates,
        test_json_schema_compliance
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("\nSHIKSHA course development functionality is working correctly!")
        print("Ready for API integration and real course generation.")
    else:
        print(f"✗ {total - passed} tests failed ({passed}/{total})")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())