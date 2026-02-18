"""Comprehensive unit tests for answer generators."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.interview.generators.generic_generator import GenericAnswerGenerator
from src.agents.interview.generators.dsa_generator import DSAAnswerGenerator
from src.agents.interview.generators.tech_generator import TechAnswerGenerator
from src.agents.interview.generators.system_design_generator import SystemDesignAnswerGenerator


class TestGenericGenerator:
    """Comprehensive tests for GenericAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = GenericAnswerGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_answer')
        assert hasattr(generator, '_get_answer_prompt_template')
        assert hasattr(generator, '_get_answer_structure')
    
    def test_get_answer_structure(self):
        """Test answer structure is defined correctly."""
        generator = GenericAnswerGenerator()
        structure = generator._get_answer_structure()
        assert isinstance(structure, dict)
        assert len(structure) > 0
        assert "Quick Answer" in structure
        assert "Introduction" in structure
    
    def test_get_answer_prompt_template(self):
        """Test prompt template is properly configured."""
        generator = GenericAnswerGenerator()
        template = generator._get_answer_prompt_template()
        assert template is not None
        assert hasattr(template, 'format')
        
        # Check that all required variables are present
        input_vars = template.input_variables
        assert "question" in input_vars
        assert "topic" in input_vars
        assert "difficulty" in input_vars
    
    @patch('src.agents.interview.generators.base_generator.BaseAnswerGenerator._generate_with_prompt')
    @patch('src.agents.interview.generators.base_generator.format_answer_as_mdx')
    def test_generate_answer_success(self, mock_mdx_format, mock_generate):
        """Test successful answer generation."""
        mock_generate.return_value = "Test answer content"
        mock_mdx_format.return_value = "Formatted MDX answer"
        
        generator = GenericAnswerGenerator()
        result = generator.generate_answer(
            question="What is Python?",
            topic="Programming Languages",
            difficulty="Medium",
            frequency="Asked Sometimes",
            priority="Medium",
            company_types=["Startup", "MNC"]
        )
        
        assert result == "Formatted MDX answer"
        mock_mdx_format.assert_called_once()
    
    def test_generate_answer_with_defaults(self):
        """Test answer generation with default parameters."""
        generator = GenericAnswerGenerator()
        
        # Should not raise with defaults
        with patch.object(generator, '_generate_with_prompt', return_value="Test"):
            with patch('src.agents.interview.generators.base_generator.format_answer_as_mdx', return_value="Test"):
                result = generator.generate_answer(
                    question="Test question",
                    topic="Test topic"
                )
                assert result == "Test"
    
    def test_quality_improvements_applied(self):
        """Test that quality improvements are applied."""
        generator = GenericAnswerGenerator()
        
        # Mock the generation to return incomplete answer
        with patch.object(generator, '_generate_with_prompt', return_value="Incomplete answer"):
            with patch.object(generator, '_apply_quality_improvements') as mock_improve:
                with patch('src.agents.interview.generators.base_generator.format_answer_as_mdx', return_value="Improved"):
                    generator.generate_answer(
                        question="Test",
                        topic="Test"
                    )
                    mock_improve.assert_called_once()


