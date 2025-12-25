"""
Global pytest configuration and fixtures for The Boring Agents test suite.

Provides shared fixtures for API testing, mocking, and test data.
"""

import pytest
import os
import json
import tempfile
import shutil
from typing import Dict, Any, Generator
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

# Set environment variables before importing the app
os.environ.setdefault("OPENAI_API_KEY", "test-api-key")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "WARNING")


# =============================================================================
# API Test Client Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def app():
    """Create a FastAPI test application."""
    from src.api.app import create_app
    return create_app()


@pytest.fixture(scope="session")
def client(app) -> Generator[TestClient, None, None]:
    """Create a test client for API testing."""
    with TestClient(app) as test_client:
        yield test_client


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================

@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp(prefix="tbe_test_")
    yield temp_path
    # Cleanup
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def temp_sessions_dir(temp_dir: str) -> str:
    """Create a temporary sessions directory."""
    sessions_path = os.path.join(temp_dir, "sessions")
    os.makedirs(sessions_path, exist_ok=True)
    return sessions_path


@pytest.fixture
def temp_output_dir(temp_dir: str) -> str:
    """Create a temporary output directory."""
    output_path = os.path.join(temp_dir, "output")
    os.makedirs(output_path, exist_ok=True)
    return output_path


# =============================================================================
# Mock Data Fixtures
# =============================================================================

@pytest.fixture
def sample_quiz_request() -> Dict[str, Any]:
    """Sample quiz creation request data."""
    return {
        "topic": "React.js Fundamentals",
        "description": "Test quiz for React concepts",
        "agentType": "tech",
        "questionCount": 5,
        "targetAudience": "developers",
        "difficulty": "medium"
    }


@pytest.fixture
def sample_interview_request() -> Dict[str, Any]:
    """Sample interview sheet creation request data."""
    return {
        "name": "React.js Interview Questions",
        "description": "Comprehensive React interview preparation",
        "agentType": "tech",
        "roadmap": "Frontend",
        "technology": "React.js",
        "questionCount": 5
    }


@pytest.fixture
def sample_topic_generation_request() -> Dict[str, Any]:
    """Sample topic generation request data."""
    return {
        "topic": "JavaScript Closures",
        "agentType": "tech",
        "questionCount": 3,
        "difficulty": "medium"
    }


@pytest.fixture
def sample_quiz_data() -> Dict[str, Any]:
    """Sample quiz output data matching Quiz.ts schema."""
    return {
        "categoryName": "React.js Fundamentals",
        "categoryDescription": "Test your React knowledge",
        "categoryIcon": "⚛️",
        "isActive": True,
        "questions": [
            {
                "question": "What is React?",
                "options": [
                    "A JavaScript library for building UIs",
                    "A database system",
                    "A programming language",
                    "An operating system"
                ],
                "correctAnswer": 0,
                "explanation": "React is a JavaScript library for building user interfaces.",
                "detailedExplanation": "React was developed by Facebook...",
                "difficulty": "easy"
            },
            {
                "question": "What is JSX?",
                "options": [
                    "A database query language",
                    "A syntax extension for JavaScript",
                    "A CSS framework",
                    "A testing library"
                ],
                "correctAnswer": 1,
                "explanation": "JSX is a syntax extension for JavaScript.",
                "detailedExplanation": "JSX allows you to write HTML-like syntax...",
                "difficulty": "easy"
            }
        ]
    }


@pytest.fixture
def sample_session_data() -> Dict[str, Any]:
    """Sample session data for testing."""
    return {
        "session_id": "test-session-123",
        "topic": "Test Topic",
        "description": "Test Description",
        "agent_type": "tech",
        "status": "in_progress",
        "progress": {"current": 1, "total": 5},
        "questions": [],
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "question_count": 5
    }


@pytest.fixture
def sample_interview_question() -> Dict[str, Any]:
    """Sample interview question data."""
    return {
        "title": "What is React?",
        "question": "Explain what React is and why it's used.",
        "answer": "React is a JavaScript library...",
        "frequency": "Most Asked",
        "companyTypes": ["MNC", "FAANG"],
        "priority": "High",
        "roadmap": "Frontend"
    }


# =============================================================================
# Mock Fixtures for LLM and External Services
# =============================================================================

@pytest.fixture
def mock_llm_response():
    """Mock LLM response generator."""
    def _create_response(content: str = "Mock LLM response"):
        mock = Mock()
        mock.content = content
        return mock
    return _create_response


@pytest.fixture
def mock_openai():
    """Mock OpenAI client for testing."""
    with patch("langchain_openai.ChatOpenAI") as mock:
        mock_instance = MagicMock()
        mock_instance.invoke.return_value = Mock(content="Mocked response")
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_session_manager():
    """Mock session manager for testing."""
    manager = Mock()
    manager.create_session.return_value = "test-session-123"
    manager.get_session.return_value = {
        "session_id": "test-session-123",
        "status": "in_progress",
        "progress": {"current": 0, "total": 5}
    }
    manager.list_sessions.return_value = []
    manager.update_status.return_value = None
    manager.save_session.return_value = None
    manager.delete_session.return_value = None
    return manager


# =============================================================================
# Environment and Configuration Fixtures
# =============================================================================

@pytest.fixture
def mock_config(temp_dir: str):
    """Mock configuration for testing."""
    with patch("src.core.config.Config") as mock:
        mock_instance = Mock()
        mock_instance.output_dir = os.path.join(temp_dir, "output")
        mock_instance.temp_dir = os.path.join(temp_dir, "temp")
        mock_instance.log_level = "WARNING"
        mock_instance.default_model = "gpt-4o-mini"
        mock_instance.environment = "test"
        mock_instance.api_base_url = "http://localhost:3000"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_env_manager():
    """Mock environment manager for testing."""
    with patch("src.core.env.get_env_manager") as mock:
        mock_instance = Mock()
        mock_instance.get.return_value = "test-value"
        mock_instance.get_required.return_value = "test-value"
        mock_instance.log_summary.return_value = None
        mock.return_value = mock_instance
        yield mock_instance


# =============================================================================
# File Operation Helpers
# =============================================================================

@pytest.fixture
def create_session_file(temp_sessions_dir: str):
    """Helper to create session files for testing."""
    def _create(session_id: str, data: Dict[str, Any]) -> str:
        filepath = os.path.join(temp_sessions_dir, f"{session_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return filepath
    return _create


@pytest.fixture
def create_output_file(temp_output_dir: str):
    """Helper to create output files for testing."""
    def _create(filename: str, data: Dict[str, Any]) -> str:
        filepath = os.path.join(temp_output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        return filepath
    return _create


# =============================================================================
# Pytest Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add api marker to tests in api directory
        if "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        # Add integration marker to integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        # Add e2e marker to e2e tests
        if "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)

