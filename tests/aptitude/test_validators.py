"""Tests for aptitude payload and answer validators."""

import pytest

from src.agents.aptitude.validators import (
    validate_answer_structure,
    validate_batch_payload,
    validate_question_payload,
    validate_topic_payload,
)


class TestValidateTopicPayload:
    def test_valid_payload(self):
        result = validate_topic_payload(
            topic_name="Problem on Trains",
            questions=["A train running at 60 km/hr crosses a pole in 9 seconds. What is the length of the train?"],
        )
        assert result["valid"] is True
        assert result["errors"] == []

    def test_empty_topic_name(self):
        result = validate_topic_payload(topic_name="", questions=["Some question here?"])
        assert result["valid"] is False
        assert any("topic_name" in e for e in result["errors"])

    def test_empty_questions_list(self):
        result = validate_topic_payload(topic_name="Trains", questions=[])
        assert result["valid"] is False
        assert any("question" in e.lower() for e in result["errors"])

    def test_none_questions(self):
        result = validate_topic_payload(topic_name="Trains", questions=None)
        assert result["valid"] is False

    def test_question_too_short(self):
        result = validate_topic_payload(topic_name="Trains", questions=["Hi?"])
        assert result["valid"] is False
        assert any("too short" in e for e in result["errors"])

    def test_empty_question_in_list(self):
        result = validate_topic_payload(
            topic_name="Trains",
            questions=["Valid question here about trains", ""],
        )
        assert result["valid"] is False
        assert any("index 1" in e for e in result["errors"])

    def test_invalid_category(self):
        result = validate_topic_payload(
            topic_name="Trains",
            questions=["A valid question about trains?"],
            category="INVALID_CATEGORY",
        )
        assert result["valid"] is False
        assert any("category" in e.lower() for e in result["errors"])

    def test_invalid_sub_category(self):
        result = validate_topic_payload(
            topic_name="Trains",
            questions=["A valid question about trains?"],
            sub_category="INVALID_SUB",
        )
        assert result["valid"] is False
        assert any("sub_category" in e.lower() for e in result["errors"])

    def test_valid_with_explicit_category(self):
        result = validate_topic_payload(
            topic_name="Custom Topic",
            questions=["A proper question about the topic?"],
            category="QUANTITATIVE",
            sub_category="ARITHMETIC_APTITUDE",
        )
        assert result["valid"] is True

    def test_multiple_valid_questions(self):
        result = validate_topic_payload(
            topic_name="Percentage",
            questions=[
                "What is 20% of 500?",
                "If a price increases by 15%, what is the new price of Rs. 200?",
                "Find the percentage increase from 40 to 50.",
            ],
        )
        assert result["valid"] is True
        assert result["errors"] == []


class TestValidateQuestionPayload:
    def test_valid_question(self):
        result = validate_question_payload({
            "question": "What is the simple interest on Rs. 5000 at 10% per annum for 2 years?",
            "topicId": "abc123",
        })
        assert result["valid"] is True

    def test_missing_question_text(self):
        result = validate_question_payload({"topicId": "abc123"})
        assert result["valid"] is False
        assert any("question" in e for e in result["errors"])

    def test_missing_topic_id(self):
        result = validate_question_payload({"question": "Some valid question?"})
        assert result["valid"] is False
        assert any("topicId" in e for e in result["errors"])

    def test_invalid_difficulty(self):
        result = validate_question_payload({
            "question": "Some valid question?",
            "topicId": "abc123",
            "difficulty": "SUPER_HARD",
        })
        assert result["valid"] is False
        assert any("difficulty" in e.lower() for e in result["errors"])

    def test_valid_difficulty_values(self):
        for diff in ["EASY", "MEDIUM", "HARD"]:
            result = validate_question_payload({
                "question": "Valid question here?",
                "topicId": "abc123",
                "difficulty": diff,
            })
            assert result["valid"] is True


