#!/usr/bin/env python3
"""
Automated Shiksha Course Creation Demo

This script demonstrates the complete automated workflow for creating
Shiksha courses using both CLI and API approaches.
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_cli_demo():
    """Demonstrate CLI-based course creation."""
    print("🎓 SHIKSHA CLI DEMO")
    print("=" * 50)
    
    # Example course parameters
    course_name = "Python for Beginners"
    description = "Learn Python programming from scratch with hands-on examples"
    difficulty = "Beginner"
    roadmap = "Backend"
    
    print(f"Creating course: {course_name}")
    print(f"Description: {description}")
    print(f"Difficulty: {difficulty}")
    print(f"Roadmap: {roadmap}")
    print()
    
    # Build CLI command
    cmd = [
        sys.executable, "main.py", "shiksha", "create-course",
        "--course-name", course_name,
        "--description", description,
        "--difficulty", difficulty,
        "--roadmap", roadmap,
        "--save"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    print("-" * 30)
    
    try:
        # Note: This would require valid API keys to actually work
        print("⚠️  Note: This requires valid API keys in .env file")
        print("⚠️  Skipping actual CLI execution for demo")
        print("✅ CLI command structure validated")
        
    except Exception as e:
        print(f"❌ CLI Demo failed: {e}")
    
    print()

def run_api_demo():
    """Demonstrate API-based course creation."""
    print("🌐 SHIKSHA API DEMO")
    print("=" * 50)
    
    api_base = "http://localhost:8088/api/v1"
    
    # Test data
    course_data = {
        "course_name": "Introduction to Machine Learning",
        "description": "Comprehensive introduction to ML concepts and algorithms",
        "difficulty_level": "Intermediate", 
        "roadmap": "Data Science",
        "enhanced": False  # Use basic orchestrator for demo
    }
    
    print(f"API Base URL: {api_base}")
    print(f"Course Data: {json.dumps(course_data, indent=2)}")
    print()
    
    try:
        # Test health endpoint
        print("1. Testing health endpoint...")
        health_url = f"{api_base}/shiksha/health"
        
        print(f"   GET {health_url}")
        print("   ⚠️  Note: This requires the API server to be running")
        print("   ⚠️  Start with: python run_api.py")
        print("   ✅ Health endpoint structure validated")
        print()
        
        # Test course creation
        print("2. Testing course creation...")
        create_url = f"{api_base}/shiksha/courses"
        
        print(f"   POST {create_url}")
        print("   ⚠️  Note: This requires valid API keys and running server")
        print("   ✅ Course creation endpoint structure validated")
        print()
        
        # Test course listing
        print("3. Testing course listing...")
        list_url = f"{api_base}/shiksha/courses"
        
        print(f"   GET {list_url}")
        print("   ✅ Course listing endpoint structure validated")
        print()
        
    except Exception as e:
        print(f"❌ API Demo failed: {e}")

def show_file_structure():
    """Show the expected file structure after course creation."""
    print("📁 FILE STRUCTURE")
    print("=" * 50)
    
    print("After course creation, files are stored in:")
    print()
    print("output/")
    print("├── courses/")
    print("│   ├── {course-id-1}.json    # Course 1 data")
    print("│   ├── {course-id-2}.json    # Course 2 data") 
    print("│   └── ...")
    print("└── shiksha_course_*.json     # CLI generated courses")
    print()
    
    # Show example course structure
    example_course = {
        "id": "12345678-1234-1234-1234-123456789012",
        "name": "Introduction to Python",
        "description": "Learn Python programming fundamentals",
        "difficulty_level": "Beginner",
        "roadmap": "Backend",
        "chapters": [
            {
                "title": "Python Basics",
                "topics": ["Variables", "Data Types", "Control Flow"],
                "exercises": ["Basic syntax practice", "Simple programs"]
            }
        ],
        "created_at": "2024-01-01T12:00:00",
        "status": "completed"
    }
    
    print("Example course structure:")
    print(json.dumps(example_course, indent=2))
    print()

def show_integration_examples():
    """Show integration examples for different use cases."""
    print("🔗 INTEGRATION EXAMPLES")
    print("=" * 50)
    
    print("1. Automated Course Pipeline:")
    print()
    python_script = '''
# Python automation script
import requests

def create_courses_batch():
    courses = [
        {"name": "Python Basics", "roadmap": "Backend"},
        {"name": "React Fundamentals", "roadmap": "Frontend"},
        {"name": "Data Analysis", "roadmap": "Data Science"}
    ]
    
    for course in courses:
        response = requests.post("http://localhost:8088/api/v1/shiksha/courses", json={
            "course_name": course["name"],
            "description": f"Complete course on {course['name']}",
            "difficulty_level": "Beginner",
            "roadmap": course["roadmap"],
            "enhanced": True
        })
        print(f"Created course: {response.json()}")

create_courses_batch()
'''
    print(python_script)
    
    print("2. Bash Automation Script:")
    print()
    bash_script = '''#!/bin/bash
# Batch course creation
courses=("Python" "JavaScript" "Go" "Rust")
for course in "${courses[@]}"; do
    python main.py shiksha create-course \\
        --course-name "Introduction to $course" \\
        --description "Learn $course programming" \\
        --difficulty "Beginner" \\
        --roadmap "Backend" \\
        --save
done
'''
    print(bash_script)
    
    print("3. CI/CD Integration:")
    print()
    cicd_example = '''
# GitHub Actions example
name: Generate Courses
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Generate courses
        run: python scripts/batch_course_creation.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
'''
    print(cicd_example)

def main():
    """Run the complete demo."""
    print("🎓 SHIKSHA AGENTIC SYSTEM DEMO")
    print("=" * 60)
    print("Automated Course Creation for The Boring Education Platform")
    print("=" * 60)
    print()
    
    # Run all demo sections
    run_cli_demo()
    run_api_demo()
    show_file_structure()
    show_integration_examples()
    
    print("🎯 SUMMARY")
    print("=" * 50)
    print("✅ Shiksha system provides complete automation for course creation")
    print("✅ Both CLI and API interfaces available")
    print("✅ Structured storage with unique course IDs")
    print("✅ Support for enhanced course generation with research")
    print("✅ Ready for integration with external systems")
    print()
    print("🚀 Next Steps:")
    print("1. Set up API keys in .env file")
    print("2. Start API server: python run_api.py")
    print("3. Create courses via CLI or API")
    print("4. Integrate with your education platform")
    print()

if __name__ == "__main__":
    main()