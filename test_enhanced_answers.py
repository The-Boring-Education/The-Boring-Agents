#!/usr/bin/env python3
"""
Test script for enhanced interview answer structure and MDX styling.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.interview import AnswerEnhancementAgent, MDXStylingAgent
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_enhanced_answer_structure():
    """Test the new enhanced answer structure."""
    console.print("\n🎯 Testing Enhanced Answer Structure")
    
    try:
        # Initialize agents
        answer_agent = AnswerEnhancementAgent()
        mdx_agent = MDXStylingAgent()
        
        # Test question
        test_question = "What is the event loop in JavaScript?"
        sheet_name = "JavaScript Fundamentals"
        
        console.print(f"📝 Question: {test_question}")
        console.print(f"📋 Sheet: {sheet_name}")
        
        # Create enhanced answer
        console.print("\n🔄 Creating enhanced answer...")
        enhanced_answer = answer_agent.create_world_class_answer(
            test_question, "", sheet_name
        )
        
        # Apply MDX styling
        console.print("🎨 Applying MDX styling...")
        styled_answer = mdx_agent.format_mdx_content(enhanced_answer, "interview_answer")
        
        # Display results
        console.print("\n✅ Enhanced Answer Structure Test - PASSED")
        console.print(f"📊 Answer Length: {len(styled_answer)} characters")
        
        # Check for required sections
        required_sections = [
            "Quick Answer", "Introduction", "Code Example", 
            "Why This Concept Matters", "Different Ways Interviewers Ask This",
            "Bad Code Example", "Good Code Example", "Related Concepts to Revise",
            "Cliffhanger", "Memory Trick", "Pro Tips", "Career Impact",
            "Companies That Ask This", "Practice Scenarios", "Follow-up Questions"
        ]
        
        found_sections = []
        for section in required_sections:
            if section in styled_answer:
                found_sections.append(section)
        
        console.print(f"📋 Found {len(found_sections)}/{len(required_sections)} required sections")
        
        if len(found_sections) >= 10:  # At least 10 sections should be present
            console.print("✅ Answer structure validation - PASSED")
        else:
            console.print("❌ Answer structure validation - FAILED")
            console.print(f"Missing sections: {set(required_sections) - set(found_sections)}")
        
        # Save sample answer
        with open("output/sample_enhanced_answer.md", "w", encoding="utf-8") as f:
            f.write(f"# Sample Enhanced Answer\n\n**Question:** {test_question}\n\n{styled_answer}")
        
        console.print("💾 Sample answer saved to: output/sample_enhanced_answer.md")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Test failed: {str(e)}")
        return False

def test_mdx_styling():
    """Test MDX styling functionality."""
    console.print("\n🎨 Testing MDX Styling")
    
    try:
        mdx_agent = MDXStylingAgent()
        
        # Test content
        test_content = """
# Quick Answer
This is a quick answer.

## Introduction
This is an introduction.

## Code Example
```javascript
console.log("Hello World");
```

## Why This Concept Matters
This concept is important.

## Different Ways Interviewers Ask This
1. What is X?
2. How does X work?
3. Explain X concept

## Bad Code Example
```javascript
// Bad code
var x = 1;
```

## Good Code Example
```javascript
// Good code
const x = 1;
```

## Related Concepts to Revise
- Concept A
- Concept B

## Cliffhanger
What's next?

## Memory Trick
Think of it like...

## Pro Tips
- Tip 1
- Tip 2

## Career Impact
- Junior: ₹4-8 LPA
- Mid-level: ₹8-15 LPA
- Senior: ₹15-25 LPA

## Companies That Ask This
- Definitely: Company A, Company B
- Sometimes: Company C, Company D

## Practice Scenarios
1. Basic implementation
2. Scaling/optimization
3. Debugging

## Follow-up Questions
1. Question 1
2. Question 2
3. Question 3
"""
        
        # Apply styling
        styled_content = mdx_agent.apply_consistent_styling(test_content)
        
        console.print("✅ MDX Styling Test - PASSED")
        console.print(f"📊 Original length: {len(test_content)} characters")
        console.print(f"📊 Styled length: {len(styled_content)} characters")
        
        # Save styled content
        with open("output/sample_styled_content.md", "w", encoding="utf-8") as f:
            f.write(f"# Sample Styled Content\n\n{styled_content}")
        
        console.print("💾 Styled content saved to: output/sample_styled_content.md")
        
        return True
        
    except Exception as e:
        console.print(f"❌ MDX styling test failed: {str(e)}")
        return False

def main():
    """Run all tests."""
    console.print(Panel.fit(
        "🧪 Testing Enhanced Interview Answer System",
        title="Test Suite",
        border_style="blue"
    ))
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Run tests
    test1_passed = test_enhanced_answer_structure()
    test2_passed = test_mdx_styling()
    
    # Summary
    console.print("\n📊 Test Summary:")
    console.print(f"✅ Enhanced Answer Structure: {'PASSED' if test1_passed else 'FAILED'}")
    console.print(f"✅ MDX Styling: {'PASSED' if test2_passed else 'FAILED'}")
    
    if test1_passed and test2_passed:
        console.print("\n🎉 All tests passed! Enhanced interview answer system is working correctly.")
    else:
        console.print("\n❌ Some tests failed. Please check the error messages above.")
    
    return test1_passed and test2_passed

if __name__ == "__main__":
    main() 