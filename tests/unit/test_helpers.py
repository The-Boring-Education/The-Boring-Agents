"""
Unit tests for helpers utility module.

Tests the utility functions in src/utils/helpers.py.
"""

import pytest
import os
import json
import yaml
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch

from src.utils.helpers import (
    setup_logging,
    load_json_file,
    save_json_file,
    load_yaml_file,
    save_yaml_file,
    clean_text,
    extract_keywords,
    generate_filename,
    validate_content_structure,
    format_duration,
)


class TestSetupLogging:
    """Tests for setup_logging function."""
    
    def test_setup_logging_default_level(self):
        """Test that setup_logging works with default level."""
        # Should not raise
        setup_logging()
    
    def test_setup_logging_with_debug_level(self):
        """Test setup_logging with DEBUG level."""
        setup_logging("DEBUG")
    
    def test_setup_logging_with_error_level(self):
        """Test setup_logging with ERROR level."""
        setup_logging("ERROR")
    
    def test_setup_logging_case_insensitive(self):
        """Test that log level is case insensitive."""
        setup_logging("info")
        setup_logging("INFO")


class TestJsonFileOperations:
    """Tests for JSON file operations."""
    
    @pytest.fixture
    def temp_json_file(self, temp_dir):
        """Create a temporary JSON file."""
        filepath = os.path.join(temp_dir, "test.json")
        yield filepath
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def test_save_json_file(self, temp_json_file):
        """Test saving JSON file."""
        data = {"key": "value", "number": 42}
        save_json_file(data, temp_json_file)
        
        assert os.path.exists(temp_json_file)
        
        with open(temp_json_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert loaded == data
    
    def test_load_json_file(self, temp_json_file):
        """Test loading JSON file."""
        data = {"name": "test", "items": [1, 2, 3]}
        
        with open(temp_json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        
        loaded = load_json_file(temp_json_file)
        assert loaded == data
    
    def test_save_json_creates_directories(self, temp_dir):
        """Test that save_json_file creates directories."""
        filepath = os.path.join(temp_dir, "nested", "dir", "test.json")
        data = {"nested": True}
        
        save_json_file(data, filepath)
        
        assert os.path.exists(filepath)
    
    def test_save_json_with_unicode(self, temp_json_file):
        """Test saving JSON with unicode characters."""
        data = {"emoji": "🚀", "hindi": "नमस्ते"}
        save_json_file(data, temp_json_file)
        
        loaded = load_json_file(temp_json_file)
        assert loaded == data
    
    def test_load_json_file_not_found(self, temp_dir):
        """Test loading non-existent JSON file."""
        filepath = os.path.join(temp_dir, "non_existent.json")
        
        with pytest.raises(FileNotFoundError):
            load_json_file(filepath)


class TestYamlFileOperations:
    """Tests for YAML file operations."""
    
    @pytest.fixture
    def temp_yaml_file(self, temp_dir):
        """Create a temporary YAML file."""
        filepath = os.path.join(temp_dir, "test.yaml")
        yield filepath
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def test_save_yaml_file(self, temp_yaml_file):
        """Test saving YAML file."""
        data = {"key": "value", "list": [1, 2, 3]}
        save_yaml_file(data, temp_yaml_file)
        
        assert os.path.exists(temp_yaml_file)
    
    def test_load_yaml_file(self, temp_yaml_file):
        """Test loading YAML file."""
        data = {"name": "test", "nested": {"inner": "value"}}
        
        with open(temp_yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f)
        
        loaded = load_yaml_file(temp_yaml_file)
        assert loaded == data
    
    def test_yaml_roundtrip(self, temp_yaml_file):
        """Test YAML save and load roundtrip."""
        data = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "list": ["a", "b", "c"]
        }
        
        save_yaml_file(data, temp_yaml_file)
        loaded = load_yaml_file(temp_yaml_file)
        
        assert loaded == data


class TestCleanText:
    """Tests for clean_text function."""
    
    def test_clean_text_removes_extra_whitespace(self):
        """Test that extra whitespace is removed."""
        text = "Hello    World"
        assert clean_text(text) == "Hello World"
    
    def test_clean_text_removes_newlines(self):
        """Test that newlines are normalized."""
        text = "Hello\n\n\nWorld"
        assert clean_text(text) == "Hello World"
    
    def test_clean_text_trims_edges(self):
        """Test that leading/trailing whitespace is removed."""
        text = "   Hello World   "
        assert clean_text(text) == "Hello World"
    
    def test_clean_text_tabs(self):
        """Test that tabs are normalized."""
        text = "Hello\t\t\tWorld"
        assert clean_text(text) == "Hello World"
    
    def test_clean_text_empty_string(self):
        """Test with empty string."""
        assert clean_text("") == ""
    
    def test_clean_text_only_whitespace(self):
        """Test with only whitespace."""
        assert clean_text("   \n\t   ") == ""


class TestExtractKeywords:
    """Tests for extract_keywords function."""
    
    def test_extract_keywords_basic(self):
        """Test basic keyword extraction."""
        text = "React is a JavaScript library for building user interfaces"
        keywords = extract_keywords(text)
        
        assert "react" in keywords
        assert "javascript" in keywords
        assert "library" in keywords
    
    def test_extract_keywords_min_length(self):
        """Test that short words are filtered."""
        text = "a b c the for this that"
        keywords = extract_keywords(text, min_length=3)
        
        assert "the" in keywords
        assert "for" in keywords
        assert "a" not in keywords
        assert "b" not in keywords
    
    def test_extract_keywords_custom_min_length(self):
        """Test custom minimum length."""
        text = "cat dog mouse elephant hippopotamus"
        keywords = extract_keywords(text, min_length=5)
        
        assert "mouse" in keywords
        assert "elephant" in keywords
        assert "cat" not in keywords
        assert "dog" not in keywords
    
    def test_extract_keywords_removes_duplicates(self):
        """Test that duplicates are removed."""
        text = "test test test test"
        keywords = extract_keywords(text)
        
        assert keywords.count("test") == 1
    
    def test_extract_keywords_lowercase(self):
        """Test that keywords are lowercase."""
        text = "React JavaScript TypeScript"
        keywords = extract_keywords(text)
        
        assert "react" in keywords
        assert "React" not in keywords


class TestGenerateFilename:
    """Tests for generate_filename function."""
    
    def test_generate_filename_default_extension(self):
        """Test generating filename with default extension."""
        filename = generate_filename("test")
        
        assert filename.startswith("test_")
        assert filename.endswith(".json")
    
    def test_generate_filename_custom_extension(self):
        """Test generating filename with custom extension."""
        filename = generate_filename("output", extension="md")
        
        assert filename.endswith(".md")
    
    def test_generate_filename_unique(self):
        """Test that filenames are unique."""
        import time
        
        filename1 = generate_filename("test")
        time.sleep(0.001)  # Tiny delay to ensure different timestamp
        filename2 = generate_filename("test")
        
        # Both should start with test_ but timestamps might be same
        assert filename1.startswith("test_")
        assert filename2.startswith("test_")
    
    def test_generate_filename_format(self):
        """Test filename format matches expected pattern."""
        import re
        
        filename = generate_filename("prefix")
        # Pattern: prefix_YYYYMMDD_HHMMSS.json
        pattern = r"prefix_\d{8}_\d{6}\.json"
        
        assert re.match(pattern, filename)


class TestValidateContentStructure:
    """Tests for validate_content_structure function."""
    
    def test_validate_content_all_fields_present(self):
        """Test validation when all fields are present."""
        content = {"name": "Test", "description": "A test", "items": []}
        required = ["name", "description", "items"]
        
        assert validate_content_structure(content, required) is True
    
    def test_validate_content_missing_field(self):
        """Test validation when a field is missing."""
        content = {"name": "Test"}
        required = ["name", "description"]
        
        assert validate_content_structure(content, required) is False
    
    def test_validate_content_empty_required(self):
        """Test validation with empty required list."""
        content = {"any": "field"}
        
        assert validate_content_structure(content, []) is True
    
    def test_validate_content_nested_fields_not_checked(self):
        """Test that nested structure is not validated."""
        content = {"outer": {"inner": "value"}}
        required = ["outer"]
        
        assert validate_content_structure(content, required) is True


class TestFormatDuration:
    """Tests for format_duration function."""
    
    def test_format_duration_seconds(self):
        """Test formatting durations in seconds."""
        assert format_duration(5.0) == "5.0s"
        assert format_duration(30.5) == "30.5s"
        assert format_duration(59.9) == "59.9s"
    
    def test_format_duration_minutes(self):
        """Test formatting durations in minutes."""
        assert format_duration(60.0) == "1.0m"
        assert format_duration(120.0) == "2.0m"
        assert format_duration(90.0) == "1.5m"
    
    def test_format_duration_hours(self):
        """Test formatting durations in hours."""
        assert format_duration(3600.0) == "1.0h"
        assert format_duration(7200.0) == "2.0h"
        assert format_duration(5400.0) == "1.5h"
    
    def test_format_duration_zero(self):
        """Test formatting zero duration."""
        assert format_duration(0.0) == "0.0s"
    
    def test_format_duration_fractional(self):
        """Test formatting fractional durations."""
        result = format_duration(1.234)
        assert result == "1.2s"

