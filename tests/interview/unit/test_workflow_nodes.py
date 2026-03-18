"""Unit tests for workflow nodes."""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.agents.interview.workflow import (
    generate_metadata_node,
    generate_questions_node,
    generate_answers_node,
    persist_state_node,
    finalize_node,
)
from src.agents.interview.generators import get_generator
from src.agents.interview.workflow import InterviewWorkflowState
from src.agents.interview.generators import AnswerAgentType


class TestGenerateMetadataNode:
    """Tests for generate_metadata_node."""
    
    def test_skip_when_meta_exists(self):
        """Test that node skips when metadata already exists."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": "Existing metadata",
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        result = generate_metadata_node(state)
        
        assert result["status"] == "questions_generating"
        assert "meta" not in result  # Should not regenerate
    
    @patch('src.agents.interview.workflow.MetadataGenerator')
    @patch('src.agents.interview.workflow._get_session_manager')
    def test_generate_metadata_success(self, mock_get_sm, mock_metadata_gen):
        """Test successful metadata generation."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": None,
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        mock_gen_instance = Mock()
        mock_gen_instance.generate_sheet_meta.return_value = "Generated metadata"
        mock_metadata_gen.return_value = mock_gen_instance
        
        mock_session = Mock()
        mock_get_sm.return_value = mock_session
        
        result = generate_metadata_node(state)
        
        assert result["meta"] == "Generated metadata"
        assert result["status"] == "questions_generating"
        mock_gen_instance.generate_sheet_meta.assert_called_once_with(
            name="Test Sheet",
            description="Test Description",
            roadmap="Tech"
        )
        mock_session.set_meta.assert_called_once_with("test-123", "Generated metadata")
    
    @patch('src.agents.interview.workflow.MetadataGenerator')
    def test_generate_metadata_error_handling(self, mock_metadata_gen):
        """Test error handling in metadata generation."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": None,
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        # Mock error
        mock_metadata_gen.side_effect = Exception("API Error")
        
        result = generate_metadata_node(state)
        
        assert result["status"] == "failed"
        assert "error" in result
        assert "API Error" in result["error"]


class TestGenerateQuestionsNode:
    """Tests for generate_questions_node."""
    
    def test_skip_when_questions_exist(self):
        """Test that node skips when questions already exist."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": "Metadata",
            "questions": [{"title": "Q1", "question": "Question 1", "answer": ""}],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        result = generate_questions_node(state)
        
        assert result["status"] == "answers_generating"
        assert "questions" not in result  # Should not regenerate
    
    @patch('src.agents.interview.workflow.QuestionGenerator')
    @patch('src.agents.interview.workflow.MetadataGenerator')
    @patch('src.agents.interview.workflow._get_session_manager')
    def test_generate_questions_success(self, mock_get_sm, mock_metadata_gen, mock_question_gen):
        """Test successful question generation."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": "Metadata",
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        mock_q_gen = Mock()
        mock_q_gen.generate_questions.return_value = ["Question 1", "Question 2"]
        mock_question_gen.return_value = mock_q_gen
        
        mock_m_gen = Mock()
        mock_m_gen.generate_question_metadata.return_value = {
            "frequency": "Asked Sometimes",
            "priority": "Medium",
            "companyTypes": ["Startup"]
        }
        mock_metadata_gen.return_value = mock_m_gen
        
        mock_session = Mock()
        mock_get_sm.return_value = mock_session
        
        result = generate_questions_node(state)
        
        assert "questions" in result
        assert len(result["questions"]) == 2
        assert result["status"] == "answers_generating"
        assert result["progress"]["total"] == 2


class TestGenerateAnswersNode:
    """Tests for generate_answers_node."""
    
    def test_error_when_no_questions(self):
        """Test error when no questions exist."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": "Metadata",
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        result = generate_answers_node(state)
        
        assert result["status"] == "failed"
        assert "error" in result
    
    def test_skip_when_all_answers_exist(self):
        """Test that node skips when all answers are generated."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": "Metadata",
            "questions": [
                {"title": "Q1", "question": "Question 1", "answer": "Answer 1"},
                {"title": "Q2", "question": "Question 2", "answer": "Answer 2"}
            ],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        result = generate_answers_node(state)
        
        assert result["status"] == "finalizing"
        assert result["progress"]["completed"] == 2
    
    @patch('src.agents.interview.workflow.get_generator')
    @patch('src.agents.interview.workflow._get_session_manager')
    def test_generate_answers_success(self, mock_get_sm, mock_get_generator):
        """Test successful answer generation."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": "Metadata",
            "questions": [
                {"title": "Q1", "question": "Question 1", "answer": "", "frequency": "Asked Sometimes", "priority": "Medium", "companyTypes": ["Startup"]}
            ],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        mock_generator = Mock()
        mock_generator.generate_answer.return_value = "Generated answer"
        mock_get_generator.return_value = mock_generator
        
        mock_session = Mock()
        mock_session.get_session.return_value = {}
        mock_get_sm.return_value = mock_session
        
        result = generate_answers_node(state)
        
        assert result["status"] == "finalizing"
        assert result["questions"][0]["answer"] == "Generated answer"
        mock_generator.generate_answer.assert_called_once()


