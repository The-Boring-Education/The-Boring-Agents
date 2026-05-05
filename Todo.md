# The Boring Agents — Unified Agentic System Plan

> **Goal**: Build a unified agentic content generation system for all TBE apps (DSA Yatra, On Campus, Shiksha, Projects) that is async, restartable, chunk-wise, LLM-agnostic, and tightly integrated with the TBE-Web API and tbe-admin dashboard.

---

## Current System Audit

### ✅ What Exists (The-Boring-Agents)

| Agent | Status | Coverage |
|-------|--------|----------|
| Quiz | ✅ Complete | Quiz generation (20 MCQs + metadata) for On Campus |
| Interview | ✅ Complete | Interview questions + answers for DSA Yatra sheets |
| Aptitude | ✅ Complete | Aptitude questions + study guides for On Campus |

### Core Infrastructure (Already Built)
- `BaseAgent` — ABC with LLM init, prompt templates, content generation
- `BaseWorkflowOrchestrator` — LangGraph execution, session management, resume capability
- `BaseSessionManager` — JSON persistence, progress tracking, status management
- `@handle_node_errors` — Decorator for node error handling
- `Config` — Pydantic Settings with multi-env support (local/dev/prod)
- FastAPI routes → controllers → orchestrators → LangGraph workflows
- Background task execution with real-time progress tracking
- Session resume/restart capability (already built!)

### ❌ What's Missing

| App | Content Type | Agent Needed |
|-----|-------------|--------------|
| DSA Yatra | DSA Questions (with deep sections) | **DSA Question Agent** |
| DSA Yatra | Study Guides (intro, concept, pattern, cheatsheet) | **DSA Study Guide Agent** |
| DSA Yatra | Real-World Problems | **DSA Real-World Agent** |
| On Campus | Aptitude Questions | ✅ Exists (needs polish) |
| On Campus | Aptitude Study Guides | ✅ Exists (needs polish) |
| On Campus | Core CS Subject Content | **Core CS Agent** |
| Shiksha | Course creation (metadata + chapters in MDX) | **Course Agent** |
| Projects | Full project scaffolding (sections + chapters) | **Project Agent** |

### ❌ Architecture Gaps
1. **No LLM abstraction** — Hardcoded to OpenAI's ChatOpenAI. Need provider-agnostic layer.
2. **No chunk-wise generation** — Current workflows are all-or-nothing (generate ALL questions).
3. **No unified pipeline** — Each agent has isolated orchestration. No shared job queue.
4. **No push-to-DB integration** — Output goes to JSON files, manual copy to DB needed.
5. **No admin-driven partial runs** — Can't say "generate only 3 questions for this topic".

---

## Architecture Design

### Layer 1: LLM Provider Abstraction

```
src/core/llm/
├── __init__.py
├── base.py          ← LLMProvider ABC (generate, generate_json, stream)
├── openai.py        ← OpenAI implementation
├── anthropic.py     ← Anthropic implementation
├── registry.py      ← get_llm(provider, model) factory
└── types.py         ← LLMResponse, LLMConfig types
```

**Key Design**: 
- `get_llm(provider="openai", model="gpt-4o-mini")` → LLMProvider instance
- Support: OpenAI, Anthropic, Google Gemini, local Ollama
- Config reads API keys from existing `Config` class
- Each agent can override model at runtime

### Layer 2: Unified Content Pipeline

```
src/core/pipeline/
├── __init__.py
├── base.py          ← ContentPipeline(agent_type, session_id, config)
├── chunked.py       ← ChunkedPipeline — process N items at a time
├── job.py           ← Job dataclass (what to generate, how much, constraints)
└── push.py          ← PushToDB — POST generated content to TBE-Web API
```

**Key Design**:
- Every generation is a "Job" with: `agent_type`, `target_count`, `topic`, `constraints`, `chunk_size`
- ChunkedPipeline generates `chunk_size` items per LangGraph invocation
- After each chunk: persist to disk, update progress, allow pause/resume
- PushToDB: When admin approves, POST directly to TBE-Web admin endpoints

### Layer 3: Agent Workflows (per app)

