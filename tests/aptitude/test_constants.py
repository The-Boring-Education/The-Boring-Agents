"""Tests for aptitude constants and topic registry."""

import pytest

from src.agents.aptitude.constants import (
    CATEGORY_SUB_CATEGORY_MAP,
    SUB_CATEGORY_FORMAT_MAP,
    TOPIC_REGISTRY,
    get_format_for_sub_category,
    get_topic_info,
    get_topics_for_sub_category,
    validate_topic_name,
)


class TestSubCategoryFormatMap:
    def test_all_sub_categories_have_format(self):
        expected_subs = {
            "ARITHMETIC_APTITUDE", "DATA_INTERPRETATION",
            "VERBAL_ABILITY", "LOGICAL_REASONING",
            "GD_ROUND", "HR_INTERVIEW",
        }
        assert set(SUB_CATEGORY_FORMAT_MAP.keys()) == expected_subs

    def test_quantitative_uses_speed(self):
        assert SUB_CATEGORY_FORMAT_MAP["ARITHMETIC_APTITUDE"] == "SPEED"
        assert SUB_CATEGORY_FORMAT_MAP["DATA_INTERPRETATION"] == "SPEED"

    def test_verbal_uses_rules(self):
        assert SUB_CATEGORY_FORMAT_MAP["VERBAL_ABILITY"] == "RULES"

    def test_reasoning_uses_speed(self):
        assert SUB_CATEGORY_FORMAT_MAP["LOGICAL_REASONING"] == "SPEED"

    def test_interview_formats(self):
        assert SUB_CATEGORY_FORMAT_MAP["GD_ROUND"] == "PERSPECTIVE"
        assert SUB_CATEGORY_FORMAT_MAP["HR_INTERVIEW"] == "BEHAVIORAL"


class TestCategorySubCategoryMap:
    def test_all_categories_present(self):
        assert set(CATEGORY_SUB_CATEGORY_MAP.keys()) == {
            "QUANTITATIVE", "VERBAL", "REASONING", "INTERVIEW"
        }

    def test_quantitative_has_correct_subs(self):
        subs = CATEGORY_SUB_CATEGORY_MAP["QUANTITATIVE"]
        assert "ARITHMETIC_APTITUDE" in subs
        assert "DATA_INTERPRETATION" in subs

    def test_verbal_has_correct_subs(self):
        assert "VERBAL_ABILITY" in CATEGORY_SUB_CATEGORY_MAP["VERBAL"]

    def test_reasoning_has_correct_subs(self):
        assert "LOGICAL_REASONING" in CATEGORY_SUB_CATEGORY_MAP["REASONING"]

    def test_interview_has_correct_subs(self):
        subs = CATEGORY_SUB_CATEGORY_MAP["INTERVIEW"]
        assert "GD_ROUND" in subs
        assert "HR_INTERVIEW" in subs


