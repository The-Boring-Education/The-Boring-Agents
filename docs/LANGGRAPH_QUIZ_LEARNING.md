# LangGraph Quiz System - Learning Guide

> **Master Document**: Update this file as you learn. Check off TODOs as you complete them.

---

## Table of Contents
1. [LangGraph Theory (Minimal)](#1-langgraph-theory-minimal)
2. [Interview Prep Code Walkthrough](#2-interview-prep-code-walkthrough)
3. [Quiz System Revamp TODOs](#3-quiz-system-revamp-todos)
4. [Side-by-Side Mapping](#4-side-by-side-mapping)
5. [Files to Remove](#5-files-to-remove)

---

## 1. LangGraph Theory (Minimal)

### What is LangGraph?

LangGraph is a library for building **stateful, multi-step AI workflows** as graphs. Think of it as a state machine for LLM applications.

**Why use LangGraph over traditional orchestration?**

| Traditional Approach | LangGraph Approach |
|---------------------|-------------------|
| Sequential function calls | Graph-based execution |
| State scattered across variables | Centralized state schema |
| Hard to resume from failures | Built-in state persistence |
| Complex conditional logic | Declarative edges |
| Difficult to visualize flow | Visual graph structure |

### Core Concepts

#### 1. State (TypedDict)
The **single source of truth** for your workflow. All data flows through this.

```python
from typing import TypedDict, List, Optional

class MyWorkflowState(TypedDict):
    session_id: str
    status: str
    data: List[str]
    error: Optional[str]
```

**Key insight**: Nodes receive the full state and return a **partial update** (only the fields they changed).

#### 2. Nodes (Functions)
Functions that:
- Receive the current state
- Do some work (call LLM, process data, etc.)
- Return a dict with fields to update

```python
def my_node(state: MyWorkflowState) -> dict:
    # Do work here
    result = process_something(state["data"])
    
    # Return ONLY the fields you want to update
    return {
        "data": result,
        "status": "processed"
    }
```

#### 3. Edges (Connections)
Define how nodes connect. Can be:
- **Direct edges**: A → B (always go from A to B)
- **Conditional edges**: A → B or C (choose based on state)

```python
# Direct edge
workflow.add_edge("node_a", "node_b")

# Conditional edge
workflow.add_conditional_edges(
    "node_a",
    lambda state: "node_b" if state["valid"] else "node_c"
)
```

#### 4. StateGraph (The Graph)
Combines everything into a runnable workflow.

```python
from langgraph.graph import StateGraph, END

workflow = StateGraph(MyWorkflowState)

# Add nodes
workflow.add_node("step1", step1_node)
workflow.add_node("step2", step2_node)

# Set entry point
workflow.set_entry_point("step1")

# Add edges
workflow.add_edge("step1", "step2")
workflow.add_edge("step2", END)

# Compile to make it runnable
app = workflow.compile()

# Run it!
result = app.invoke(initial_state)
```

### Mental Model

```
┌─────────────────────────────────────────────────────────────┐
│                        StateGraph                           │
│                                                             │
│   [Entry Point]                                             │
│        ↓                                                    │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │ Node A  │ ──→ │ Node B  │ ──→ │ Node C  │ ──→ [END]   │
│   └─────────┘     └─────────┘     └─────────┘              │
│        ↓               ↓               ↓                    │
│   Return partial   Return partial   Return partial          │
│   state update     state update     state update           │
│                                                             │
│   ════════════════════════════════════════════════════     │
│                  Unified State Object                       │
│   ════════════════════════════════════════════════════     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Interview Prep Code Walkthrough

The Interview Prep system is your **reference implementation**. Study each file in order.

### File 1: `state.py` - The State Schema

**Location**: `src/agents/interview/workflow/state.py`

```python
class InterviewWorkflowState(TypedDict):
    # Session info
    session_id: str
    name: str
    description: str
    agent_type: str
    roadmap: str
    question_count: int
    
    # Status tracking
    status: str  # pending, metadata_generating, questions_generating, etc.
    current_step: str
    error: Optional[str]
    
    # Generated content
    meta: Optional[str]
    questions: List[Dict[str, Any]]
    question_texts: List[str]
    
    # Progress & output
    progress: Dict[str, Any]
    output_file: Optional[str]
    sheet_data: Optional[Dict[str, Any]]
```

**What to learn**:
- Every field the workflow needs is defined here
- Status field tracks where we are in the flow
- Generated content accumulates as nodes complete

### File 2: `graph.py` - The Graph Definition

**Location**: `src/agents/interview/workflow/graph.py`

```python
from langgraph.graph import StateGraph, END

def create_workflow_graph() -> StateGraph:
    # 1. Create graph with state schema
    workflow = StateGraph(InterviewWorkflowState)
    
    # 2. Add nodes (functions that process state)
    workflow.add_node("generate_metadata", generate_metadata_node)
    workflow.add_node("persist_after_metadata", persist_state_node)
    workflow.add_node("generate_questions", generate_questions_node)
    workflow.add_node("persist_after_questions", persist_state_node)
    workflow.add_node("generate_answers", generate_answers_node)
    workflow.add_node("persist_after_answers", persist_state_node)
    workflow.add_node("finalize", finalize_node)
    
    # 3. Set where the graph starts
    workflow.set_entry_point("generate_metadata")
    
    # 4. Define the flow (edges)
    workflow.add_edge("generate_metadata", "persist_after_metadata")
    workflow.add_edge("persist_after_metadata", "generate_questions")
    workflow.add_edge("generate_questions", "persist_after_questions")
    workflow.add_edge("persist_after_questions", "generate_answers")
    workflow.add_edge("generate_answers", "persist_after_answers")
    workflow.add_edge("persist_after_answers", "finalize")
    workflow.add_edge("finalize", END)
    
    # 5. Compile and return
    return workflow.compile()
```

**What to learn**:
- Graph is created with the state schema
- Nodes are named functions added via `add_node`
- Edges define the execution order
- `persist_state_node` is reused multiple times (same function, different edge positions)
- `END` is a special constant that terminates the graph

**Visual representation**:
```
generate_metadata → persist → generate_questions → persist → generate_answers → persist → finalize → END
```

### File 3: `nodes.py` - The Node Functions

**Location**: `src/agents/interview/workflow/nodes.py`

Each node follows this pattern:

```python
@handle_node_errors("node_name", "failed")  # Decorator for error handling
def my_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]
    
    # 1. Check if we should skip (idempotency)
    if check_skip_condition(state, "some_field"):
        return {"status": "next_status"}
    
    # 2. Log execution
    log_node_execution("my_node", session_id)
    
    # 3. Do the actual work
    result = do_something(state["input_field"])
    
    # 4. Update session manager (persistence)
    session_manager = InterviewSessionManager()
    session_manager.update_something(session_id, result)
    
    # 5. Return PARTIAL state update
    return {
        "output_field": result,
        "status": "next_status",
        "current_step": "What's happening next..."
    }
```

**Key patterns to notice**:

1. **Idempotency**: Each node checks if work is already done → can resume from failures
2. **Error handling decorator**: Wraps nodes to catch errors and set failed status
3. **Partial returns**: Only return fields that changed
4. **Session persistence**: Update external storage for durability

**Example - generate_metadata_node**:
```python
@handle_node_errors("generate_metadata", "failed")
def generate_metadata_node(state: InterviewWorkflowState) -> Dict[str, Any]:
    session_id = state["session_id"]
    
    # Skip if already generated
    if check_skip_condition(state, "meta"):
        return {
            "status": "questions_generating",
            "current_step": "Generating questions..."
        }
    
    # Generate metadata using LLM
    metadata_gen = MetadataGenerator()
    meta = metadata_gen.generate_sheet_meta(
        name=state["name"],
        description=state["description"],
        roadmap=state["roadmap"]
    )
    
    # Persist to session
    session_manager = InterviewSessionManager()
    session_manager.set_meta(session_id, meta)
    
    # Return partial update
    return {
        "meta": meta,
        "status": "questions_generating",
        "current_step": "Generating questions..."
    }
```

### File 4: `orchestrator.py` - The Coordinator

**Location**: `src/agents/interview/workflow/orchestrator.py`

The orchestrator is the **entry point** that:
1. Creates sessions
2. Prepares initial state
3. Invokes the graph
4. Handles results

```python
class InterviewWorkflowOrchestrator:
    def __init__(self):
        self.graph = create_workflow_graph()  # Create the compiled graph
        self.session_manager = InterviewSessionManager()
    
    def start_generation(self, name, description, agent_type, ...) -> str:
        # 1. Create session in storage
        session_id = self.session_manager.create_session(
            name=name,
            description=description,
            agent_type=agent_type,
            ...
        )
        
        # 2. Create initial state
        initial_state = create_initial_state(
            session_id=session_id,
            name=name,
            ...
        )
        
        return session_id
    
    def execute_workflow(self, session_id: str) -> Dict[str, Any]:
        # 1. Load session data
        session_data = self.session_manager.get_session(session_id)
        
        # 2. Build state from session
        initial_state = state_from_session(session_data)
        
        # 3. Determine resume point
        initial_state["status"] = determine_resume_status(initial_state)
        
        # 4. Execute the graph!
        final_state = self.graph.invoke(initial_state)
        
        # 5. Update session with results
        self._update_session_from_state(session_id, final_state)
        
        return final_state
```

**What to learn**:
- Orchestrator owns the graph instance
- Sessions are created BEFORE graph execution
- State is built from session data (enables resume)
- `graph.invoke(state)` runs the entire workflow
- Results are persisted back to session

### File 5: `session_manager.py` - Session Storage

**Location**: `src/agents/interview/session/session_manager.py`

Extends `BaseSessionManager` with interview-specific methods:

```python
class InterviewSessionManager(BaseSessionManager):
    def __init__(self):
        super().__init__(workflow_type="interview")  # Sets sessions_dir
    
    def _create_session_data(self, session_id, name, description, ...) -> Dict:
        return {
            "session_id": session_id,
            "workflow_type": "interview",
            "name": name,
            "description": description,
            "status": SessionStatus.PENDING.value,
            "questions": [],
            "progress": {...},
            ...
        }
    
    # Interview-specific methods
    def set_meta(self, session_id, meta): ...
    def add_question(self, session_id, question): ...
    def set_output_file(self, session_id, output_file, sheet_data): ...
```

**What to learn**:
- Session data mirrors the state schema
- Provides domain-specific helper methods
- Persists to JSON files in `temp/interview_sessions/`

### File 6: Common Utilities

**`workflow_utils.py`**: Node execution helpers
```python
# Error handling decorator
@handle_node_errors("node_name", "failed")

# Skip condition checker
check_skip_condition(state, "field")

# Logging helper
log_node_execution("node_name", session_id)

# Progress update builder
get_progress_update(completed, total, current_step)
```

**`state_utils.py`**: State manipulation helpers
```python
# Create fresh state
create_initial_state(session_id, name, ...)

# Build state from existing session
state_from_session(session_data)

# Determine where to resume
determine_resume_status(state)
```

---

## 3. Quiz System Revamp TODOs

Update this checklist as you learn and build. Mark items with `[x]` when complete.

### Phase 1: Understanding LangGraph

- [x] Read and understand `state.py` (InterviewWorkflowState)
- [x] Read and understand `graph.py` (StateGraph creation)
- [x] Read and understand `nodes.py` (node functions pattern)
- [x] Read and understand `orchestrator.py` (workflow execution)
- [x] Run the Interview Prep workflow locally to see it in action
- [x] Trace through logs to understand execution flow

### Phase 2: Design Quiz Workflow

- [ ] Define QuizWorkflowState (what fields do we need?)
- [ ] Draw the quiz generation flow (what nodes do we need?)
- [ ] Identify what can be reused vs. what's quiz-specific
- [ ] Document the node responsibilities

### Phase 3: Implement Quiz LangGraph

- [ ] Create `src/agents/quiz/workflow/state.py`
- [ ] Create `src/agents/quiz/workflow/nodes.py`
- [ ] Create `src/agents/quiz/workflow/graph.py`
- [ ] Create `src/agents/quiz/workflow/orchestrator.py`
- [ ] Create `src/agents/quiz/session/session_manager.py`

### Phase 4: Create Quiz Generators

- [ ] Create base quiz generator
- [ ] Create question generator node
- [ ] Create research node (if needed)
- [ ] Create metadata generator node
- [ ] Create upload/finalize node

### Phase 5: Integrate with API

- [ ] Update `src/api/routes/quiz.py` to use new orchestrator
- [ ] Update `src/api/controllers/quiz_controller.py`
- [ ] Update API models if needed
- [ ] Test API endpoints

### Phase 6: Testing & Polish

- [ ] Write unit tests for nodes
- [ ] Write integration tests for workflow
- [ ] Test resume functionality
- [ ] Test error handling
- [ ] Remove old quiz code (see Section 5)

---

## 4. Side-by-Side Mapping

| Interview Prep | Quiz Equivalent (You'll Build) |
|---------------|-------------------------------|
| **State** | |
| `InterviewWorkflowState` | `QuizWorkflowState` |
| `session_id, name, description` | `session_id, topic, target_audience` |
| `questions: List[Dict]` | `questions: List[Dict]` |
| `meta: str` | `category_metadata: Dict` |
| | |
| **Nodes** | |
| `generate_metadata_node` | `generate_category_metadata_node` |
| `generate_questions_node` | `generate_quiz_questions_node` |
| `generate_answers_node` | N/A (Quiz has options, not answers) |
| `persist_state_node` | `persist_state_node` (reuse pattern) |
| `finalize_node` | `finalize_quiz_node` |
| | |
| **Graph Flow** | |
| metadata → questions → answers → finalize | research? → questions → metadata → finalize |
| | |
| **Session Manager** | |
| `InterviewSessionManager` | `QuizSessionManager` |
| `set_meta()`, `add_question()` | `set_category()`, `add_question()` |
| | |
| **Generators** | |
| `MetadataGenerator` | `QuizMetadataGenerator` |
| `QuestionGenerator` | `QuizQuestionGenerator` |
| `BaseAnswerGenerator` | N/A |
| | |
| **Orchestrator** | |
| `InterviewWorkflowOrchestrator` | `QuizWorkflowOrchestrator` |
| `start_generation()` | `start_quiz_generation()` |
| `execute_workflow()` | `execute_quiz_workflow()` |

### Quiz-Specific Considerations

1. **Questions have options**: Unlike interview Q&A, quiz questions have:
   - Multiple options (4 choices)
   - Correct answer index
   - Explanation
   - Difficulty level

2. **Research step**: The current quiz system has research. Consider if you need:
   - A dedicated research node
   - Or integrate research into question generation

3. **No answer generation**: Quiz questions have predefined options, not generated answers

4. **Category metadata**: Different from interview sheet metadata:
   - categoryName
   - categoryDescription
   - categoryIcon

---

## 5. Files to Remove

**Remove AFTER you've built and tested the new LangGraph Quiz system.**

### Quiz Agent Files (to delete)
| File | Lines | Purpose |
|------|-------|---------|
| `src/agents/quiz/__init__.py` | 16 | Exports |
| `src/agents/quiz/quiz_orchestrator.py` | 745 | Old orchestrator (non-LangGraph) |
| `src/agents/quiz/quiz_question_creator.py` | 557 | Question creation with prompts |
| `src/agents/quiz/quiz_researcher.py` | 482 | Research agent with prompts |
| `src/agents/quiz/quiz_uploader.py` | 529 | DB upload & validation |
| `src/agents/quiz/types.py` | 163 | Type definitions (QuizModel, QuizQuestionModel) |

### API Files (to update, not delete)
| File | Lines | Action |
|------|-------|--------|
| `src/api/routes/quiz.py` | 304 | Update to use new orchestrator |
| `src/api/controllers/quiz_controller.py` | 243 | Update to use new orchestrator |
| `src/api/models/quiz_models.py` | 48 | Keep or update as needed |

### Temp Files (auto-cleanup)
| Directory | Purpose |
|-----------|---------|
| `temp/quiz_progress/` | Progress tracking files |

---

## Quick Reference Commands

```bash
# Run the agents server
cd /Users/imsks/Public/git-repos/tbe/The-Boring-Agents
python run.py

# Test Interview Prep endpoint (to see it work)
curl -X POST http://localhost:8000/api/v1/interview/sheets \
  -H "Content-Type: application/json" \
  -d '{"name": "React Basics", "description": "Test sheet", "agent_type": "tech", "roadmap": "Frontend"}'

# Check session status
curl http://localhost:8000/api/v1/interview/sessions/{session_id}
```

---

## Notes & Questions

Use this space to jot down questions as you learn:

1. _Your question here..._
2. _Your question here..._
3. _Your question here..._

---

**Last Updated**: _(Update this when you make changes)_

