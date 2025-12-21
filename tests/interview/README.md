# Interview Agents Test Suite

This directory contains comprehensive tests for the interview agents system.

## Test Structure

```
tests/interview/
├── unit/
│   ├── test_generators.py                    # Basic generator tests
│   ├── test_generators_comprehensive.py      # Comprehensive generator tests
│   ├── test_workflow_nodes.py                # Workflow node tests
│   ├── test_metadata_question_generators.py  # Metadata and question generator tests
│   ├── test_common_utils.py                  # Common utilities tests
│   ├── test_schema_utils.py                  # Schema utilities tests
│   └── test_session_manager.py               # Session manager tests
└── integration/
    ├── test_workflow.py                       # Basic integration tests
    └── test_workflow_comprehensive.py        # Comprehensive integration tests
```

## Running Tests

### Run all tests
```bash
pytest tests/interview/
```

### Run unit tests only
```bash
pytest tests/interview/unit/
```

### Run integration tests only
```bash
pytest tests/interview/integration/
```

### Run specific test file
```bash
pytest tests/interview/unit/test_generators_comprehensive.py
```

### Run with coverage
```bash
pytest tests/interview/ --cov=src/agents/interview --cov-report=html
```

## Test Coverage

### Unit Tests

1. **Generators** (`test_generators_comprehensive.py`)
   - Generic answer generator
   - DSA answer generator
   - Tech answer generator
   - System design answer generator
   - Common generator functionality
   - Error handling

2. **Workflow Nodes** (`test_workflow_nodes.py`)
   - Metadata generation node
   - Question generation node
   - Answer generation node
   - State persistence node
   - Finalization node
   - Answer generator factory

3. **Metadata & Question Generators** (`test_metadata_question_generators.py`)
   - Metadata generation
   - Question generation
   - Parsing and validation
   - Different agent types and roadmaps

4. **Common Utilities** (`test_common_utils.py`)
   - Workflow utilities (error handling, state management)
   - State utilities (creation, validation, normalization)

5. **Session Manager** (`test_session_manager.py`)
   - Session creation
   - State persistence
   - Progress tracking

6. **Schema Utils** (`test_schema_utils.py`)
   - Schema validation
   - Enum validation
   - Field transformation

### Integration Tests

1. **Workflow Integration** (`test_workflow_comprehensive.py`)
   - Full workflow execution
   - Session management
   - Resume functionality
   - Error handling and recovery
   - Different workflow stages

## Mocking Strategy

All tests use mocking to avoid making real API calls:

- **LLM Calls**: All `_generate_with_prompt` calls are mocked
- **File I/O**: Session file operations are mocked or use temporary directories
- **External Services**: All external API calls are mocked

## Key Test Patterns

### Testing Generators
```python
@patch('src.agents.interview.generators.base_generator.BaseAnswerGenerator._generate_with_prompt')
@patch('src.agents.interview.common.mdx_utils.format_answer_as_mdx')
def test_generate_answer_success(self, mock_mdx_format, mock_generate):
    mock_generate.return_value = "Test answer"
    mock_mdx_format.return_value = "Formatted MDX"
    
    generator = GenericAnswerGenerator()
    result = generator.generate_answer(question="Test", topic="Test")
    
    assert result == "Formatted MDX"
```

### Testing Workflow Nodes
```python
@patch('src.agents.interview.workflow.nodes.MetadataGenerator')
def test_generate_metadata_success(self, mock_metadata_gen):
    mock_gen = Mock()
    mock_gen.generate_sheet_meta.return_value = "Metadata"
    mock_metadata_gen.return_value = mock_gen
    
    state = create_test_state()
    result = generate_metadata_node(state)
    
    assert result["meta"] == "Metadata"
```

### Testing Integration
```python
@patch('src.agents.interview.workflow.orchestrator.create_workflow_graph')
def test_full_workflow(self, mock_create_graph):
    mock_graph = Mock()
    mock_graph.invoke.return_value = {"status": "completed"}
    mock_create_graph.return_value = mock_graph
    
    orchestrator = InterviewWorkflowOrchestrator()
    result = orchestrator.execute_workflow("session-123")
    
    assert result["status"] == "completed"
```

## Test Data

Test data is created inline in each test to keep tests isolated and independent. Temporary directories are used for file-based operations and cleaned up after each test.

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- Fast execution (all mocked)
- No external dependencies
- Deterministic results
- Comprehensive coverage

## Adding New Tests

When adding new functionality:

1. Add unit tests for the new component
2. Add integration tests if it affects workflow
3. Update this README if adding new test categories
4. Ensure all tests pass before committing

## Notes

- Tests marked with `@pytest.mark.skip` require LLM API keys and are skipped by default
- All tests use temporary directories that are cleaned up automatically
- Mock objects are used extensively to avoid external dependencies

