"""Utility functions for The Boring Agents."""

import logging
import json
import yaml
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import re


def setup_logging(log_level: str = "INFO") -> None:
    """Setup logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def load_json_file(filepath: str) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Parsed JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], filepath: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save the file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_yaml_file(filepath: str) -> Dict[str, Any]:
    """Load data from a YAML file.
    
    Args:
        filepath: Path to the YAML file
        
    Returns:
        Parsed YAML data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_yaml_file(data: Dict[str, Any], filepath: str) -> None:
    """Save data to a YAML file.
    
    Args:
        data: Data to save
        filepath: Path to save the file
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, indent=2, allow_unicode=True)


def clean_text(text: str) -> str:
    """Clean and normalize text content.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """Extract keywords from text.
    
    Args:
        text: Text to extract keywords from
        min_length: Minimum length of keywords
        
    Returns:
        List of extracted keywords
    """
    # Simple keyword extraction (can be enhanced with NLP libraries)
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    keywords = [word for word in words if len(word) >= min_length]
    return list(set(keywords))  # Remove duplicates


def generate_filename(prefix: str, extension: str = "json") -> str:
    """Generate a timestamped filename.
    
    Args:
        prefix: Prefix for the filename
        extension: File extension (without dot)
        
    Returns:
        Generated filename
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"


def validate_content_structure(content: Dict[str, Any], required_fields: List[str]) -> bool:
    """Validate that content has required fields.
    
    Args:
        content: Content to validate
        required_fields: List of required field names
        
    Returns:
        True if all required fields are present
    """
    return all(field in content for field in required_fields)


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"