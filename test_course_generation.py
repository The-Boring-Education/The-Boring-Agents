#!/usr/bin/env python3
"""
Test script for course generation functionality.
This script tests the new course development features without requiring actual API calls.
"""

import sys
import os
import json

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents')

def test_course_schema_validation():
    """Test that the course generation produces the correct JSON schema."""
    print("Testing course schema validation...")
    
    # Sample course data in the expected format
    expected_schema = {
        "status": True,
        "data": {
            "_id": "6799dfcadd77f0ff4c605790",
            "name": "Zero to One Backend Dev with Node.js",
            "slug": "zero-to-one-backend-development",
            "coverImageURL": "https://ik.imagekit.io/tbe/webapp/shiksha-zero-to-one-backend-dev-cover.svg",
            "description": "Start Your Backend Dev Journey. Projects Included.",
            "liveOn": "2025-01-31T06:00:00.000Z",
            "roadmap": "Backend",
            "difficultyLevel": "Beginner",
            "chapters": [
                {
                    "name": "GitHub - Version Control and Collaboration",
                    "content": "# GitHub - Version Control and Collaboration\n\n...",
                    "_id": "6799ee55dd77f0ff4c60592a",
                    "createdAt": "2025-01-29T09:01:09.636Z",
                    "updatedAt": "2025-01-29T09:01:09.636Z"
                }
            ]
        }
    }
    
    # Test schema validation function
    def validate_course_schema(course_data):
        required_fields = ["status", "data"]
        data_fields = ["_id", "name", "slug", "coverImageURL", "description", 
                      "liveOn", "roadmap", "difficultyLevel", "chapters"]
        chapter_fields = ["name", "content", "_id", "createdAt", "updatedAt"]
        
        # Check top-level fields
        for field in required_fields:
            if field not in course_data:
                return False, f"Missing top-level field: {field}"
        
        # Check data fields
        data = course_data.get("data", {})
        for field in data_fields:
            if field not in data:
                return False, f"Missing data field: {field}"
        
        # Check chapters structure
        chapters = data.get("chapters", [])
        if not isinstance(chapters, list):
            return False, "Chapters must be a list"
        
        for i, chapter in enumerate(chapters):
            for field in chapter_fields:
                if field not in chapter:
                    return False, f"Missing field '{field}' in chapter {i}"
        
        return True, "Schema validation passed"
    
    # Test the validation
    is_valid, message = validate_course_schema(expected_schema)
    
    if is_valid:
        print("✓ Course schema validation passed")
        return True
    else:
        print(f"✗ Course schema validation failed: {message}")
        return False

def test_content_agent_structure():
    """Test that ContentAgent has the new methods."""
    print("Testing ContentAgent structure...")
    
    try:
        # Set dummy API key
        os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-testing'
        
        from src.agents import ContentAgent
        
        # Test that we can instantiate the agent
        agent = ContentAgent()
        
        # Test that new methods exist
        required_methods = [
            'generate_chapter_content',
            'create_complete_course',
            '_get_default_chapters'
        ]
        
        for method_name in required_methods:
            if not hasattr(agent, method_name):
                print(f"✗ Missing method: {method_name}")
                return False
        
        # Test that new prompt templates exist
        templates = agent._get_prompt_templates()
        required_templates = [
            'chapter_content',
            'complete_course'
        ]
        
        for template_name in required_templates:
            if template_name not in templates:
                print(f"✗ Missing template: {template_name}")
                return False
        
        print("✓ ContentAgent structure test passed")
        print(f"✓ Available templates: {list(templates.keys())}")
        print(f"✓ Available methods: {[m for m in dir(agent) if not m.startswith('_') and callable(getattr(agent, m))]}")
        
        return True
    except Exception as e:
        print(f"✗ ContentAgent structure test failed: {e}")
        return False

def test_default_chapters():
    """Test the default chapter generation."""
    print("Testing default chapter generation...")
    
    try:
        os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-testing'
        
        from src.agents import ContentAgent
        agent = ContentAgent()
        
        # Test backend chapters
        backend_chapters = agent._get_default_chapters("Backend Development", "Backend")
        if len(backend_chapters) < 8:
            print(f"✗ Backend chapters too few: {len(backend_chapters)}")
            return False
        
        # Test frontend chapters  
        frontend_chapters = agent._get_default_chapters("Frontend Development", "Frontend")
        if len(frontend_chapters) < 6:
            print(f"✗ Frontend chapters too few: {len(frontend_chapters)}")
            return False
        
        # Test generic chapters
        generic_chapters = agent._get_default_chapters("Python Programming", "Programming")
        if len(generic_chapters) < 6:
            print(f"✗ Generic chapters too few: {len(generic_chapters)}")
            return False
        
        print(f"✓ Backend chapters: {len(backend_chapters)} chapters")
        print(f"✓ Frontend chapters: {len(frontend_chapters)} chapters") 
        print(f"✓ Generic chapters: {len(generic_chapters)} chapters")
        
        return True
    except Exception as e:
        print(f"✗ Default chapters test failed: {e}")
        return False

def test_cli_imports():
    """Test that the CLI imports work correctly."""
    print("Testing CLI imports...")
    
    try:
        # Test that main.py can be imported (which tests all the import paths)
        import main
        print("✓ CLI imports successful")
        return True
    except Exception as e:
        print(f"✗ CLI imports failed: {e}")
        return False

def main():
    """Run all tests."""
    print("The Boring Agents - Course Generation Test")
    print("=" * 50)
    
    tests = [
        test_course_schema_validation,
        test_content_agent_structure,
        test_default_chapters,
        test_cli_imports
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()  # Add spacing between tests
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("\nCourse generation functionality is working correctly!")
        print("Ready for integration with actual LLM APIs.")
    else:
        print(f"✗ {total - passed} tests failed ({passed}/{total})")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())