# GitHub Copilot Instructions — The-Boring-Agents

FastAPI + LangGraph AI content generation service for The Boring Education platform.

## Tech Stack
- **Framework**: FastAPI + Uvicorn
- **AI**: LangGraph (StateGraph) + LangChain + OpenAI (gpt-4o-mini)
- **Config**: Pydantic Settings (`src/core/config.py` → `config` singleton)
- **Validation**: Pydantic v2 `BaseModel` for all API schemas
- **Testing**: Pytest (class-based) + pytest-asyncio + pytest-mock + httpx
- **Linting**: Ruff + mypy
- **Python**: 3.9+

## Folder Structure
```
src/
├── agents/
│   ├── base.py         ← BaseAgent ABC
│   ├── quiz/           ← workflow.py, generators.py, session.py, prompts.py
│   ├── interview/      ← Interview prep workflow
│   └── aptitude/       ← Aptitude workflow
├── api/
│   ├── app.py          ← FastAPI app factory
│   ├── controllers/    ← Business logic per domain
│   ├── models/         ← Pydantic request/response models
│   ├── routes/         ← FastAPI routers
│   └── middleware.py
├── core/
│   ├── config.py       ← Pydantic Settings (Config class)
│   ├── orchestrator.py ← BaseWorkflowOrchestrator + @handle_node_errors
│   └── session/        ← BaseSessionManager
└── utils/
```

## LangGraph Workflow Pattern

### Every agent follows: TypedDict State → StateGraph Nodes → Orchestrator

```python
# 1. State
class MyAgentState(TypedDict):
    session_id: str
    topic: str
    status: str
    current_step: str
    error: Optional[str]
    progress: Dict[str, Any]
    output: Optional[Dict[str, Any]]

# 2. Node
@handle_node_errors("generate", error_status="failed")
def generate_node(state: MyAgentState) -> Dict[str, Any]:
    log_node_execution("generate", state["session_id"])
    if check_skip_condition(state, "output"):
        return {}
    result = ContentGenerator().generate(state["topic"])
    return {"output": result, "progress": get_progress_update(1, 2, "Generated")}

# 3. Graph
def create_workflow_graph():
    graph = StateGraph(MyAgentState)
    graph.add_node("generate", generate_node)
    graph.set_entry_point("generate")
    graph.add_edge("generate", END)
    return graph.compile()
```

## FastAPI Route Pattern (thin routes)
```python
@router.post("/resource", response_model=SessionResponse)
async def create_resource(payload: CreateResourceRequest, background_tasks: BackgroundTasks, request: Request):
    log_action(request, "create_resource", topic=payload.topic)
    try:
        return controller.create_resource(payload, background_tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Rules (Never Do This)
```python
# ❌ Plain dict as state
def my_node(state: dict) -> dict: ...
# ✅ TypedDict
def my_node(state: MyAgentState) -> Dict[str, Any]: ...

# ❌ os.environ directly
api_key = os.environ["OPENAI_API_KEY"]
# ✅ config singleton
from src.core.config import config
api_key = config.openai_api_key

# ❌ ChatOpenAI in a node
def my_node(state): llm = ChatOpenAI(model="gpt-4o-mini")
# ✅ Generator class
def my_node(state): generator = ContentGenerator(); result = generator.generate(state["topic"])

# ❌ print() for logging
print("Starting workflow")
# ✅ logging module
logger = logging.getLogger(__name__); logger.info("Starting workflow")

# ❌ Real LLM in tests
def test_generate(): orchestrator.run_workflow(state)
# ✅ Mock it
with patch("src.agents.quiz.generators.QuizQuestionGenerator.generate") as mock:
    mock.return_value = [{"question": "Q1"}]
```

## Test Structure
```python
class TestMyFeature:
    """Tests for MyFeature."""

    def test_initialization(self, temp_sessions_dir):
        """Test that feature initializes correctly."""
        assert feature is not None

    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async operation completes."""
        result = await async_fn()
        assert result.status == "success"
```