```
src/agents/
├── base.py                 ← BaseAgent (exists, enhance with LLM abstraction)
├── quiz/                   ← ✅ Exists (refactor to use new LLM layer)
├── interview/              ← ✅ Exists (refactor)
├── aptitude/               ← ✅ Exists (refactor)
├── dsa/                    ← NEW: DSA Question + Study Guide + Real-World
│   ├── __init__.py
│   ├── workflow.py         ← LangGraph workflow (chunked generation)
│   ├── question_generator.py   ← Deep DSA question with all sections
│   ├── study_guide_generator.py ← 4-section study guides
│   ├── real_world_generator.py  ← Real-world problem generation
│   ├── prompts.py          ← All DSA prompts
│   ├── session.py          ← DSASessionManager
│   └── validators.py       ← Output schema validation
├── course/                 ← NEW: Shiksha course generation
│   ├── __init__.py
│   ├── workflow.py         ← Course outline → chapter generation pipeline
│   ├── outline_generator.py    ← Generate course structure
│   ├── chapter_generator.py    ← Generate MDX content per chapter
│   ├── prompts.py
│   ├── session.py
│   └── validators.py
├── project/                ← NEW: Project scaffolding
│   ├── __init__.py
│   ├── workflow.py         ← Idea → sections → chapters pipeline
│   ├── planner.py          ← Break idea into sections + learning path
│   ├── chapter_generator.py    ← Generate chapter content
│   ├── prompts.py
│   ├── session.py
│   └── validators.py
└── core_cs/                ← NEW: Core CS subjects for On Campus
    ├── __init__.py
    ├── workflow.py
    ├── content_generator.py
    ├── prompts.py
    ├── session.py
    └── validators.py
```

### Layer 4: API & Admin Integration

```
src/api/
├── routes/
│   ├── quiz.py             ← ✅ Exists
│   ├── interview_prep.py   ← ✅ Exists
│   ├── aptitude.py         ← ✅ Exists
│   ├── dsa.py              ← NEW
│   ├── course.py           ← NEW
│   ├── project.py          ← NEW
│   ├── core_cs.py          ← NEW
│   ├── pipeline.py         ← NEW: Unified job management
│   └── push.py             ← NEW: Push content to TBE-Web DB
├── controllers/
│   ├── ... (existing)
│   ├── dsa_controller.py   ← NEW
│   ├── course_controller.py ← NEW
│   ├── project_controller.py ← NEW
│   ├── core_cs_controller.py ← NEW
│   └── push_controller.py  ← NEW: Review + push to DB
└── models/
    ├── ... (existing)
    ├── dsa_models.py        ← NEW
    ├── course_models.py     ← NEW
    ├── project_models.py    ← NEW
    └── pipeline_models.py   ← NEW
```

---

## Data Schemas (Output Must Match TBE-Web DB)

### DSA Question Output Schema
```json
{
  "title": "Two Sum",
  "answer": "Use a hashmap to store complements...",
  "resources": {
    "youtubeURL": "",
    "leetcodeURL": "https://leetcode.com/problems/two-sum/",
    "blogURL": ""
  },
  "domain": ["CODING"],
  "difficulty": "EASY",
  "companyTypes": ["FAANG", "MNC"],
  "topics": ["ARRAY", "HASHMAP"],
  "isRealWorldProblem": false,
  "sections": {
    "first_principles": { "paragraphs": [], "key_observation": "" },
    "constraints": [{ "constraint": "", "plain_meaning": "", "implication": "" }],
    "examples": [{ "label": "", "input": "", "output": "", "explanation": "" }],
    "ways_to_solve": [{ "approach_number": 1, "name": "", "description": "", "time_complexity": "", "space_complexity": "", "verdict": "" }],
    "how_to_approach": { "steps": [{ "step_number": 1, "heading": "", "body": "" }] },
    "pseudo_code": { "code": "", "annotations": [] },
    "working_code": { "default_language": "python", "languages": { "python": { "code": "" } } },
    "common_mistakes": [{ "mistake_number": 1, "title": "", "wrong_code": "", "explanation": "", "fix": "" }]
  }
}
```

