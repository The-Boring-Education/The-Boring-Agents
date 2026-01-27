"""
Unit tests for session types module.

Tests the SessionStatus, ProgressInfo, and BaseSessionData classes.
"""

import pytest
from datetime import datetime

from src.core.session.session_types import (
    SessionStatus,
    ProgressInfo,
    BaseSessionData,
)


class TestSessionStatus:
    """Tests for SessionStatus enum."""
    
    def test_status_values(self):
        """Test that all status values are correct."""
        assert SessionStatus.PENDING.value == "pending"
        assert SessionStatus.IN_PROGRESS.value == "in_progress"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.FAILED.value == "failed"
        assert SessionStatus.CANCELLED.value == "cancelled"
    
    def test_status_is_string_enum(self):
        """Test that SessionStatus is a string enum."""
        assert isinstance(SessionStatus.PENDING, str)
        assert SessionStatus.PENDING == "pending"
    
    def test_status_from_string(self):
        """Test creating status from string."""
        status = SessionStatus("completed")
        assert status == SessionStatus.COMPLETED
    
    def test_status_invalid_value_raises(self):
        """Test that invalid value raises error."""
        with pytest.raises(ValueError):
            SessionStatus("invalid_status")


class TestProgressInfo:
    """Tests for ProgressInfo class."""
    
    def test_default_initialization(self):
        """Test default initialization."""
        progress = ProgressInfo()
        
        assert progress.current_step == "Initializing..."
        assert progress.completed == 0
        assert progress.total == 0
        assert progress.percent == 0.0
    
    def test_initialization_with_values(self):
        """Test initialization with specific values."""
        progress = ProgressInfo(
            current_step="Processing",
            completed=5,
            total=10
        )
        
        assert progress.current_step == "Processing"
        assert progress.completed == 5
        assert progress.total == 10
        assert progress.percent == 50.0
    
    def test_percent_calculation(self):
        """Test automatic percent calculation."""
        progress = ProgressInfo(completed=3, total=4)
        assert progress.percent == 75.0
    
    def test_percent_zero_total(self):
        """Test percent with zero total."""
        progress = ProgressInfo(completed=5, total=0)
        assert progress.percent == 0.0
    
    def test_custom_percent(self):
        """Test custom percent overrides calculation."""
        progress = ProgressInfo(completed=1, total=2, percent=99.9)
        assert progress.percent == 99.9
    
    def test_to_dict(self):
        """Test to_dict method."""
        progress = ProgressInfo(
            current_step="Test step",
            completed=3,
            total=5
        )
        result = progress.to_dict()
        
        assert result["current_step"] == "Test step"
        assert result["completed"] == 3
        assert result["total"] == 5
        assert result["percent"] == 60.0
    
    def test_to_dict_rounds_percent(self):
        """Test that to_dict rounds percent to 2 decimals."""
        progress = ProgressInfo(completed=1, total=3)  # 33.333...%
        result = progress.to_dict()
        
        assert result["percent"] == 33.33
    
    def test_from_dict(self):
        """Test from_dict class method."""
        data = {
            "current_step": "Loading",
            "completed": 7,
            "total": 10,
            "percent": 70.0
        }
        progress = ProgressInfo.from_dict(data)
        
        assert progress.current_step == "Loading"
        assert progress.completed == 7
        assert progress.total == 10
        assert progress.percent == 70.0
    
    def test_from_dict_defaults(self):
        """Test from_dict with missing fields."""
        progress = ProgressInfo.from_dict({})
        
        assert progress.current_step == "Initializing..."
        assert progress.completed == 0
        assert progress.total == 0
    
    def test_roundtrip(self):
        """Test to_dict and from_dict roundtrip."""
        original = ProgressInfo(
            current_step="Processing item 5",
            completed=5,
            total=20
        )
        data = original.to_dict()
        restored = ProgressInfo.from_dict(data)
        
        assert restored.current_step == original.current_step
        assert restored.completed == original.completed
        assert restored.total == original.total
        # Note: percent might differ due to rounding
        assert abs(restored.percent - original.percent) < 0.01


