"""Schema utilities for interview sheet generation matching Mongoose schema."""

from typing import List, Optional, Dict, Any
from slugify import slugify


# Schema constants matching TypeScript enums
ROADMAPS: List[str] = ["Frontend", "Backend", "Fullstack", "Tech"]
INTERVIEW_QUESTION_FREQUENCY: List[str] = ["Most Asked", "Asked Frequently", "Asked Sometimes"]
PRIORITY_LEVELS: List[str] = ["High", "Medium", "Low"]
COMPANY_TYPES: List[str] = ["Startup", "MidSize", "MNC", "FAANG"]


def generate_slug(name: str) -> str:
    """Generate slug from name using python-slugify.
    
    Args:
        name: Sheet name
        
    Returns:
        Slugified string
    """
    return slugify(name, lowercase=True)


def generate_cover_image_url(topic: Optional[str] = None) -> str:
    """Generate cover image URL.
    
    Args:
        topic: Optional topic name for generating relevant image
        
    Returns:
        Cover image URL (placeholder or Unsplash)
    """
    if topic:
        # Use Unsplash API with topic-based search
        search_term = slugify(topic, separator="+")
        return f"https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=800&h=400&fit=crop&crop=center&q=80"
    return "https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=800&h=400&fit=crop&crop=center&q=80"


def validate_roadmap(roadmap: str) -> bool:
    """Validate roadmap value.
    
    Args:
        roadmap: Roadmap value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return roadmap in ROADMAPS


def validate_frequency(frequency: str) -> bool:
    """Validate frequency value.
    
    Args:
        frequency: Frequency value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return frequency in INTERVIEW_QUESTION_FREQUENCY


def validate_priority(priority: str) -> bool:
    """Validate priority value.
    
    Args:
        priority: Priority value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return priority in PRIORITY_LEVELS


def validate_company_types(company_types: List[str]) -> bool:
    """Validate company types list.
    
    Args:
        company_types: List of company types to validate
        
    Returns:
        True if all valid, False otherwise
    """
    return all(ct in COMPANY_TYPES for ct in company_types)


def get_schema_defaults() -> Dict[str, Any]:
    """Get default values for optional schema fields.
    
    Returns:
        Dictionary of default values
    """
    return {
        "isPremium": False,
        "price": 0,
        "discountPercentage": 0,
        "appliedCoupon": None,
        "features": []
    }


def transform_to_camel_case(field_name: str) -> str:
    """Transform snake_case to camelCase.
    
    Args:
        field_name: Field name in snake_case
        
    Returns:
        Field name in camelCase
    """
    parts = field_name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def validate_sheet_structure(sheet_data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate sheet structure against Mongoose schema.
    
    Args:
        sheet_data: Sheet data to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ["name", "slug", "description", "coverImageURL", "liveOn", "roadmap"]
    for field in required_fields:
        if field not in sheet_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate roadmap
    if "roadmap" in sheet_data and not validate_roadmap(sheet_data["roadmap"]):
        errors.append(f"Invalid roadmap value: {sheet_data['roadmap']}. Must be one of {ROADMAPS}")
    
    # Validate questions
    if "questions" in sheet_data:
        for i, question in enumerate(sheet_data["questions"]):
            question_errors = validate_question_structure(question, i)
            errors.extend(question_errors)
    
    return len(errors) == 0, errors


def validate_question_structure(question: Dict[str, Any], index: int = 0) -> List[str]:
    """Validate question structure.
    
    Args:
        question: Question data to validate
        index: Question index for error messages
        
    Returns:
        List of error messages
    """
    errors = []
    
    # Required fields
    required_fields = ["title", "question", "answer", "frequency", "priority"]
    for field in required_fields:
        if field not in question:
            errors.append(f"Question {index}: Missing required field: {field}")
    
    # Validate title length
    if "title" in question and len(question["title"]) > 100:
        errors.append(f"Question {index}: Title exceeds 100 characters")
    
    # Validate frequency
    if "frequency" in question and not validate_frequency(question["frequency"]):
        errors.append(f"Question {index}: Invalid frequency value: {question['frequency']}")
    
    # Validate priority
    if "priority" in question and not validate_priority(question["priority"]):
        errors.append(f"Question {index}: Invalid priority value: {question['priority']}")
    
    # Validate companyTypes
    if "companyTypes" in question:
        if not isinstance(question["companyTypes"], list):
            errors.append(f"Question {index}: companyTypes must be a list")
        elif not validate_company_types(question["companyTypes"]):
            errors.append(f"Question {index}: Invalid companyTypes values")
    
    return errors

