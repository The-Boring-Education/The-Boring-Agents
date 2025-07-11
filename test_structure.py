#!/usr/bin/env python3
"""
Simple test script to verify The Boring Agents functionality.
This script tests the basic structure without requiring actual API calls.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, '/home/runner/work/The-Boring-Agents/The-Boring-Agents')

def test_imports():
    """Test that all modules can be imported correctly."""
    print("Testing imports...")
    
    try:
        from src import Config, BaseAgent
        print("✓ Core imports successful")
        
        from src.agents import ContentAgent, InterviewAgent, ProjectAgent
        print("✓ Agent imports successful")
        
        from src.utils import setup_logging, generate_filename
        print("✓ Utility imports successful")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_configuration():
    """Test configuration management."""
    print("\nTesting configuration...")
    
    try:
        from src.core.config import Config
        
        # Test with dummy API key
        os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-testing'
        config = Config()
        
        print(f"✓ Default model: {config.default_model}")
        print(f"✓ Output directory: {config.output_dir}")
        print(f"✓ Temperature: {config.temperature}")
        print(f"✓ Max tokens: {config.max_tokens}")
        print(f"✓ API key validation: {config.validate_api_keys()}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_agent_structure():
    """Test that agents can be instantiated (without making API calls)."""
    print("\nTesting agent structure...")
    
    try:
        # Set dummy API key
        os.environ['OPENAI_API_KEY'] = 'sk-dummy-key-for-testing'
        
        from src.agents import ContentAgent, InterviewAgent, ProjectAgent
        
        # Test that we can get prompt templates (doesn't require API calls)
        content_agent = ContentAgent()
        interview_agent = InterviewAgent()
        project_agent = ProjectAgent()
        
        # Test prompt template retrieval
        content_templates = content_agent._get_prompt_templates()
        interview_templates = interview_agent._get_prompt_templates()
        project_templates = project_agent._get_prompt_templates()
        
        print(f"✓ ContentAgent templates: {list(content_templates.keys())}")
        print(f"✓ InterviewAgent templates: {list(interview_templates.keys())}")
        print(f"✓ ProjectAgent templates: {list(project_templates.keys())}")
        
        return True
    except Exception as e:
        print(f"✗ Agent structure test failed: {e}")
        return False

def test_utility_functions():
    """Test utility functions."""
    print("\nTesting utility functions...")
    
    try:
        from src.utils import (
            generate_filename, 
            clean_text, 
            extract_keywords,
            format_duration
        )
        
        # Test filename generation
        filename = generate_filename("test", "json")
        print(f"✓ Generated filename: {filename}")
        
        # Test text cleaning
        dirty_text = "  This   is   messy    text  "
        clean = clean_text(dirty_text)
        print(f"✓ Text cleaning: '{dirty_text}' -> '{clean}'")
        
        # Test keyword extraction
        text = "Python is a programming language used for web development and data science"
        keywords = extract_keywords(text)
        print(f"✓ Keywords extracted: {keywords[:5]}...")  # Show first 5
        
        # Test duration formatting
        duration = format_duration(3661)  # 1 hour, 1 minute, 1 second
        print(f"✓ Duration formatting: 3661s -> {duration}")
        
        return True
    except Exception as e:
        print(f"✗ Utility functions test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("The Boring Agents - Basic Structure Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_configuration,
        test_agent_structure,
        test_utility_functions
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✓ All tests passed ({passed}/{total})")
        print("\nThe Boring Agents structure is working correctly!")
        print("Ready for integration with actual LLM APIs.")
    else:
        print(f"✗ {total - passed} tests failed ({passed}/{total})")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())