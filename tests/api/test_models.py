"""
Tests for API request/response models.

Tests Pydantic model validation for all API endpoints.
"""

import pytest
from pydantic import ValidationError

from src.api.models.quiz_models import (
    QuizDifficulty,
    QuizAgentType,
    QuizQuestionModel,
    QuizOutputModel,
    CreateQuizRequest,
    TopicGenerationRequest,
    UploadQuizRequest,
    ValidateQuizRequest,
    SessionResponse,
    SimpleStatus,
)
from src.api.models.interview_prep_models import (
    CreateSheetRequest,
    TopicGenerationRequest as InterviewTopicRequest,
    SessionResponse as InterviewSessionResponse,
)


class TestQuizDifficultyEnum:
    """Tests for QuizDifficulty enum."""
    
    def test_easy_value(self):
        """Test easy difficulty value."""
        assert QuizDifficulty.EASY.value == "easy"
    
    def test_medium_value(self):
        """Test medium difficulty value."""
        assert QuizDifficulty.MEDIUM.value == "medium"
    
    def test_hard_value(self):
        """Test hard difficulty value."""
        assert QuizDifficulty.HARD.value == "hard"


class TestQuizAgentTypeEnum:
    """Tests for QuizAgentType enum."""
    
    def test_generic_value(self):
        """Test generic agent type value."""
        assert QuizAgentType.GENERIC.value == "generic"
    
    def test_tech_value(self):
        """Test tech agent type value."""
        assert QuizAgentType.TECH.value == "tech"
    
    def test_dsa_value(self):
        """Test DSA agent type value."""
        assert QuizAgentType.DSA.value == "dsa"
    
    def test_conceptual_value(self):
        """Test conceptual agent type value."""
        assert QuizAgentType.CONCEPTUAL.value == "conceptual"


class TestQuizQuestionModel:
    """Tests for QuizQuestionModel."""
    
    def test_valid_question(self):
        """Test creating a valid question."""
        question = QuizQuestionModel(
            question="What is React?",
            options=["A JS library", "A database", "A language", "An OS"],
            correctAnswer=0,
            explanation="React is a JavaScript library",
            detailedExplanation="React was developed by Facebook...",
            difficulty=QuizDifficulty.EASY
        )
        
        assert question.question == "What is React?"
        assert len(question.options) == 4
        assert question.correctAnswer == 0
    
    def test_question_minimum_options(self):
        """Test that question requires minimum 2 options."""
        with pytest.raises(ValidationError):
            QuizQuestionModel(
                question="Test?",
                options=["Only one"],  # Too few
                correctAnswer=0,
                explanation="Test",
                detailedExplanation="Test",
                difficulty=QuizDifficulty.EASY
            )
    
    def test_question_correct_answer_bounds(self):
        """Test correctAnswer must be within bounds."""
        with pytest.raises(ValidationError):
            QuizQuestionModel(
                question="Test?",
                options=["A", "B", "C", "D"],
                correctAnswer=5,  # Out of bounds
                explanation="Test",
                detailedExplanation="Test",
                difficulty=QuizDifficulty.EASY
            )
    
    def test_difficulty_normalization(self):
        """Test that difficulty is normalized to lowercase."""
        question = QuizQuestionModel(
            question="Test?",
            options=["A", "B"],
            correctAnswer=0,
            explanation="Test",
            detailedExplanation="Test",
            difficulty="EASY"  # Uppercase
        )
        
        assert question.difficulty == QuizDifficulty.EASY


class TestQuizOutputModel:
    """Tests for QuizOutputModel."""
    
    def test_valid_quiz_output(self, sample_quiz_data):
        """Test creating a valid quiz output."""
        quiz = QuizOutputModel(**sample_quiz_data)
        
        assert quiz.categoryName == "React.js Fundamentals"
        assert len(quiz.questions) == 2
        assert quiz.isActive is True
    
    def test_quiz_output_requires_category_name(self):
        """Test that categoryName is required."""
        with pytest.raises(ValidationError):
            QuizOutputModel(
                categoryDescription="Test",
                categoryIcon="🎯",
                questions=[]
            )
    
    def test_quiz_output_requires_questions(self):
        """Test that questions are required."""
        with pytest.raises(ValidationError):
            QuizOutputModel(
                categoryName="Test",
                categoryDescription="Test",
                categoryIcon="🎯"
                # Missing questions
            )


class TestCreateQuizRequest:
    """Tests for CreateQuizRequest."""
    
    def test_valid_request_minimal(self):
        """Test creating request with minimal fields."""
        request = CreateQuizRequest(topic="React.js")
        
        assert request.topic == "React.js"
        assert request.question_count == 20  # Default
        assert request.difficulty == QuizDifficulty.MEDIUM  # Default
    
    def test_valid_request_full(self):
        """Test creating request with all fields."""
        request = CreateQuizRequest(
            topic="Python",
            description="Python quiz",
            agentType="tech",
            questionCount=30,
            targetAudience="senior developers",
            difficulty="hard"
        )
        
        assert request.topic == "Python"
        assert request.question_count == 30
        assert request.difficulty == QuizDifficulty.HARD
    
    def test_request_requires_topic(self):
        """Test that topic is required."""
        with pytest.raises(ValidationError):
            CreateQuizRequest()
    
    def test_question_count_bounds(self):
        """Test question count bounds (1-100)."""
        with pytest.raises(ValidationError):
            CreateQuizRequest(topic="Test", questionCount=0)
        
        with pytest.raises(ValidationError):
            CreateQuizRequest(topic="Test", questionCount=101)
    
    def test_agent_type_normalization(self):
        """Test agent type is normalized."""
        request = CreateQuizRequest(topic="Test", agentType="TECH")
        assert request.agent_type == QuizAgentType.TECH