class TestBaseSessionData:
    """Tests for BaseSessionData class."""
    
    def test_initialization_required_fields(self):
        """Test initialization with required fields."""
        session = BaseSessionData(
            session_id="test-123",
            workflow_type="quiz"
        )
        
        assert session.session_id == "test-123"
        assert session.workflow_type == "quiz"
        assert session.status == SessionStatus.PENDING
    
    def test_initialization_all_fields(self):
        """Test initialization with all fields."""
        progress = ProgressInfo(completed=5, total=10)
        metadata = {"topic": "React"}
        
        session = BaseSessionData(
            session_id="test-456",
            workflow_type="interview",
            status=SessionStatus.IN_PROGRESS,
            progress=progress,
            metadata=metadata
        )
        
        assert session.session_id == "test-456"
        assert session.workflow_type == "interview"
        assert session.status == SessionStatus.IN_PROGRESS
        assert session.progress.completed == 5
        assert session.metadata["topic"] == "React"
    
    def test_default_progress(self):
        """Test default progress is created."""
        session = BaseSessionData(
            session_id="test-789",
            workflow_type="shiksha"
        )
        
        assert isinstance(session.progress, ProgressInfo)
        assert session.progress.current_step == "Initializing..."
    
    def test_default_metadata(self):
        """Test default metadata is empty dict."""
        session = BaseSessionData(
            session_id="test-789",
            workflow_type="quiz"
        )
        
        assert session.metadata == {}
    
    def test_timestamps_set(self):
        """Test that timestamps are set on creation."""
        session = BaseSessionData(
            session_id="test-timestamps",
            workflow_type="quiz"
        )
        
        assert session.created_at is not None
        assert session.updated_at is not None
        # Should be ISO format strings
        assert "T" in session.created_at
    
    def test_error_default_none(self):
        """Test that error defaults to None."""
        session = BaseSessionData(
            session_id="test-error",
            workflow_type="quiz"
        )
        
        assert session.error is None
    
    def test_to_dict(self):
        """Test to_dict method."""
        session = BaseSessionData(
            session_id="test-to-dict",
            workflow_type="interview",
            status=SessionStatus.COMPLETED
        )
        result = session.to_dict()
        
        assert result["session_id"] == "test-to-dict"
        assert result["workflow_type"] == "interview"
        assert result["status"] == "completed"
        assert "progress" in result
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_to_dict_includes_progress(self):
        """Test that to_dict includes progress dict."""
        session = BaseSessionData(
            session_id="test-progress",
            workflow_type="quiz",
            progress=ProgressInfo(completed=5, total=10)
        )
        result = session.to_dict()
        
        assert result["progress"]["completed"] == 5
        assert result["progress"]["total"] == 10
    
    def test_to_dict_includes_error(self):
        """Test that to_dict includes error."""
        session = BaseSessionData(
            session_id="test-error",
            workflow_type="quiz"
        )
        session.error = "Something went wrong"
        result = session.to_dict()
        
        assert result["error"] == "Something went wrong"
    
    def test_from_dict(self):
        """Test from_dict class method."""
        data = {
            "session_id": "restored-session",
            "workflow_type": "quiz",
            "status": "in_progress",
            "progress": {
                "current_step": "Generating questions",
                "completed": 3,
                "total": 10
            },
            "metadata": {"difficulty": "hard"},
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:05:00",
            "error": None
        }
        session = BaseSessionData.from_dict(data)
        
        assert session.session_id == "restored-session"
        assert session.workflow_type == "quiz"
        assert session.status == SessionStatus.IN_PROGRESS
        assert session.progress.completed == 3
        assert session.metadata["difficulty"] == "hard"
    
    def test_from_dict_defaults(self):
        """Test from_dict with minimal data."""
        data = {
            "session_id": "minimal-session"
        }
        session = BaseSessionData.from_dict(data)
        
        assert session.session_id == "minimal-session"
        assert session.workflow_type == "unknown"
        assert session.status == SessionStatus.PENDING
    
    def test_from_dict_preserves_timestamps(self):
        """Test that from_dict preserves timestamps."""
        data = {
            "session_id": "test-timestamps",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00"
        }
        session = BaseSessionData.from_dict(data)
        
        assert session.created_at == "2024-01-01T00:00:00"
        assert session.updated_at == "2024-01-02T00:00:00"
    
    def test_roundtrip(self):
        """Test to_dict and from_dict roundtrip."""
        original = BaseSessionData(
            session_id="roundtrip-test",
            workflow_type="interview",
            status=SessionStatus.IN_PROGRESS,
            progress=ProgressInfo(completed=5, total=10),
            metadata={"key": "value"}
        )
        original.error = "Test error"
        
        data = original.to_dict()
        restored = BaseSessionData.from_dict(data)
        
        assert restored.session_id == original.session_id
        assert restored.workflow_type == original.workflow_type
        assert restored.status == original.status
        assert restored.progress.completed == original.progress.completed
        assert restored.metadata == original.metadata
        assert restored.error == original.error


class TestSessionStatusTransitions:
    """Tests for status transition patterns."""
    
    def test_typical_workflow_transitions(self):
        """Test typical workflow status transitions."""
        session = BaseSessionData(
            session_id="workflow-test",
            workflow_type="quiz"
        )
        
        # Initial state
        assert session.status == SessionStatus.PENDING
        
        # Start processing
        session.status = SessionStatus.IN_PROGRESS
        assert session.status == SessionStatus.IN_PROGRESS
        
        # Complete
        session.status = SessionStatus.COMPLETED
        assert session.status == SessionStatus.COMPLETED
    
    def test_failure_transition(self):
        """Test failure status transition."""
        session = BaseSessionData(
            session_id="failure-test",
            workflow_type="quiz"
        )
        
        session.status = SessionStatus.IN_PROGRESS
        session.status = SessionStatus.FAILED
        session.error = "API error"
        
        assert session.status == SessionStatus.FAILED
        assert session.error == "API error"
    
    def test_cancelled_transition(self):
        """Test cancelled status transition."""
        session = BaseSessionData(
            session_id="cancel-test",
            workflow_type="interview"
        )
        
        session.status = SessionStatus.IN_PROGRESS
        session.status = SessionStatus.CANCELLED
        
        assert session.status == SessionStatus.CANCELLED

