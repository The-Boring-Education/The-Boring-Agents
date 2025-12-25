"""
Unit tests for quiz metadata generator.

Tests the QuizMetadataGenerator class.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.quiz.generators.metadata_generator import QuizMetadataGenerator


class TestQuizMetadataGeneratorInit:
    """Tests for QuizMetadataGenerator initialization."""
    
    def test_initialization(self):
        """Test that generator can be initialized."""
        generator = QuizMetadataGenerator()
        assert generator is not None
    
    def test_has_prompt_templates(self):
        """Test that generator has prompt templates."""
        generator = QuizMetadataGenerator()
        templates = generator._get_prompt_templates()
        
        assert isinstance(templates, dict)
        assert "generate_category_metadata" in templates


class TestQuizMetadataGeneratorGeneration:
    """Tests for metadata generation."""
    
    @pytest.fixture
    def generator(self):
        """Create a metadata generator."""
        return QuizMetadataGenerator()
    
    @patch.object(QuizMetadataGenerator, '_generate_with_prompt')
    def test_generate_category_metadata_success(self, mock_generate, generator):
        """Test successful metadata generation."""
        mock_generate.return_value = '''
        {
            "categoryName": "React.js Quiz",
            "categoryDescription": "Test your React knowledge with this comprehensive quiz.",
            "categoryIcon": "⚛️"
        }
        '''
        
        result = generator.generate_category_metadata(
            topic="React.js",
            question_count=20,
            target_audience="developers"
        )
        
        assert result["categoryName"] == "React.js Quiz"
        assert "React" in result["categoryDescription"]
        assert result["categoryIcon"] == "⚛️"
    
    @patch.object(QuizMetadataGenerator, '_generate_with_prompt')
    def test_generate_category_metadata_fallback(self, mock_generate, generator):
        """Test fallback when generation fails."""
        mock_generate.return_value = "Invalid JSON response"
        
        result = generator.generate_category_metadata(
            topic="Python",
            question_count=10
        )
        
        # Should fall back to defaults
        assert result["categoryName"] == "Python"
        assert "Python" in result["categoryDescription"]
        assert result["categoryIcon"] is not None
    
    def test_generate_content_method(self, generator):
        """Test generate_content wrapper method."""
        with patch.object(generator, 'generate_category_metadata') as mock_gen:
            mock_gen.return_value = {"categoryName": "Test"}
            
            result = generator.generate_content(
                "generate_category_metadata",
                topic="Test",
                question_count=10
            )
            
            mock_gen.assert_called_once()
    
    def test_generate_content_invalid_type(self, generator):
        """Test generate_content with invalid type raises error."""
        with pytest.raises(ValueError):
            generator.generate_content("invalid_type", topic="Test")


class TestQuizMetadataGeneratorParsing:
    """Tests for JSON parsing."""
    
    @pytest.fixture
    def generator(self):
        """Create a metadata generator."""
        return QuizMetadataGenerator()
    
    def test_parse_json_response_valid(self, generator):
        """Test parsing valid JSON."""
        response = '{"categoryName": "Test", "categoryIcon": "🎯"}'
        result = generator._parse_json_response(response)
        
        assert result["categoryName"] == "Test"
        assert result["categoryIcon"] == "🎯"
    
    def test_parse_json_response_with_text(self, generator):
        """Test parsing JSON embedded in text."""
        response = '''
        Here is the metadata:
        {"categoryName": "Test Quiz", "categoryDescription": "A test", "categoryIcon": "📝"}
        Hope this helps!
        '''
        result = generator._parse_json_response(response)
        
        assert result["categoryName"] == "Test Quiz"
    
    def test_parse_json_response_invalid(self, generator):
        """Test parsing invalid JSON returns None."""
        response = "This is not JSON at all"
        result = generator._parse_json_response(response)
        
        assert result is None
    
    def test_parse_json_response_empty(self, generator):
        """Test parsing empty response returns None."""
        result = generator._parse_json_response("")
        
        assert result is None


class TestQuizMetadataGeneratorValidation:
    """Tests for metadata validation."""
    
    @pytest.fixture
    def generator(self):
        """Create a metadata generator."""
        return QuizMetadataGenerator()
    
    def test_validate_metadata_complete(self, generator):
        """Test validating complete metadata."""
        metadata = {
            "categoryName": "Test Quiz",
            "categoryDescription": "A description",
            "categoryIcon": "🎯"
        }
        result = generator._validate_metadata(metadata, "Test")
        
        assert result["categoryName"] == "Test Quiz"
        assert result["categoryDescription"] == "A description"
        assert result["categoryIcon"] == "🎯"
    
    def test_validate_metadata_missing_name(self, generator):
        """Test validating metadata with missing name."""
        metadata = {
            "categoryDescription": "A description",
            "categoryIcon": "🎯"
        }
        result = generator._validate_metadata(metadata, "React")
        
        assert result["categoryName"] == "React"
    
    def test_validate_metadata_missing_description(self, generator):
        """Test validating metadata with missing description."""
        metadata = {
            "categoryName": "Test",
            "categoryIcon": "🎯"
        }
        result = generator._validate_metadata(metadata, "Python")
        
        assert "Python" in result["categoryDescription"]
    
    def test_validate_metadata_missing_icon(self, generator):
        """Test validating metadata with missing icon."""
        metadata = {
            "categoryName": "Test",
            "categoryDescription": "Description"
        }
        result = generator._validate_metadata(metadata, "React")
        
        assert result["categoryIcon"] is not None
    
    def test_validate_metadata_truncates_long_name(self, generator):
        """Test that long names are truncated."""
        metadata = {
            "categoryName": "A" * 150,  # Too long
            "categoryDescription": "Test",
            "categoryIcon": "🎯"
        }
        result = generator._validate_metadata(metadata, "Test")
        
        assert len(result["categoryName"]) <= 100
    
    def test_validate_metadata_truncates_long_description(self, generator):
        """Test that long descriptions are truncated."""
        metadata = {
            "categoryName": "Test",
            "categoryDescription": "A" * 600,  # Too long
            "categoryIcon": "🎯"
        }
        result = generator._validate_metadata(metadata, "Test")
        
        assert len(result["categoryDescription"]) <= 500


class TestQuizMetadataGeneratorDefaultIcons:
    """Tests for default icon selection."""
    
    @pytest.fixture
    def generator(self):
        """Create a metadata generator."""
        return QuizMetadataGenerator()
    
    def test_default_icon_react(self, generator):
        """Test default icon for React topic."""
        icon = generator._get_default_icon("React.js")
        assert icon == "⚛️"
    
    def test_default_icon_javascript(self, generator):
        """Test default icon for JavaScript topic."""
        icon = generator._get_default_icon("JavaScript Basics")
        assert icon == "🟨"
    
    def test_default_icon_python(self, generator):
        """Test default icon for Python topic."""
        icon = generator._get_default_icon("Python Programming")
        assert icon == "🐍"
    
    def test_default_icon_node(self, generator):
        """Test default icon for Node.js topic."""
        icon = generator._get_default_icon("Node.js")
        assert icon == "🟩"
    
    def test_default_icon_unknown(self, generator):
        """Test default icon for unknown topic."""
        icon = generator._get_default_icon("Unknown Topic XYZ")
        assert icon == "📝"
    
    def test_default_icon_case_insensitive(self, generator):
        """Test that icon matching is case insensitive."""
        icon1 = generator._get_default_icon("REACT")
        icon2 = generator._get_default_icon("react")
        icon3 = generator._get_default_icon("React")
        
        assert icon1 == icon2 == icon3 == "⚛️"


class TestQuizMetadataGeneratorDefaults:
    """Tests for default metadata generation."""
    
    @pytest.fixture
    def generator(self):
        """Create a metadata generator."""
        return QuizMetadataGenerator()
    
    def test_get_default_metadata(self, generator):
        """Test getting default metadata."""
        result = generator._get_default_metadata("JavaScript")
        
        assert result["categoryName"] == "JavaScript"
        assert "JavaScript" in result["categoryDescription"]
        assert result["categoryIcon"] == "🟨"
    
    def test_get_default_metadata_has_all_fields(self, generator):
        """Test that default metadata has all required fields."""
        result = generator._get_default_metadata("Test Topic")
        
        assert "categoryName" in result
        assert "categoryDescription" in result
        assert "categoryIcon" in result

