"""Type definitions for quiz agents."""

from enum import Enum
from typing import Dict, List, Optional, Any


class QuizDifficulty(Enum):
    """Quiz difficulty levels matching the database model."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class QuizTopic(Enum):
    """Available quiz topics."""
    REACT = "React.js"
    NODEJS = "Node.js"
    MONGODB = "MongoDB"
    EXPRESS = "Express.js"
    HTML = "HTML"
    CSS = "CSS"
    JAVASCRIPT = "JavaScript"
    PYTHON = "Python"
    JAVA = "Java"
    CPP = "C++"
    C = "C"
    REDUX = "Redux"
    SQL = "SQL"
    NOSQL = "NoSQL"
    DATA_SCIENCE = "Data Science"
    MACHINE_LEARNING = "Machine Learning"
    DEEP_LEARNING = "Deep Learning"
    AI = "Artificial Intelligence"
    CLOUD_COMPUTING = "Cloud Computing"
    DEVOPS = "DevOps"
    CYBER_SECURITY = "Cyber Security"
    
    @classmethod
    def from_string(cls, topic: str) -> Optional['QuizTopic']:
        """Convert string to QuizTopic enum."""
        topic_map = {
            "react": cls.REACT,
            "react.js": cls.REACT,
            "reactjs": cls.REACT,
            "node": cls.NODEJS,
            "node.js": cls.NODEJS,
            "nodejs": cls.NODEJS,
            "mongo": cls.MONGODB,
            "mongodb": cls.MONGODB,
            "express": cls.EXPRESS,
            "express.js": cls.EXPRESS,
            "expressjs": cls.EXPRESS,
            "html": cls.HTML,
            "css": cls.CSS,
            "javascript": cls.JAVASCRIPT,
            "js": cls.JAVASCRIPT,
            "python": cls.PYTHON,
            "java": cls.JAVA,
            "c++": cls.CPP,
            "cpp": cls.CPP,
            "c": cls.C,
            "redux": cls.REDUX,
            "sql": cls.SQL,
            "nosql": cls.NOSQL,
            "data science": cls.DATA_SCIENCE,
            "datascience": cls.DATA_SCIENCE,
            "machine learning": cls.MACHINE_LEARNING,
            "ml": cls.MACHINE_LEARNING,
            "deep learning": cls.DEEP_LEARNING,
            "dl": cls.DEEP_LEARNING,
            "artificial intelligence": cls.AI,
            "ai": cls.AI,
            "cloud computing": cls.CLOUD_COMPUTING,
            "cloud": cls.CLOUD_COMPUTING,
            "devops": cls.DEVOPS,
            "cyber security": cls.CYBER_SECURITY,
            "cybersecurity": cls.CYBER_SECURITY,
            "security": cls.CYBER_SECURITY
        }
        
        normalized = topic.lower().strip()
        return topic_map.get(normalized)


class QuizQuestionModel:
    """Quiz question data model matching the database schema."""
    
    def __init__(self, 
                 question: str,
                 options: List[str],
                 correct_answer: int,
                 explanation: str,
                 detailed_explanation: str,
                 difficulty: QuizDifficulty):
        """Initialize a quiz question."""
        self.question = question
        self.options = options
        self.correct_answer = correct_answer
        self.explanation = explanation
        self.detailed_explanation = detailed_explanation
        self.difficulty = difficulty
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "question": self.question,
            "options": self.options,
            "correctAnswer": self.correct_answer,
            "explanation": self.explanation,
            "detailedExplanation": self.detailed_explanation,
            "difficulty": self.difficulty.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuizQuestionModel':
        """Create from dictionary."""
        return cls(
            question=data.get("question", ""),
            options=data.get("options", []),
            correct_answer=data.get("correctAnswer", 0),
            explanation=data.get("explanation", ""),
            detailed_explanation=data.get("detailedExplanation", ""),
            difficulty=QuizDifficulty(data.get("difficulty", "medium"))
        )


class QuizModel:
    """Quiz data model matching the database schema."""
    
    def __init__(self,
                 category_name: str,
                 category_description: str,
                 category_icon: str,
                 questions: List[QuizQuestionModel],
                 is_active: bool = True):
        """Initialize a quiz."""
        self.category_name = category_name
        self.category_description = category_description
        self.category_icon = category_icon
        self.questions = questions
        self.is_active = is_active
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "categoryName": self.category_name,
            "categoryDescription": self.category_description,
            "categoryIcon": self.category_icon,
            "questions": [q.to_dict() for q in self.questions],
            "isActive": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuizModel':
        """Create from dictionary."""
        questions = [QuizQuestionModel.from_dict(q) for q in data.get("questions", [])]
        return cls(
            category_name=data.get("categoryName", ""),
            category_description=data.get("categoryDescription", ""),
            category_icon=data.get("categoryIcon", ""),
            questions=questions,
            is_active=data.get("isActive", True)
        ) 