### DSA Study Guide Output Schema
```json
{
  "topicId": "array",
  "title": "Arrays - Complete Study Guide",
  "hasGuide": true,
  "sections": [
    { "type": "intro", "content": { "pageTitle": "", "subtitle": "", "openingParagraph": "", "prereqCards": [], "callouts": [] } },
    { "type": "concept", "content": { "pageTitle": "", "subsections": [{ "subheading": "", "bodyText": "", "codeBlocks": [] }] } },
    { "type": "pattern", "content": { "pageTitle": "", "whatIsIt": "", "triggerPhrases": [], "codeTemplates": [], "workedExample": {} } },
    { "type": "cheatsheet", "content": { "pageTitle": "", "patternRows": [], "decisionGuide": "", "questionGroups": [] } }
  ]
}
```

### Course Output Schema (Shiksha)
```json
{
  "name": "React Fundamentals",
  "slug": "react-fundamentals",
  "description": "...",
  "coverImageURL": "",
  "roadmap": "FRONTEND",
  "difficultyLevel": "EASY",
  "isPremium": false,
  "features": ["Free Certificate", "Hands-on Projects"],
  "chapters": [
    { "name": "Introduction to React", "content": "# MDX Content...", "isOptional": false }
  ]
}
```

### Project Output Schema
```json
{
  "name": "Build a Real-Time Chat App",
  "slug": "build-real-time-chat-app",
  "description": "...",
  "coverImageURL": "",
  "roadmap": "FULLSTACK",
  "difficultyLevel": "MEDIUM",
  "requiredSkills": ["REACT", "NODEJS", "WEBSOCKETS"],
  "sections": [
    {
      "sectionId": "uuid",
      "sectionName": "Planning & Architecture",
      "chapters": [
        { "chapterId": "uuid", "chapterName": "System Design", "content": "# MDX...", "isOptional": false }
      ]
    }
  ]
}
```

### Aptitude Question Output Schema (existing, refined)
```json
{
  "topic": "problem-on-trains",
  "questions": [
    { "question": "...", "options": ["A", "B", "C", "D"], "answer": "...", "difficulty": "EASY", "order": 1 }
  ]
}
```

---

## Implementation Plan (Phases)

### Phase 1: Core Infrastructure Refactor ✅
> Make existing system LLM-agnostic and chunk-capable

| # | Task | Status | Details |
|---|------|--------|---------|
| 1.1 | Create LLM Provider Abstraction | ✅ | `src/core/llm/` — base, openai, anthropic, registry |
| 1.2 | Refactor BaseAgent to use LLM registry | ✅ | Replace `ChatOpenAI` with `get_llm()` |
| 1.3 | Add chunk_size support to BaseSessionManager | ✅ | Track items_generated vs target_count |
| 1.4 | Create ChunkedPipeline base class | ✅ | Generate N items per invocation, persist between chunks |
| 1.5 | Create PushToDB utility | ✅ | POST to TBE-Web admin API endpoints |
| 1.6 | Add unified job queue model | ✅ | Job dataclass with status, type, constraints |
| 1.7 | Write tests for new core infra | ✅ | Unit tests with mocked LLM |

### Phase 2: DSA Yatra Agent ⬜
> Generate DSA questions, study guides, real-world problems

| # | Task | Status | Details |
|---|------|--------|---------|
| 2.1 | Create DSA Question Generator | ⬜ | Deep sections matching TBE-Web schema |
| 2.2 | Create DSA Study Guide Generator | ⬜ | 4 section types (intro, concept, pattern, cheatsheet) |
| 2.3 | Create DSA Real-World Problem Generator | ⬜ | `isRealWorldProblem: true` variant |
| 2.4 | Create DSA LangGraph Workflow | ⬜ | Chunked: generate N questions per run |
| 2.5 | Create DSA Session Manager | ⬜ | Track topic, difficulty, count, progress |
| 2.6 | Create DSA API routes + controller | ⬜ | POST /api/v1/dsa/questions, /study-guide |
| 2.7 | Create DSA Pydantic models | ⬜ | Request/response validation |
| 2.8 | Create DSA output validators | ⬜ | Validate against TBE-Web schema |
| 2.9 | Write DSA agent tests | ⬜ | Mocked LLM, schema validation |
| 2.10 | Push-to-DB: DSA questions endpoint | ⬜ | POST to `/api/v1/interview-prep/dsa-sheet/` |
| 2.11 | Push-to-DB: Study guides endpoint | ⬜ | POST to `/api/v1/interview-prep/study-guide/` |