class TestValidateAnswerStructure:
    def test_speed_format_complete(self):
        answer = """
##### 📘 Fundamental Concept
Speed = Distance / Time

##### 🧱 The Conventional Method
Step 1: Let the length = L
Step 2: L = 60 * 5/18 * 9

##### ⚡ The Pro Shortcut (Trick)
Just multiply speed in m/s by time.

##### ⚠️ Common Trap
Students forget to convert km/hr to m/s.

##### ⏱️ Time-Saving Tip
Check if answer is divisible by 5.
"""
        result = validate_answer_structure(answer, "SPEED")
        assert result["valid"] is True
        assert result["missing_sections"] == []

    def test_speed_format_missing_sections(self):
        answer = """
##### 📘 Fundamental Concept
Speed = Distance / Time

##### 🧱 The Conventional Method
Step 1: solve it
"""
        result = validate_answer_structure(answer, "SPEED")
        assert result["valid"] is False
        assert "The Pro Shortcut" in result["missing_sections"] or len(result["missing_sections"]) > 0

    def test_rules_format_complete(self):
        answer = """
##### 🖋️ Context & Meaning
The sentence tests subject-verb agreement.

##### ⚖️ The Grammar Rule
Subject-verb agreement: singular subjects take singular verbs.

##### ❌ Why Others Are Wrong
Option A: incorrect tense. Option B: wrong number.

##### 💡 Vocabulary Bridge
Remember: "each" is always singular.
"""
        result = validate_answer_structure(answer, "RULES")
        assert result["valid"] is True

    def test_perspective_format_complete(self):
        answer = """
##### 🌍 Topic Overview
This topic is relevant because of recent policy changes.

##### ✅ Arguments FOR
- Point 1
- Point 2

##### ❌ Arguments AGAINST
- Counter 1
- Counter 2

##### 📊 Key Facts/Stats
- 65% of people surveyed agree
- Policy enacted in 2023

##### 🤝 The Closing Stance
Both sides have merit. A balanced approach is needed.
"""
        result = validate_answer_structure(answer, "PERSPECTIVE")
        assert result["valid"] is True

    def test_behavioral_format_complete(self):
        answer = """
##### 🕵️ The Interviewer's Intent
They want to assess communication skills and confidence.

##### ⭐ The STAR Strategy
Situation: During my college project...
Task: I was responsible for...
Action: I decided to...
Result: We achieved...

##### 📝 Sample "Winning" Answer
"I am a final year student passionate about technology..."

##### 🚩 Red Flags (Do NOT Say)
1. Don't badmouth previous employers
2. Don't say "I have no weaknesses"
"""
        result = validate_answer_structure(answer, "BEHAVIORAL")
        assert result["valid"] is True

    def test_empty_answer(self):
        result = validate_answer_structure("", "SPEED")
        assert result["valid"] is False
        assert any("empty" in e.lower() for e in result["errors"])

    def test_invalid_format_type(self):
        result = validate_answer_structure("some answer", "UNKNOWN_FORMAT")
        assert result["valid"] is False
        assert any("format type" in e.lower() for e in result["errors"])

    def test_section_coverage_reporting(self):
        answer = "Fundamental Concept: x=y. Common Trap: watch out."
        result = validate_answer_structure(answer, "SPEED")
        assert isinstance(result["section_coverage"], dict)
        assert result["section_coverage"]["Fundamental Concept"] is True
        assert result["section_coverage"]["Common Trap"] is True


class TestValidateBatchPayload:
    def test_valid_batch(self):
        result = validate_batch_payload([
            {"name": "Trains", "questions": ["Q1 about trains length?"]},
            {"name": "Clocks", "questions": ["Q1 about clock angles?"]},
        ])
        assert result["valid"] is True

    def test_empty_batch(self):
        result = validate_batch_payload([])
        assert result["valid"] is False

    def test_none_batch(self):
        result = validate_batch_payload(None)
        assert result["valid"] is False

    def test_topic_missing_name(self):
        result = validate_batch_payload([{"questions": ["Q1?"]}])
        assert result["valid"] is False
        assert any("name" in e.lower() for e in result["errors"])

    def test_topic_missing_questions(self):
        result = validate_batch_payload([{"name": "Trains"}])
        assert result["valid"] is False
        assert any("questions" in e.lower() for e in result["errors"])