class TestTopicGenerationRequest:
    """Tests for TopicGenerationRequest."""
    
    def test_valid_request(self):
        """Test creating a valid request."""
        request = TopicGenerationRequest(
            topic="JavaScript Closures",
            questionCount=10
        )
        
        assert request.topic == "JavaScript Closures"
        assert request.question_count == 10
    
    def test_defaults(self):
        """Test default values."""
        request = TopicGenerationRequest(topic="Test")
        
        assert request.agent_type == QuizAgentType.TECH
        assert request.question_count == 20
        assert request.target_audience == "developers"
        assert request.difficulty == QuizDifficulty.MEDIUM


class TestSessionResponse:
    """Tests for SessionResponse."""
    
    def test_valid_response(self):
        """Test creating a valid response."""
        response = SessionResponse(
            sessionId="test-123",
            message="Session created"
        )
        
        assert response.sessionId == "test-123"
        assert response.message == "Session created"
    
    def test_requires_session_id(self):
        """Test that sessionId is required."""
        with pytest.raises(ValidationError):
            SessionResponse(message="Test")
    
    def test_requires_message(self):
        """Test that message is required."""
        with pytest.raises(ValidationError):
            SessionResponse(sessionId="test-123")


class TestSimpleStatus:
    """Tests for SimpleStatus."""
    
    def test_success_status(self):
        """Test creating success status."""
        status = SimpleStatus(ok=True, message="Success")
        
        assert status.ok is True
        assert status.message == "Success"
    
    def test_failure_status(self):
        """Test creating failure status."""
        status = SimpleStatus(ok=False, message="Failed")
        
        assert status.ok is False
        assert status.message == "Failed"


class TestValidateQuizRequest:
    """Tests for ValidateQuizRequest."""
    
    def test_valid_request(self, sample_quiz_data):
        """Test creating a valid validation request."""
        request = ValidateQuizRequest(quiz=sample_quiz_data)
        
        assert request.quiz["categoryName"] == "React.js Fundamentals"
    
    def test_accepts_any_dict(self):
        """Test that quiz field accepts any dictionary."""
        request = ValidateQuizRequest(quiz={"anything": "goes"})
        
        assert request.quiz["anything"] == "goes"


class TestUploadQuizRequest:
    """Tests for UploadQuizRequest."""
    
    def test_valid_request(self, sample_quiz_data):
        """Test creating a valid upload request."""
        quiz_output = QuizOutputModel(**sample_quiz_data)
        request = UploadQuizRequest(quiz=quiz_output)
        
        assert request.quiz.categoryName == "React.js Fundamentals"
    
    def test_with_api_url(self, sample_quiz_data):
        """Test creating request with API URL."""
        quiz_output = QuizOutputModel(**sample_quiz_data)
        request = UploadQuizRequest(
            quiz=quiz_output,
            apiUrl="http://localhost:3000"
        )
        
        assert request.api_url == "http://localhost:3000"
    
    def test_default_admin_secret(self, sample_quiz_data):
        """Test default admin secret."""
        quiz_output = QuizOutputModel(**sample_quiz_data)
        request = UploadQuizRequest(quiz=quiz_output)
        
        assert request.admin_secret == "TBEAdmin"


class TestInterviewCreateSheetRequest:
    """Tests for Interview CreateSheetRequest."""
    
    def test_valid_request(self):
        """Test creating a valid sheet request."""
        request = CreateSheetRequest(
            name="React Interview",
            description="React interview questions"
        )
        
        assert request.name == "React Interview"
        assert request.description == "React interview questions"
    
    def test_requires_name(self):
        """Test that name is required."""
        with pytest.raises(ValidationError):
            CreateSheetRequest(description="Test")
    
    def test_requires_description(self):
        """Test that description is required."""
        with pytest.raises(ValidationError):
            CreateSheetRequest(name="Test")
    
    def test_defaults(self):
        """Test default values."""
        request = CreateSheetRequest(
            name="Test",
            description="Test"
        )
        
        assert request.roadmap == "Tech"
        assert request.question_count == 20
    
    def test_question_count_bounds(self):
        """Test question count bounds."""
        with pytest.raises(ValidationError):
            CreateSheetRequest(
                name="Test",
                description="Test",
                questionCount=0
            )


class TestInterviewTopicRequest:
    """Tests for Interview TopicGenerationRequest."""
    
    def test_valid_request(self):
        """Test creating a valid request."""
        request = InterviewTopicRequest(
            topic="React Hooks",
            questionCount=15
        )
        
        assert request.topic == "React Hooks"
        assert request.question_count == 15
    
    def test_defaults(self):
        """Test default values."""
        request = InterviewTopicRequest(topic="Test")
        
        assert request.question_count == 20
        assert request.roadmap == "Tech"
        assert request.difficulty == "Medium"
        assert request.generate_answers is True