class TestTopicRegistry:
    def test_registry_not_empty(self):
        assert len(TOPIC_REGISTRY) > 0

    def test_all_topics_have_required_fields(self):
        for topic in TOPIC_REGISTRY:
            assert "name" in topic, f"Missing 'name' in topic: {topic}"
            assert "category" in topic, f"Missing 'category' in topic: {topic}"
            assert "subCategory" in topic, f"Missing 'subCategory' in topic: {topic}"

    def test_all_categories_valid(self):
        valid_cats = set(CATEGORY_SUB_CATEGORY_MAP.keys())
        for topic in TOPIC_REGISTRY:
            assert topic["category"] in valid_cats, (
                f"Invalid category '{topic['category']}' in topic '{topic['name']}'"
            )

    def test_all_sub_categories_valid(self):
        valid_subs = set(SUB_CATEGORY_FORMAT_MAP.keys())
        for topic in TOPIC_REGISTRY:
            assert topic["subCategory"] in valid_subs, (
                f"Invalid subCategory '{topic['subCategory']}' in topic '{topic['name']}'"
            )

    def test_arithmetic_aptitude_topics_count(self):
        arith_topics = [t for t in TOPIC_REGISTRY if t["subCategory"] == "ARITHMETIC_APTITUDE"]
        assert len(arith_topics) == 24

    def test_data_interpretation_topics_count(self):
        di_topics = [t for t in TOPIC_REGISTRY if t["subCategory"] == "DATA_INTERPRETATION"]
        assert len(di_topics) == 4

    def test_verbal_ability_topics_count(self):
        verbal_topics = [t for t in TOPIC_REGISTRY if t["subCategory"] == "VERBAL_ABILITY"]
        assert len(verbal_topics) == 3

    def test_logical_reasoning_topics_count(self):
        lr_topics = [t for t in TOPIC_REGISTRY if t["subCategory"] == "LOGICAL_REASONING"]
        assert len(lr_topics) == 14

    def test_gd_round_topics_count(self):
        gd_topics = [t for t in TOPIC_REGISTRY if t["subCategory"] == "GD_ROUND"]
        assert len(gd_topics) == 5

    def test_hr_interview_topics_count(self):
        hr_topics = [t for t in TOPIC_REGISTRY if t["subCategory"] == "HR_INTERVIEW"]
        assert len(hr_topics) == 6

    def test_no_duplicate_topic_names(self):
        names = [t["name"] for t in TOPIC_REGISTRY]
        assert len(names) == len(set(names)), "Duplicate topic names found"

    def test_specific_topics_exist(self):
        expected = [
            "Problem on Trains", "Percentage", "Probability",
            "Spotting Errors", "Synonyms",
            "Number Series", "Analogies",
            "Politics", "Self Introduction",
        ]
        topic_names = {t["name"] for t in TOPIC_REGISTRY}
        for name in expected:
            assert name in topic_names, f"Expected topic '{name}' not found"


class TestGetFormatForSubCategory:
    def test_valid_sub_category(self):
        assert get_format_for_sub_category("ARITHMETIC_APTITUDE") == "SPEED"
        assert get_format_for_sub_category("VERBAL_ABILITY") == "RULES"
        assert get_format_for_sub_category("GD_ROUND") == "PERSPECTIVE"
        assert get_format_for_sub_category("HR_INTERVIEW") == "BEHAVIORAL"

    def test_case_insensitive(self):
        assert get_format_for_sub_category("arithmetic_aptitude") == "SPEED"

    def test_invalid_sub_category_raises(self):
        with pytest.raises(ValueError, match="Unknown sub-category"):
            get_format_for_sub_category("INVALID")


class TestGetTopicsForSubCategory:
    def test_returns_correct_topics(self):
        topics = get_topics_for_sub_category("DATA_INTERPRETATION")
        assert len(topics) == 4
        names = [t["name"] for t in topics]
        assert "Table Charts" in names
        assert "Bar Charts" in names

    def test_empty_for_nonexistent(self):
        topics = get_topics_for_sub_category("NONEXISTENT")
        assert topics == []


class TestValidateTopicName:
    def test_existing_topic(self):
        assert validate_topic_name("Problem on Trains") is True

    def test_case_insensitive(self):
        assert validate_topic_name("problem on trains") is True
        assert validate_topic_name("PROBLEM ON TRAINS") is True

    def test_nonexistent_topic(self):
        assert validate_topic_name("Quantum Physics") is False


class TestGetTopicInfo:
    def test_valid_topic(self):
        info = get_topic_info("Problem on Trains")
        assert info["name"] == "Problem on Trains"
        assert info["category"] == "QUANTITATIVE"
        assert info["subCategory"] == "ARITHMETIC_APTITUDE"
        assert info["answerFormatType"] == "SPEED"

    def test_verbal_topic(self):
        info = get_topic_info("Synonyms")
        assert info["category"] == "VERBAL"
        assert info["answerFormatType"] == "RULES"

    def test_gd_topic(self):
        info = get_topic_info("Politics")
        assert info["category"] == "INTERVIEW"
        assert info["answerFormatType"] == "PERSPECTIVE"

    def test_hr_topic(self):
        info = get_topic_info("Self Introduction")
        assert info["category"] == "INTERVIEW"
        assert info["answerFormatType"] == "BEHAVIORAL"

    def test_nonexistent_raises(self):
        with pytest.raises(ValueError, match="Topic not found"):
            get_topic_info("Nonexistent Topic")