class TestPersistStateNode:
    """Tests for persist_state_node."""
    
    @patch('src.agents.interview.workflow._get_session_manager')
    def test_persist_state_success(self, mock_get_sm):
        """Test successful state persistence."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "in_progress",
            "current_step": "Processing...",
            "error": None,
            "meta": "Metadata",
            "questions": [],
            "question_texts": [],
            "progress": {"completed": 5, "total": 10},
            "output_file": None,
            "sheet_data": None
        }
        
        mock_session = Mock()
        mock_session.get_session.return_value = {
            "session_id": "test-123",
            "status": "pending"
        }
        mock_get_sm.return_value = mock_session
        
        result = persist_state_node(state)
        
        assert result == {}
        mock_session.save_session.assert_called_once()
    
    @patch('src.agents.interview.workflow._get_session_manager')
    def test_persist_state_error_handling(self, mock_get_sm):
        """Test error handling in state persistence."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "pending",
            "current_step": "Initializing...",
            "error": None,
            "meta": None,
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        mock_session = Mock()
        mock_session.get_session.side_effect = Exception("File error")
        mock_get_sm.return_value = mock_session
        
        result = persist_state_node(state)
        assert result == {}


class TestFinalizeNode:
    """Tests for finalize_node."""
    
    def test_skip_when_already_finalized(self):
        """Test that node skips when already finalized."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "finalizing",
            "current_step": "Finalizing...",
            "error": None,
            "meta": "Metadata",
            "questions": [],
            "question_texts": [],
            "progress": {},
            "output_file": "/path/to/output.json",
            "sheet_data": {"name": "Test Sheet"}
        }
        
        result = finalize_node(state)
        
        assert result["status"] == "completed"
    
    @patch('src.agents.interview.workflow._get_session_manager')
    @patch('src.agents.interview.workflow.validate_sheet_structure')
    @patch('src.agents.interview.workflow.generate_slug')
    @patch('src.agents.interview.workflow.generate_cover_image_url')
    @patch('src.agents.interview.workflow.get_schema_defaults')
    @patch('builtins.open', create=True)
    @patch('json.dump')
    @patch('os.makedirs')
    @patch('os.path.join')
    def test_finalize_success(
        self, mock_join, mock_makedirs, mock_json_dump, mock_open,
        mock_defaults, mock_cover, mock_slug, mock_validate, mock_get_sm
    ):
        """Test successful finalization."""
        state: InterviewWorkflowState = {
            "session_id": "test-123",
            "name": "Test Sheet",
            "description": "Test Description",
            "agent_type": "generic",
            "roadmap": "Tech",
            "status": "finalizing",
            "current_step": "Finalizing...",
            "error": None,
            "meta": "Metadata",
            "questions": [
                {"title": "Q1", "question": "Question 1", "answer": "Answer 1"}
            ],
            "question_texts": [],
            "progress": {},
            "output_file": None,
            "sheet_data": None
        }
        
        mock_slug.return_value = "test-sheet"
        mock_cover.return_value = "https://example.com/image.jpg"
        mock_defaults.return_value = {
            "isPremium": False,
            "price": 0,
            "discountPercentage": 0,
            "appliedCoupon": None,
            "features": [],
            "dsaQuestions": []
        }
        mock_validate.return_value = (True, [])
        mock_join.return_value = "/path/to/output.json"
        
        mock_session = Mock()
        mock_get_sm.return_value = mock_session
        
        result = finalize_node(state)
        
        assert result["status"] == "completed"
        assert "sheet_data" in result
        assert "output_file" in result
        mock_session.set_output_file.assert_called_once()
        mock_session.update_status.assert_called_once()


class TestGetGenerator:
    """Tests for generator registry get_generator()."""
    
    def test_get_generic_generator(self):
        generator = get_generator("generic")
        assert generator is not None
        from src.agents.interview.generators import GenericAnswerGenerator
        assert isinstance(generator, GenericAnswerGenerator)
    
    def test_get_dsa_generator(self):
        generator = get_generator("dsa")
        assert generator is not None
        from src.agents.interview.generators import DSAAnswerGenerator
        assert isinstance(generator, DSAAnswerGenerator)
    
    def test_get_tech_generator(self):
        generator = get_generator("tech", technology="Python")
        assert generator is not None
        from src.agents.interview.generators import TechAnswerGenerator
        assert isinstance(generator, TechAnswerGenerator)
    
    def test_get_system_design_generator(self):
        generator = get_generator("system_design")
        assert generator is not None
        from src.agents.interview.generators import SystemDesignAnswerGenerator
        assert isinstance(generator, SystemDesignAnswerGenerator)
    
    def test_raises_for_invalid_type(self):
        """Test that invalid agent type raises ValueError."""
        with pytest.raises(ValueError):
            get_generator("invalid_type")

