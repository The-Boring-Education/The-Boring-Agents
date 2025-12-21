"""Quick test to verify question IDs are properly assigned during parsing."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.interview.interview_sheet_manager import InterviewSheetManager
from core.config import config
from utils.session_logger import SessionLogger

# Create logger
logger = SessionLogger("test-session")

# Create manager instance
manager = InterviewSheetManager(
    config=config,
    logger=logger,
    language="python"
)

# Test data: Sample MDX content with questions
test_mdx_content = """# Python Interview Questions – The Boring Education

## Questions

- Question: What is a decorator in Python?
  - Difficulty: Hard
  - Frequency: High
  - Priority: High
  - Company Types: MNC, Startup

- Question: Explain list comprehensions in Python.
  - Difficulty: Medium
  - Frequency: High
  - Priority: Medium
  - Company Types: Startup, Freelance

- Question: What is the difference between == and is?
  - Difficulty: Easy
  - Frequency: Medium
  - Priority: High
  - Company Types: MNC
"""

# Parse questions
questions = manager._parse_questions_from_mdx(test_mdx_content)

print("✅ Test Results:")
print(f"Total questions parsed: {len(questions)}")
print()

for i, q in enumerate(questions, 1):
    print(f"Question {i}:")
    print(f"  ID: {q.get('id')} {'✅' if q.get('id') else '❌ MISSING'}")
    print(f"  Text: {q.get('question')[:50]}...")
    print(f"  Difficulty: {q.get('difficulty')}")
    print(f"  Has created_at: {bool(q.get('created_at'))} ✅" if q.get('created_at') else "  Has created_at: False ❌")
    print(f"  Has updated_at: {bool(q.get('updated_at'))} ✅" if q.get('updated_at') else "  Has updated_at: False ❌")
    print()

# Check all IDs are unique
ids = [q.get('id') for q in questions]
unique_ids = set(ids)
if len(ids) == len(unique_ids):
    print("✅ All question IDs are UNIQUE")
else:
    print(f"❌ Duplicate IDs found! {len(ids)} questions but only {len(unique_ids)} unique IDs")

# Check no None IDs
if None in ids:
    print(f"❌ Found {ids.count(None)} questions with None as ID")
else:
    print("✅ All questions have valid IDs (no None values)")

print("\n✅ Test complete!")
