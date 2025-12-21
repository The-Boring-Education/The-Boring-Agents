"""Unit tests for answer generators."""

import pytest
from unittest.mock import Mock, patch

from src.agents.interview.generators.generic_generator import GenericAnswerGenerator
from src.agents.interview.generators.dsa_generator import DSAAnswerGenerator
from src.agents.interview.generators.tech_generator import TechAnswerGenerator
from src.agents.interview.generators.system_design_generator import SystemDesignAnswerGenerator


class TestGenericGenerator:
    """Tests for GenericAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = GenericAnswerGenerator()
        assert generator is not None
        assert hasattr(generator, 'generate_answer')
    
    def test_get_answer_structure(self):
        """Test answer structure is defined."""
        generator = GenericAnswerGenerator()
        structure = generator._get_answer_structure()
        assert isinstance(structure, dict)
        assert len(structure) > 0


class TestDSAGenerator:
    """Tests for DSAAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = DSAAnswerGenerator()
        assert generator is not None
    
    def test_get_answer_structure(self):
        """Test answer structure includes DSA-specific sections."""
        generator = DSAAnswerGenerator()
        structure = generator._get_answer_structure()
        assert "Introduction" in structure
        assert "Time & Space Complexity" in structure


class TestTechGenerator:
    """Tests for TechAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = TechAnswerGenerator(technology="Python")
        assert generator is not None
        assert generator.technology == "Python"
    
    def test_get_answer_structure(self):
        """Test answer structure includes tech-specific sections."""
        generator = TechAnswerGenerator()
        structure = generator._get_answer_structure()
        assert "Practical Implementation" in structure


class TestSystemDesignGenerator:
    """Tests for SystemDesignAnswerGenerator."""
    
    def test_generator_initialization(self):
        """Test generator can be initialized."""
        generator = SystemDesignAnswerGenerator()
        assert generator is not None
    
    def test_get_answer_structure(self):
        """Test answer structure includes system design sections."""
        generator = SystemDesignAnswerGenerator()
        structure = generator._get_answer_structure()
        assert "System Architecture Overview" in structure
        assert "Scalability" in structure

