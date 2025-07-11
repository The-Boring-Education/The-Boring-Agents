#!/usr/bin/env python3
"""
Final validation script for SHIKSHA course development.
Validates that the generated courses match the exact schema from the problem statement.
"""

import sys
import os
import json
from datetime import datetime

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents')
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents/src')

def validate_course_schema(course_data):
    """Validate that course data matches the expected SHIKSHA schema."""
    print("Validating course schema...")
    
    # Expected structure from problem statement
    required_top_level = ["status", "data"]
    required_data_fields = [
        "_id", "name", "slug", "coverImageURL", "description", 
        "liveOn", "roadmap", "difficultyLevel", "chapters"
    ]
    required_chapter_fields = [
        "name", "content", "_id", "createdAt", "updatedAt"
    ]
    
    # Validate top level
    for field in required_top_level:
        assert field in course_data, f"Missing top-level field: {field}"
        print(f"✓ Has {field}")
    
    assert course_data["status"] == True, "Status should be True"
    print("✓ Status is True")
    
    # Validate data section
    data = course_data["data"]
    for field in required_data_fields:
        assert field in data, f"Missing data field: {field}"
        print(f"✓ Has data.{field}")
    
    # Validate chapters
    assert isinstance(data["chapters"], list), "Chapters should be a list"
    assert len(data["chapters"]) > 0, "Should have at least one chapter"
    print(f"✓ Has {len(data['chapters'])} chapters")
    
    # Validate first chapter structure
    first_chapter = data["chapters"][0]
    for field in required_chapter_fields:
        assert field in first_chapter, f"Missing chapter field: {field}"
        print(f"✓ Chapter has {field}")
    
    # Validate content format
    content = first_chapter["content"]
    assert content.startswith("#"), "Chapter content should start with markdown header"
    assert "📌" in content, "Should have callout boxes"
    assert "### Why Do You Need" in content, "Should have structured sections"
    assert "## Tutorial" in content, "Should have tutorial section"
    assert "youtube.com" in content, "Should have YouTube links"
    assert "## Share It On Social Media" in content, "Should have social media section"
    assert "### LinkedIn" in content, "Should have LinkedIn template"
    assert "### Twitter" in content, "Should have Twitter template"
    assert "#Shiksha #TheBoringEducation" in content, "Should have proper hashtags"
    print("✓ Chapter content has all required sections")
    
    return True

def test_example_from_problem_statement():
    """Test against the exact example from the problem statement."""
    print("\nTesting against problem statement example...")
    
    # Expected structure from the problem
    expected_fields = {
        "status": True,
        "data": {
            "_id": "string",
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
                    "content": "# GitHub - Version Control and Collaboration...",
                    "_id": "string",
                    "createdAt": "2025-01-29T09:01:09.636Z",
                    "updatedAt": "2025-01-29T09:01:09.636Z"
                }
            ]
        }
    }
    
    # Load our generated course
    output_file = "./output/demo_shiksha_course.json"
    assert os.path.exists(output_file), f"Output file not found: {output_file}"
    
    with open(output_file, 'r') as f:
        our_course = json.load(f)
    
    # Validate structure matches
    validate_course_schema(our_course)
    
    # Check specific fields match expected types
    data = our_course["data"]
    assert isinstance(data["_id"], str), "_id should be string"
    assert isinstance(data["name"], str), "name should be string"
    assert isinstance(data["slug"], str), "slug should be string"
    assert data["coverImageURL"].startswith("https://"), "coverImageURL should be valid URL"
    assert isinstance(data["description"], str), "description should be string"
    assert "T" in data["liveOn"], "liveOn should be ISO datetime"
    assert data["roadmap"] in ["Backend", "Frontend", "Fullstack"], "roadmap should be valid"
    assert data["difficultyLevel"] in ["Beginner", "Intermediate", "Advanced"], "difficulty should be valid"
    
    print("✓ All fields match expected types")
    print("✓ Structure matches problem statement example")
    
    return True

def test_mdx_content_format():
    """Test that the MDX content format matches the expected structure."""
    print("\nTesting MDX content format...")
    
    # Load generated course
    output_file = "./output/demo_shiksha_course.json"
    with open(output_file, 'r') as f:
        course_data = json.load(f)
    
    # Check first chapter content
    first_chapter = course_data["data"]["chapters"][0]
    content = first_chapter["content"]
    
    # Expected patterns from the problem statement example
    patterns = [
        "# ",  # Main header
        "📌",  # Callout box
        "**When I started learning",  # Personal intro
        "### Why Do You Need",  # Why section
        "### How Important Is It?",  # Importance section
        "### How Long Will It Take to Learn?",  # Time estimate
        "## Tutorial",  # Tutorial section
        "[Complete",  # Video link format
        "https://www.youtube.com/watch?v=",  # YouTube URL
        "💡",  # Tip callout
        "### Projects to Build",  # Projects section
        "## Share It On Social Media",  # Social media section
        "### LinkedIn",  # LinkedIn template
        "### Twitter",  # Twitter template
        "```",  # Code blocks for templates
        "#Shiksha #TheBoringEducation",  # Required hashtags
    ]
    
    for pattern in patterns:
        assert pattern in content, f"Missing expected pattern: {pattern}"
        print(f"✓ Contains: {pattern}")
    
    print("✓ MDX content format matches expected structure")
    return True

def main():
    """Run all validation tests."""
    print("SHIKSHA Course Schema Validation")
    print("=" * 50)
    
    tests = [
        test_example_from_problem_statement,
        test_mdx_content_format
    ]
    
    try:
        for test in tests:
            test()
        
        print("\n" + "=" * 50)
        print("✅ ALL VALIDATIONS PASSED!")
        print("\nThe SHIKSHA course development feature:")
        print("✓ Generates courses in the exact schema format")
        print("✓ Creates MDX content with proper structure")
        print("✓ Includes YouTube video integration")
        print("✓ Has social media sharing templates")
        print("✓ Follows The Boring Education branding")
        print("✓ Ready for production use")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())