### Phase 3: Shiksha (Course) Agent ⬜
> Generate full courses with MDX chapters

| # | Task | Status | Details |
|---|------|--------|---------|
| 3.1 | Create Course Outline Generator | ⬜ | Name, description, chapter list from topic |
| 3.2 | Create Chapter Content Generator | ⬜ | MDX content per chapter |
| 3.3 | Create Course LangGraph Workflow | ⬜ | outline → chapters (chunked, 1-3 chapters per run) |
| 3.4 | Create Course Session Manager | ⬜ | Track course, chapters generated/total |
| 3.5 | Create Course API routes + controller | ⬜ | POST /api/v1/course/generate |
| 3.6 | Create Course Pydantic models | ⬜ | Request/response schemas |
| 3.7 | Write Course agent tests | ⬜ | Mocked LLM |
| 3.8 | Push-to-DB: Course endpoint | ⬜ | POST to `/api/v1/shiksha/` |

### Phase 4: Project Agent ⬜
> Generate full project content from an idea

| # | Task | Status | Details |
|---|------|--------|---------|
| 4.1 | Create Project Planner | ⬜ | Idea → sections + learning path + skills |
| 4.2 | Create Project Chapter Generator | ⬜ | MDX content per chapter in section |
| 4.3 | Create Project LangGraph Workflow | ⬜ | plan → sections → chapters (chunked) |
| 4.4 | Create Project Session Manager | ⬜ | Track sections + chapters progress |
| 4.5 | Create Project API routes + controller | ⬜ | POST /api/v1/project/generate |
| 4.6 | Create Project Pydantic models | ⬜ | Request with idea, skills, difficulty |
| 4.7 | Write Project agent tests | ⬜ | Mocked LLM |
| 4.8 | Push-to-DB: Project endpoint | ⬜ | POST to TBE-Web project API |

### Phase 5: On Campus Enhancements ⬜
> Refine existing aptitude + add Core CS

| # | Task | Status | Details |
|---|------|--------|---------|
| 5.1 | Refactor Aptitude agent to use new LLM layer | ⬜ | Replace direct ChatOpenAI |
| 5.2 | Add chunk-wise aptitude generation | ⬜ | Generate N questions per chunk |
| 5.3 | Create Core CS Content Generator | ⬜ | Subjects like OS, DBMS, CN, OOP |
| 5.4 | Create Core CS LangGraph Workflow | ⬜ | Topic → subtopics → content |
| 5.5 | Create Core CS API routes | ⬜ | POST /api/v1/core-cs/generate |
| 5.6 | Aptitude push-to-DB integration | ⬜ | Direct POST to TBE-Web aptitude upload |
| 5.7 | Write Core CS tests | ⬜ | Mocked LLM |

### Phase 6: Admin Dashboard Integration ⬜
> tbe-admin updates for new agents

| # | Task | Status | Details |
|---|------|--------|---------|
| 6.1 | Add DSA agent API hooks in tbe-admin | ⬜ | `src/api/dsaAgentsApi.ts` |
| 6.2 | Add Course agent API hooks | ⬜ | `src/api/courseAgentsApi.ts` |
| 6.3 | Add Project agent API hooks | ⬜ | `src/api/projectAgentsApi.ts` |
| 6.4 | Create unified Agent Dashboard page | ⬜ | View all agent types, sessions, progress |
| 6.5 | Add "Push to Dev DB" button per content | ⬜ | Review → approve → push |
| 6.6 | Add "Migrate to Prod" workflow | ⬜ | Dev DB → Prod DB migration trigger |
| 6.7 | Add chunk-size controls in UI | ⬜ | "Generate 3 questions" vs "Generate 20" |

### Phase 7: Existing Agent Refactors ⬜
> Align quiz + interview to new architecture

| # | Task | Status | Details |
|---|------|--------|---------|
| 7.1 | Refactor Quiz agent to new LLM layer | ⬜ | Use `get_llm()` |
| 7.2 | Refactor Interview agent to new LLM layer | ⬜ | Use `get_llm()` |
| 7.3 | Add chunk support to Quiz workflow | ⬜ | Generate N questions at a time |
| 7.4 | Add push-to-DB for Quiz | ⬜ | POST to TBE-Web quiz API |
| 7.5 | Add push-to-DB for Interview | ⬜ | POST to TBE-Web interview API |