class TestDSAGenerator:
    """Comprehensive tests for DSAAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = DSAAnswerGenerator()
        assert generator is not None
    
    def test_get_answer_structure(self):
        """Test answer structure includes DSA-specific sections."""
        generator = DSAAnswerGenerator()
        structure = generator._get_answer_structure()
        assert isinstance(structure, dict)
        assert "Introduction" in structure
        assert "Time & Space Complexity" in structure or "Complexity" in structure
    
    def test_get_answer_prompt_template(self):
        """Test prompt template includes DSA-specific instructions."""
        generator = DSAAnswerGenerator()
        template = generator._get_answer_prompt_template()
        assert template is not None
        
        # Format template to check content
        formatted = template.format(
            question="Test question",
            topic="DSA",
            difficulty="Medium",
            frequency="Asked Sometimes",
            priority="Medium",
            company_types="Startup, MNC"
        )
        assert "DSA" in formatted or "algorithm" in formatted.lower() or "data structure" in formatted.lower()


class TestTechGenerator:
    """Comprehensive tests for TechAnswerGenerator."""
    
    def test_generator_initialization_with_technology(self):
        """Test generator can be initialized with technology."""
        generator = TechAnswerGenerator(technology="Python")
        assert generator is not None
        assert hasattr(generator, 'technology')
        assert generator.technology == "Python"
    
    def test_generator_initialization_without_technology(self):
        """Test generator can be initialized without technology."""
        generator = TechAnswerGenerator()
        assert generator is not None
    
    def test_get_answer_structure(self):
        """Test answer structure includes tech-specific sections."""
        generator = TechAnswerGenerator()
        structure = generator._get_answer_structure()
        assert isinstance(structure, dict)
        assert "Practical Implementation" in structure or "Code" in str(structure)
    
    def test_technology_in_prompt(self):
        """Test that technology is included in prompt when provided."""
        generator = TechAnswerGenerator(technology="React")
        template = generator._get_answer_prompt_template()
        
        formatted = template.format(
            question="Test",
            topic="React",
            difficulty="Medium",
            frequency="Asked Sometimes",
            priority="Medium",
            company_types="Startup"
        )
        # Technology should be mentioned in the prompt
        assert "React" in formatted or "react" in formatted.lower()


class TestSystemDesignGenerator:
    """Comprehensive tests for SystemDesignAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = SystemDesignAnswerGenerator()
        assert generator is not None
    
    def test_get_answer_structure(self):
        """Test answer structure includes system design sections."""
        generator = SystemDesignAnswerGenerator()
        structure = generator._get_answer_structure()
        assert isinstance(structure, dict)
        # Should have system design specific sections
        assert any(keyword in str(structure).lower() for keyword in ["system", "architecture", "scalability", "design"])
    
    def test_get_answer_prompt_template(self):
        """Test prompt template includes system design instructions."""
        generator = SystemDesignAnswerGenerator()
        template = generator._get_answer_prompt_template()
        assert template is not None
        
        formatted = template.format(
            question="Design a system",
            topic="System Design",
            difficulty="Hard",
            frequency="Asked Frequently",
            priority="High",
            company_types="FAANG"
        )
        assert "system" in formatted.lower() or "design" in formatted.lower() or "architecture" in formatted.lower()


class TestGeneratorCommon:
    """Tests for common generator functionality."""
    
    @pytest.mark.parametrize("generator_class", [
        GenericAnswerGenerator,
        DSAAnswerGenerator,
        TechAnswerGenerator,
        SystemDesignAnswerGenerator
    ])
    def test_all_generators_have_required_methods(self, generator_class):
        """Test that all generators implement required methods."""
        generator = generator_class()
        assert hasattr(generator, 'generate_answer')
        assert hasattr(generator, '_get_answer_prompt_template')
        assert hasattr(generator, '_get_answer_structure')
    
    @pytest.mark.parametrize("generator_class", [
        GenericAnswerGenerator,
        DSAAnswerGenerator,
        TechAnswerGenerator,
        SystemDesignAnswerGenerator
    ])
    def test_all_generators_return_mdx(self, generator_class):
        """Test that all generators return MDX-formatted answers."""
        generator = generator_class()
        
        with patch.object(generator, '_generate_with_prompt', return_value="Raw answer"):
            with patch('src.agents.interview.generators.base_generator.format_answer_as_mdx') as mock_mdx:
                mock_mdx.return_value = "MDX formatted"
                
                result = generator.generate_answer(
                    question="Test",
                    topic="Test"
                )
                
                assert result == "MDX formatted"
                mock_mdx.assert_called_once()
    
    def test_error_handling_in_generation(self):
        """Test that errors are properly handled during generation."""
        generator = GenericAnswerGenerator()
        
        with patch.object(generator, '_generate_with_prompt', side_effect=Exception("API Error")):
            with pytest.raises(Exception):
                generator.generate_answer(
                    question="Test",
                    topic="Test"
                )

