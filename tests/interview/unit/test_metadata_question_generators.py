"""Unit tests for metadata and question generators."""

import pytest
from unittest.mock import Mock, patch

from src.agents.interview.common.metadata_generator import MetadataGenerator
from src.agents.interview.common.question_generator import QuestionGenerator


class TestMetadataGenerator:
    """Tests for MetadataGenerator."""
    
    def test_initialization(self):
        """Test metadata generator can be initialized."""
        generator = MetadataGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_sheet_meta')
        assert hasattr(generator, 'generate_question_metadata')
    
    def test_get_prompt_templates(self):
        """Test prompt templates are defined."""
        generator = MetadataGenerator()
        templates = generator._get_prompt_templates()
        assert isinstance(templates, dict)
        assert "sheet_meta" in templates
        assert "question_metadata" in templates
    
    @patch('src.agents.interview.common.metadata_generator.MetadataGenerator._generate_with_prompt')
    def test_generate_sheet_meta(self, mock_generate):
        """Test sheet metadata generation."""
        mock_generate.return_value = "Generated metadata content"
        
        generator = MetadataGenerator()
        result = generator.generate_sheet_meta(
            name="Test Sheet",
            description="Test Description",
            roadmap="Tech"
        )
        
        assert result == "Generated metadata content"
        mock_generate.assert_called_once()
        
        # Check that prompt includes required fields
        call_args = mock_generate.call_args[0][0]
        assert "Test Sheet" in call_args
        assert "Test Description" in call_args
        assert "Tech" in call_args
    
    @patch('src.agents.interview.common.metadata_generator.MetadataGenerator._generate_with_prompt')
    def test_generate_question_metadata(self, mock_generate):
        """Test question metadata generation."""
        mock_generate.return_value = """
        Frequency: Asked Frequently
        Priority: High
        Company Types: FAANG, MNC
        """
        
        generator = MetadataGenerator()
        result = generator.generate_question_metadata(
            question="What is Python?",
            topic="Programming Languages",
            context="Basic concepts"
        )
        
        assert isinstance(result, dict)
        assert "frequency" in result
        assert "priority" in result
        assert "companyTypes" in result
        assert result["frequency"] == "Asked Frequently"
        assert result["priority"] == "High"
        assert "FAANG" in result["companyTypes"]
        assert "MNC" in result["companyTypes"]
    
    def test_parse_metadata_result(self):
        """Test metadata parsing from AI response."""
        generator = MetadataGenerator()
        
        result_text = """
        Frequency: Most Asked
        Priority: High
        Company Types: Startup, MNC, FAANG
        """
        
        metadata = generator._parse_metadata_result(result_text)
        
        assert metadata["frequency"] == "Most Asked"
        assert metadata["priority"] == "High"
        assert len(metadata["companyTypes"]) > 0
    
    def test_parse_metadata_with_defaults(self):
        """Test metadata parsing with defaults when values are invalid."""
        generator = MetadataGenerator()
        
        result_text = """
        Frequency: Invalid Value
        Priority: Also Invalid
        Company Types: Invalid, Also Invalid
        """
        
        metadata = generator._parse_metadata_result(result_text)
        
        # Should fall back to defaults
        assert metadata["frequency"] == "Asked Sometimes"
        assert metadata["priority"] == "Medium"
        assert metadata["companyTypes"] == ["Startup", "MNC"]
    
    def test_validate_metadata_values(self):
        """Test that metadata values are validated."""
        generator = MetadataGenerator()
        
        with patch.object(generator, '_generate_with_prompt', return_value="Invalid metadata"):
            with patch.object(generator, '_parse_metadata_result') as mock_parse:
                mock_parse.return_value = {
                    "frequency": "Invalid",
                    "priority": "Invalid",
                    "companyTypes": ["Invalid"]
                }
                
                result = generator.generate_question_metadata(
                    question="Test",
                    topic="Test"
                )
                
                # Should have validated values
                assert result["frequency"] in ["Most Asked", "Asked Frequently", "Asked Sometimes"]
                assert result["priority"] in ["High", "Medium", "Low"]
                assert all(ct in ["Startup", "MidSize", "MNC", "FAANG"] for ct in result["companyTypes"])


