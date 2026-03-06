"""Tests for aptitude answer generators."""

import pytest
from unittest.mock import patch, Mock, MagicMock

from src.agents.aptitude.generators import (
    AptitudeAnswerGenerator,
    get_aptitude_generator,
)


class TestAptitudeAnswerGenerator:
    def test_valid_format_types(self):
        for fmt in ["SPEED", "RULES", "PERSPECTIVE", "BEHAVIORAL"]:
            gen = get_aptitude_generator(fmt)
            assert gen.format_type == fmt

    def test_case_insensitive_format(self):
        gen = get_aptitude_generator("speed")
        assert gen.format_type == "SPEED"

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError, match="Invalid format_type"):
            get_aptitude_generator("INVALID")

    @patch.object(AptitudeAnswerGenerator, "_generate_with_prompt")
    def test_generate_answer_calls_llm(self, mock_gen):
        mock_gen.return_value = (
            "##### 📘 Fundamental Concept\nSpeed formula.\n"
            "##### 🧱 The Conventional Method\nStep by step.\n"
            "##### ⚡ The \"Pro\" Shortcut (Trick)\nQuick trick.\n"
            "##### ⚠️ Common Trap\nWatch out.\n"
            "##### ⏱️ Time-Saving Tip\nEliminate options."
        )

        gen = get_aptitude_generator("SPEED")
        answer = gen.generate_answer(
            question="What is 20% of 500?",
            topic="Percentage",
            sub_category="ARITHMETIC_APTITUDE",
        )

        assert mock_gen.called
        assert "Fundamental Concept" in answer
        assert len(answer) > 0

    @patch.object(AptitudeAnswerGenerator, "_generate_with_prompt")
    def test_generate_content_method(self, mock_gen):
        mock_gen.return_value = "Complete answer with all sections: Context, Grammar Rule, Why others are wrong, Vocabulary Bridge"

        gen = get_aptitude_generator("RULES")
        result = gen.generate_content(
            content_type="answer",
            question="Find the error",
            topic="Spotting Errors",
            sub_category="VERBAL_ABILITY",
        )

        assert result["status"] == "success"
        assert result["format_type"] == "RULES"
        assert "answer" in result

    def test_generate_content_invalid_type(self):
        gen = get_aptitude_generator("SPEED")
        with pytest.raises(ValueError, match="Unknown content type"):
            gen.generate_content(content_type="invalid")

    @patch.object(AptitudeAnswerGenerator, "_generate_with_prompt")
    def test_quality_check_patches_missing_sections(self, mock_gen):
        mock_gen.side_effect = [
            "##### 📘 Fundamental Concept\nBasic rule.",
            "##### 🧱 Conventional Method\nStep by step.",
            "##### ⚡ Pro Shortcut\nQuick trick.",
            "##### ⚠️ Common Trap\nWatch out.",
            "##### ⏱️ Time-Saving Tip\nEliminate.",
        ]

        gen = get_aptitude_generator("SPEED")
        answer = gen.generate_answer(
            question="Calculate interest",
            topic="Simple Interest",
            sub_category="ARITHMETIC_APTITUDE",
        )

        assert mock_gen.call_count > 1


class TestGetAptitudeGenerator:
    def test_returns_generator_instance(self):
        gen = get_aptitude_generator("SPEED")
        assert isinstance(gen, AptitudeAnswerGenerator)

    def test_all_format_types(self):
        for fmt in ["SPEED", "RULES", "PERSPECTIVE", "BEHAVIORAL"]:
            gen = get_aptitude_generator(fmt)
            assert gen.format_type == fmt
