"""Unit tests for schema utilities."""

import pytest

from src.agents.interview.common.schema_utils import (
    generate_slug,
    generate_cover_image_url,
    validate_roadmap,
    validate_frequency,
    validate_priority,
    validate_company_types,
    validate_sheet_structure,
    validate_question_structure,
    ROADMAPS,
    INTERVIEW_QUESTION_FREQUENCY,
    PRIORITY_LEVELS,
    COMPANY_TYPES
)


class TestSchemaUtils:
    """Tests for schema utilities."""
    
    def test_generate_slug(self):
        """Test slug generation."""
        slug = generate_slug("Test Interview Sheet")
        assert slug == "test-interview-sheet"
        assert "-" in slug
        assert slug.islower()
    
    def test_generate_cover_image_url(self):
        """Test cover image URL generation."""
        url = generate_cover_image_url("Python")
        assert url.startswith("https://")
        assert "unsplash" in url or "images" in url
    
    def test_validate_roadmap(self):
        """Test roadmap validation."""
        assert validate_roadmap("Tech") is True
        assert validate_roadmap("Frontend") is True
        assert validate_roadmap("Invalid") is False
    
    def test_validate_frequency(self):
        """Test frequency validation."""
        assert validate_frequency("Most Asked") is True
        assert validate_frequency("Asked Frequently") is True
        assert validate_frequency("Invalid") is False
    
    def test_validate_priority(self):
        """Test priority validation."""
        assert validate_priority("High") is True
        assert validate_priority("Medium") is True
        assert validate_priority("Invalid") is False
    
    def test_validate_company_types(self):
        """Test company types validation."""
        assert validate_company_types(["Startup", "MNC"]) is True
        assert validate_company_types(["Invalid"]) is False
        assert validate_company_types([]) is True
    
    def test_validate_sheet_structure(self):
        """Test sheet structure validation."""
        valid_sheet = {
            "name": "Test Sheet",
            "slug": "test-sheet",
            "description": "Test Description",
            "coverImageURL": "https://example.com/image.jpg",
            "liveOn": "2024-01-01T00:00:00.000Z",
            "roadmap": "Tech",
            "questions": []
        }
        
        is_valid, errors = validate_sheet_structure(valid_sheet)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_question_structure(self):
        """Test question structure validation."""
        valid_question = {
            "title": "Test Question",
            "question": "What is Python?",
            "answer": "Python is a programming language",
            "frequency": "Asked Sometimes",
            "priority": "Medium",
            "companyTypes": ["Startup"]
        }
        
        errors = validate_question_structure(valid_question)
        assert len(errors) == 0