---

## Key Design Decisions

### 1. LLM Agnostic
```python
# Usage in any generator:
from src.core.llm import get_llm

llm = get_llm(provider="anthropic", model="claude-sonnet-4-20250514")
response = llm.generate_json(prompt, schema=DSAQuestionSchema)
```

### 2. Chunk-wise Generation
```python
# Admin requests: "Generate 3 DSA questions on Arrays, MEDIUM difficulty"
job = Job(
    agent_type="dsa_question",
    topic="ARRAY",
    target_count=3,         # Only 3, not 20
    chunk_size=3,           # All in one chunk
    difficulty="MEDIUM",
    constraints={"domain": ["CODING"], "companyTypes": ["FAANG"]}
)
```

### 3. Restartable Sessions
```python
# If generation fails at question 5/10:
# Session JSON has: { "items_generated": 5, "status": "failed", "error": "..." }
# Admin clicks "Resume" → picks up from question 6
orchestrator.resume_session(session_id)  # Already supported!
```

### 4. Push to Dev DB Flow
```
Generate → Review in Admin → Push to Dev DB → Test → Migrate to Prod
                ↓
   Admin can edit content before pushing
```

### 5. Unified Session Model
All agents share the same session lifecycle:
```
PENDING → IN_PROGRESS → (PAUSED) → COMPLETED → PUSHED_TO_DEV → MIGRATED_TO_PROD
                   ↘ FAILED → (RESUME) → IN_PROGRESS
```

---

## File Changes Needed (Existing Repos)

### The-Boring-Agents (this repo)
- [ ] Create `src/core/llm/` package (new)
- [ ] Modify `src/agents/base.py` (use LLM registry)
- [ ] Modify `src/core/config.py` (add provider configs)
- [ ] Create `src/agents/dsa/` (new)
- [ ] Create `src/agents/course/` (new)
- [ ] Create `src/agents/project/` (new)
- [ ] Create `src/agents/core_cs/` (new)
- [ ] Create `src/core/pipeline/` (new)
- [ ] Add new API routes + controllers
- [ ] Add Pydantic models for all new agents

### tbe-admin
- [ ] Add `src/api/dsaAgentsApi.ts`
- [ ] Add `src/api/courseAgentsApi.ts`
- [ ] Add `src/api/projectAgentsApi.ts`
- [ ] Add unified agent pages in `src/pages/`
- [ ] Add push-to-DB UI components

### TBE-Web (minimal)
- [ ] Ensure admin API endpoints accept agent output format
- [ ] Add `/api/v1/admin/dsa-sheet/bulk` if not exists
- [ ] Add `/api/v1/admin/shiksha/bulk` if not exists
- [ ] Add `/api/v1/admin/project/bulk` if not exists

---

## Priority Order

1. **Phase 1** (Core Infra) — MUST DO FIRST, unblocks everything
2. **Phase 2** (DSA Agent) — Highest content value, most complex schema
3. **Phase 3** (Course Agent) — High value, simpler schema (MDX)
4. **Phase 4** (Project Agent) — Similar to Course but with sections
5. **Phase 5** (On Campus) — Refine existing + add Core CS
6. **Phase 6** (Admin) — Parallel with Phase 2-5
7. **Phase 7** (Refactors) — Can be done anytime after Phase 1

---

## Success Criteria

- [ ] Can generate DSA questions with `POST /api/v1/dsa/questions` (partial: 3 or full: 20)
- [ ] Can generate study guides with `POST /api/v1/dsa/study-guide`
- [ ] Can generate full courses with `POST /api/v1/course/generate`
- [ ] Can generate projects with `POST /api/v1/project/generate`
- [ ] Can switch LLM provider via request param or env var
- [ ] Can resume failed sessions
- [ ] Can push approved content to Dev DB from admin
- [ ] Can migrate Dev → Prod from admin
- [ ] All output matches TBE-Web database schemas exactly
- [ ] Admin dashboard shows real-time progress for all agents

---

## Notes

- **Start Date**: 5 May 2026
- **Last Updated**: 5 May 2026
- **Owner**: Admin (via tbe-admin dashboard)
- **Status**: PLANNING