class TestQuestionGenerator:
    """Tests for QuestionGenerator."""
    
    def test_initialization(self):
        """Test question generator can be initialized."""
        generator = QuestionGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_questions')
    
    def test_get_prompt_templates(self):
        """Test prompt templates are defined."""
        generator = QuestionGenerator()
        templates = generator._get_prompt_templates()
        assert isinstance(templates, dict)
        assert "generate_questions" in templates
    
    @patch('src.agents.interview.common.question_generator.QuestionGenerator._generate_with_prompt')
    def test_generate_questions(self, mock_generate):
        """Test question generation."""
        mock_generate.return_value = """
        1. What is Python?
        2. How does Python handle memory management?
        3. Explain Python's GIL.
        """
        
        generator = QuestionGenerator()
        result = generator.generate_questions(
            name="Python Basics",
            description="Basic Python concepts",
            agent_type="generic",
            question_count=3,
            roadmap="Tech"
        )
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert "Python" in result[0]
        mock_generate.assert_called_once()
        
        # Check that prompt includes required fields
        call_args = mock_generate.call_args[0][0]
        assert "Python Basics" in call_args
        assert "Basic Python concepts" in call_args
        assert "generic" in call_args
    
    def test_parse_questions(self):
        """Test question parsing from generated text."""
        generator = QuestionGenerator()
        
        questions_text = """
        1. What is Python?
        2. How does memory work?
        3. Explain the concept.
        """
        
        questions = generator._parse_questions(questions_text, max_questions=3)
        
        assert len(questions) == 3
        assert "Python" in questions[0]
        assert "memory" in questions[1]
    
    def test_parse_questions_with_bullets(self):
        """Test parsing questions with bullet points."""
        generator = QuestionGenerator()
        
        questions_text = """
        - What is Python?
        - How does memory work?
        - Explain the concept.
        """
        
        questions = generator._parse_questions(questions_text, max_questions=3)
        
        assert len(questions) == 3
        assert "Python" in questions[0]
    
    def test_parse_questions_limits_count(self):
        """Test that question parsing respects max count."""
        generator = QuestionGenerator()
        
        questions_text = """
        1. Question 1
        2. Question 2
        3. Question 3
        4. Question 4
        5. Question 5
        """
        
        questions = generator._parse_questions(questions_text, max_questions=3)
        
        assert len(questions) == 3
    
    def test_parse_questions_filters_short(self):
        """Test that very short questions are filtered out."""
        generator = QuestionGenerator()
        
        questions_text = """
        1. What is Python?
        2. Hi
        3. How does memory work?
        """
        
        questions = generator._parse_questions(questions_text, max_questions=10)
        
        # "Hi" should be filtered out (too short)
        assert len(questions) >= 2
        assert all(len(q) > 10 for q in questions)
    
    def test_generate_questions_with_different_agent_types(self):
        """Test question generation for different agent types."""
        generator = QuestionGenerator()
        
        agent_types = ["generic", "dsa", "tech", "system_design"]
        
        for agent_type in agent_types:
            with patch.object(generator, '_generate_with_prompt', return_value="1. Test question"):
                result = generator.generate_questions(
                    name="Test",
                    description="Test",
                    agent_type=agent_type,
                    question_count=1,
                    roadmap="Tech"
                )
                
                assert isinstance(result, list)
                assert len(result) > 0
    
    def test_generate_questions_with_different_roadmaps(self):
        """Test question generation for different roadmaps."""
        generator = QuestionGenerator()
        
        roadmaps = ["Frontend", "Backend", "Fullstack", "Tech"]
        
        for roadmap in roadmaps:
            with patch.object(generator, '_generate_with_prompt', return_value="1. Test question"):
                result = generator.generate_questions(
                    name="Test",
                    description="Test",
                    agent_type="generic",
                    question_count=1,
                    roadmap=roadmap
                )
                
                assert isinstance(result, list)
                assert len(result) > 0

