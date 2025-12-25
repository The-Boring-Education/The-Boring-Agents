# The Boring Agents - Test Suite

Comprehensive test suite for The Boring Agents API and agentic systems.

## 📁 Test Structure

```
tests/
├── conftest.py                 # Global fixtures and pytest configuration
├── README.md                   # This file
│
├── api/                        # API endpoint tests
│   ├── __init__.py
│   ├── test_health.py          # Health check endpoint tests
│   ├── test_quiz_routes.py     # Quiz API route tests
│   ├── test_interview_routes.py # Interview API route tests
│   ├── test_session_routes.py  # Session management route tests
│   └── test_models.py          # Pydantic model validation tests
│
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_helpers.py         # Utils/helpers tests
│   ├── test_validation.py      # Validation utilities tests
│   ├── test_session_logger.py  # Session logger tests
│   ├── test_request_logging.py # Request logging tests
│   ├── test_env.py             # Environment manager tests
│   ├── test_session_types.py   # Session types tests
│   └── test_config.py          # Configuration tests
│
├── quiz/                       # Quiz agent tests
│   ├── __init__.py
│   ├── test_session_manager.py # Quiz session manager tests
│   ├── test_workflow_state.py  # Workflow state tests
│   ├── test_metadata_generator.py # Metadata generator tests
│   └── test_orchestrator.py    # E2E orchestrator tests
│
└── interview/                  # Interview agent tests (existing)
    ├── unit/                   # Unit tests
    └── integration/            # Integration tests
```

## 🚀 Running Tests

### Prerequisites

Install development dependencies:

```bash
pip install -e ".[dev]"
```

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

Open `htmlcov/index.html` to view the coverage report.

### Run Specific Test Categories

```bash
# API tests only
pytest tests/api/

# Unit tests only
pytest tests/unit/

# Quiz tests only
pytest tests/quiz/

# Interview tests only
pytest tests/interview/

# Specific test file
pytest tests/api/test_quiz_routes.py

# Specific test class
pytest tests/api/test_quiz_routes.py::TestQuizCreation

# Specific test method
pytest tests/api/test_quiz_routes.py::TestQuizCreation::test_create_quiz_returns_session_id
```

### Run by Markers

```bash
# Run only API tests
pytest -m api

# Run only integration tests
pytest -m integration

# Run only E2E tests
pytest -m e2e

# Exclude slow tests
pytest -m "not slow"
```

### Verbose Output

```bash
pytest -v                  # Verbose
pytest -vv                 # More verbose
pytest -s                  # Show print statements
pytest --tb=long           # Detailed tracebacks
```

## 🧪 Test Categories

### 1. API Tests (`tests/api/`)

Tests for FastAPI endpoints using TestClient:
- **Health Check**: Basic service health verification
- **Quiz Routes**: Quiz creation, session management, validation, upload
- **Interview Routes**: Sheet creation, topic generation, session management
- **Session Routes**: Cross-workflow session operations
- **Models**: Pydantic model validation

### 2. Unit Tests (`tests/unit/`)

Isolated tests for individual components:
- **Helpers**: File operations, text processing, utility functions
- **Validation**: Interview question validation logic
- **Session Logger**: JSONL logging for workflows
- **Request Logging**: API request logging utilities
- **Environment**: Environment variable management
- **Config**: Application configuration
- **Session Types**: Session status enums and data structures

### 3. Quiz Agent Tests (`tests/quiz/`)

Tests for the quiz generation workflow:
- **Session Manager**: Quiz session CRUD operations
- **Workflow State**: TypedDict state management
- **Metadata Generator**: Category metadata generation
- **Orchestrator**: E2E workflow orchestration

### 4. Interview Agent Tests (`tests/interview/`)

Tests for the interview preparation workflow (existing tests):
- **Generators**: Answer generators for different types
- **Workflow Nodes**: Individual workflow step tests
- **Session Manager**: Interview session management
- **Integration**: Full workflow tests

## 🎭 Mocking Strategy

All tests use mocking to avoid:
- Real API calls to OpenAI/Anthropic
- File system side effects
- External service dependencies

### Common Mocks

```python
# Mock LLM responses
@patch.object(Generator, '_generate_with_prompt')
def test_generation(self, mock_generate):
    mock_generate.return_value = "Mocked response"
    # ...

# Mock session manager
@pytest.fixture
def mock_session_manager():
    manager = Mock()
    manager.create_session.return_value = "session-123"
    return manager

# Mock workflow graph
@patch('src.agents.quiz.workflow.orchestrator.create_workflow_graph')
def test_workflow(self, mock_graph):
    mock_graph.return_value.invoke.return_value = {"status": "completed"}
    # ...
```

## 📊 Coverage Goals

| Module | Target Coverage |
|--------|-----------------|
| `src/api/` | 80% |
| `src/utils/` | 90% |
| `src/core/` | 80% |
| `src/agents/quiz/` | 70% |
| `src/agents/interview/` | 70% |

## 🛠️ Fixtures

Key fixtures available in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `client` | FastAPI TestClient |
| `temp_dir` | Temporary directory (auto-cleaned) |
| `temp_sessions_dir` | Temporary sessions directory |
| `sample_quiz_request` | Sample quiz creation request |
| `sample_interview_request` | Sample interview request |
| `sample_quiz_data` | Sample quiz output data |
| `sample_session_data` | Sample session data |
| `mock_llm_response` | Mock LLM response factory |
| `mock_session_manager` | Pre-configured mock session manager |

## 🔍 Debugging Tests

### Run single test with full output

```bash
pytest tests/api/test_quiz_routes.py::TestQuizCreation::test_create_quiz_returns_session_id -v -s --tb=long
```

### Drop into debugger on failure

```bash
pytest --pdb
```

### Run with logging

```bash
pytest --log-cli-level=DEBUG
```

## ✅ Writing New Tests

### Test File Naming

- File: `test_<module_name>.py`
- Class: `Test<FeatureName>`
- Method: `test_<specific_behavior>`

### Test Structure

```python
class TestFeatureName:
    """Tests for FeatureName."""
    
    @pytest.fixture
    def setup_fixture(self, temp_dir):
        """Setup for tests."""
        return SomeObject(temp_dir)
    
    def test_happy_path(self, setup_fixture):
        """Test the expected behavior."""
        result = setup_fixture.do_something()
        assert result == expected
    
    def test_edge_case(self, setup_fixture):
        """Test edge case behavior."""
        with pytest.raises(ValueError):
            setup_fixture.do_invalid_thing()
```

### Best Practices

1. **One assertion per test** (when practical)
2. **Descriptive test names** that explain what's being tested
3. **Use fixtures** for common setup
4. **Mock external dependencies**
5. **Test both success and failure paths**
6. **Keep tests fast** - mock slow operations

## 🏃 CI/CD Integration

Tests are designed to run in CI/CD pipelines:
- No external dependencies required
- Deterministic results
- Fast execution (all mocked)
- Comprehensive coverage reports

Example GitHub Actions workflow:

```yaml
- name: Run Tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=src --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## 📝 Notes

- Tests marked with `@pytest.mark.skip` require actual API keys
- All file operations use temporary directories
- Mock objects are used extensively to avoid external calls
- Integration tests may require additional setup

