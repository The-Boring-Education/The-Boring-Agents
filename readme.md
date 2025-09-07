# The Boring Agents

AI-powered content generation for The Boring Education platform.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** installed (recommended to use a virtualenv)
2. **API Keys** configured in `.env` file:
    ```bash
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    HUGGINGFACE_API_KEY=your_huggingface_key
    ```

### Installation

1. **Clone and setup**:

    ```bash
    git clone <repository-url>
    cd The-Boring-Agents

    # Create & activate virtualenv (macOS/Linux)
    python3 -m venv .venv
    source .venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt

    # If you see "ModuleNotFoundError: pydantic_settings"
    pip install pydantic-settings
    ```

2. **Configure environment**:

    Create a `.env` file in the repo root (at least one provider key is required):

    ```bash
    cat > .env <<'EOF'
    # AI Provider Keys (provide at least one)
    OPENAI_API_KEY=your_openai_key
    ANTHROPIC_API_KEY=your_anthropic_key
    HUGGINGFACE_API_KEY=your_huggingface_key

    # App behavior
    ENVIRONMENT=dev
    DEFAULT_MODEL=gpt-4o-mini
    MAX_TOKENS=4000
    TEMPERATURE=0.8
    OUTPUT_DIR=./output
    TEMP_DIR=./temp

    # Local Agents API server controls
    AGENTS_API_HOST=0.0.0.0
    AGENTS_API_PORT=8088
    RELOAD=1

    # Backend URLs used for uploads (optional)
    LOCAL_API_BASE_URL=http://localhost:3000
    DEV_API_BASE_URL=https://tbe-dev-git-development-tbe.vercel.app
    PROD_API_BASE_URL=https://www.theboringeducation.com
    EOF
    ```

3. **Test the system**:
    ```bash
    python3 main.py status
    ```

### Start the Agents API (FastAPI)

```bash
# From repo root
source .venv/bin/activate
export OPENAI_API_KEY=...  # set at least one provider key, or use .env

# Optional: override host/port
export AGENTS_API_HOST=0.0.0.0
export AGENTS_API_PORT=8088

python3 run_api.py  # FastAPI on http://localhost:8088
# Swagger UI: http://localhost:8088/docs

# Health check
curl -sS http://localhost:8088/api/v1/ping | jq

# Available topics (dynamic for Admin UI)
curl -sS http://localhost:8088/api/v1/quiz/topics | jq

# Example: Generate a quiz (cURL)
curl -sS -X POST http://localhost:8088/api/v1/quiz/generate \
  -H 'Content-Type: application/json' \
  -d '{"topic":"React","question_count":10,"target_audience":"developers","save":true,"environment":"local"}' | jq '.ok? // .quiz.questions | length?'

# Example: Create interview sheet from MDX (cURL)
curl -sS -X POST http://localhost:8088/api/v1/interview/create-sheet \
  -H 'Content-Type: application/json' \
  -d '{"mdx_file":"lab/interview-prep/python/python_requirements.mdx","agent_type":"generic","save":true}'
```

## 📁 File Structure

```
The-Boring-Agents/
├── lab/
│   └── interview-prep/          # Interview preparation files
│       ├── dsa_requirements.mdx     # Requirements for DSA interviews
│       ├── dsa_questions.mdx        # DSA questions list
│       ├── dsa_questions_with_metadata.mdx  # Questions with metadata
│       └── test_questions.mdx       # Test file for quick testing
├── src/
│   ├── agents/                 # AI agents for different tasks
│   │   ├── interview/          # Interview preparation agents
│   │   ├── project/           # Project generation agents
│   │   └── shiksha/           # Course creation agents
│   ├── core/                  # Core functionality
│   └── utils/                 # Utility functions
├── output/                    # Generated content output
├── main.py                    # CLI entry point
└── requirements.txt           # Python dependencies
```

## 🚀 Professional Automated Workflow (NEW!)

**🎯 One-Command Complete Automation** - Just provide a skill name, we handle EVERYTHING!

```bash
# Run the professional automated workflow
./scripts/interview_prep_workflow.sh
```

This launches our **production-grade workflow automation** that requires **ONLY** a skill name and automates everything else:

### ✨ **What It Does Automatically:**

-   🎯 **Smart Setup** - Just enter skill name and choose agent type
-   🤖 **Agent Selection** - Choose from generic, DSA, or tech-specific agents
-   📁 **Directory Creation** - Creates organized folder structure automatically
-   📝 **Requirements Generation** - Auto-generates comprehensive requirements MDX
-   🤖 **AI Question Generation** - Creates 100 tailored interview questions
-   📊 **Metadata Addition** - Adds difficulty, frequency, company types automatically
-   💬 **Answer Generation** - Creates detailed answers with examples and code
-   🎨 **Formatting Fix** - Cleans up MDX formatting issues automatically
-   📈 **Visual Progress** - Beautiful progress bars and status updates
-   🚨 **Error Handling** - Robust error recovery and detailed logging
-   📝 **Complete Output** - Ready-to-use interview prep sheets

### 🛡️ **Professional Features:**

-   **Simple Configuration** - Just 2 questions: skill name + agent type
-   **Agent Control** - Choose the perfect agent (generic/dsa/tech) for your needs
-   **Progress Visualization** - Real-time progress bars with percentages
-   **Comprehensive Logging** - Detailed logs for debugging and tracking
-   **Error Prevention** - Robust error handling prevents loops and failures
-   **Production Ready** - Generates industry-standard interview materials

### 📊 **Supported Technologies (Auto-Detected):**

-   **DSA** - "DSA", "Algorithms", "Data Structures", "LeetCode"
-   **Python** - "Python", auto-detects frameworks (Django, Flask, FastAPI)
-   **JavaScript** - "JavaScript", "JS", "Node.js", "React", "Vue", "Angular"
-   **Java** - "Java", auto-detects Spring, enterprise patterns
-   **DevOps** - "DevOps", "Docker", "Kubernetes", "AWS", "Cloud"
-   **Any Technology** - The system adapts to any skill you provide

### 🎯 **Super Simple Usage:**

```bash
# Launch the workflow
./scripts/interview_prep_workflow.sh

# You'll be asked 2 simple questions:
# 1. Skill/Technology name: "Python", "React", "DSA", "Java", etc.
# 2. Agent type:
#    - generic (general questions)
#    - dsa (data structures & algorithms)
#    - tech (technology-specific)

# Examples:
# ✅ "Python" + tech agent → Python tech interview sheet
# ✅ "React" + tech agent → React framework interview sheet
# ✅ "DSA" + dsa agent → Data structures & algorithms sheet
# ✅ "Java" + tech agent → Java tech interview sheet
# ✅ "System Design" + generic agent → General system design sheet

# That's it! Everything else is automated.
```

### 📁 **Auto-Generated File Structure:**

```
lab/interview-prep/
├── python/                           # Auto-created skill directory
│   ├── python_requirements.mdx       # Generated requirements template
│   ├── python_requirements_questions.mdx  # AI-generated questions
│   ├── python_requirements_questions_with_metadata.mdx  # With metadata
│   └── ...
├── java/                             # Another skill directory
├── react/                            # Frontend skill directory
└── {your-skill}/                     # Your custom skill
    ├── {skill}_requirements.mdx      # Requirements template
    ├── {skill}_requirements_questions.mdx
    └── {skill}_requirements_questions_with_metadata.mdx

output/
├── complete_sheet_{skill}.json       # Final generated sheet
├── logs/                             # Execution logs
└── ...
```

### 🔧 **Advanced Options:**

```bash
# Run just the workflow script directly (skip launcher)
./scripts/interview_prep_workflow.sh

# Manual override for specific steps
python3 main.py interview --help

# Check system status
python3 main.py status
```

### 🚨 **Troubleshooting:**

-   **Permission Issues**: Run `chmod +x scripts/interview_prep_workflow.sh`
-   **Python Errors**: Ensure you're in the right directory and virtual environment is activated
-   **API Issues**: Check your `.env` file has valid API keys
-   **Interrupted Workflow**: Check the log files in `logs/` directory for detailed error information
-   **Resume Failed Generation**: Use the individual commands from the manual workflow section

---

## 🎯 Manual Interview Preparation Workflow

For advanced users who prefer manual control, the system also supports a 4-step manual process:

### Available Agent Types

-   **`generic`** (default): General-purpose interview questions
-   **`dsa`**: Data Structures & Algorithms questions with detailed complexity analysis
-   **`tech`**: Technology-specific questions (Python, React, Java, DevOps, etc.)
-   **`system_design`**: System design questions (coming soon)

### DSA Agent Advantages

When using `--agent-type dsa`, you get:

-   **Enhanced Code Examples**: Multiple language implementations (Python, Java, C++)
-   **Detailed Complexity Analysis**: Time and space complexity with explanations
-   **Optimization Strategies**: Multiple approaches from brute force to optimal solutions
-   **Indian Context**: Examples relevant to Indian tech interviews
-   **Performance Tips**: Memory optimization and debugging strategies
-   **Real-world Applications**: Practical use cases for each algorithm
-   **Interview-specific Guidance**: Common mistakes and how to avoid them

### Tech Agent Advantages

When using `--agent-type tech`, you get:

-   **Technology-Specific Expertise**: Focused on specific technologies (Python, React, Java, DevOps, etc.)
-   **Production-Ready Examples**: Real-world code examples with best practices
-   **Framework-Specific Patterns**: Technology-specific design patterns and conventions
-   **Indian Tech Context**: Examples from Indian startups and companies (Flipkart, Paytm, Zomato)
-   **Latest Features**: Coverage of modern features and ecosystem tools
-   **Performance Optimization**: Technology-specific optimization techniques
-   **Security Considerations**: Technology-specific security best practices
-   **Deployment Strategies**: Production deployment and DevOps considerations

### Supported Technologies for Tech Agent

The tech agent supports the following technologies:

**Programming Languages:**

-   Python (Django, Flask, FastAPI, Pandas, NumPy)
-   Java (Spring Boot, Maven, Gradle)
-   JavaScript (Node.js, npm, yarn)
-   TypeScript

**Frontend Frameworks:**

-   React / React.js (Hooks, Redux, Context API)
-   Angular (RxJS, TypeScript)
-   Vue.js (Vuex, Nuxt)

**Backend Frameworks:**

-   Node.js (Express.js, npm)
-   Django (Python web framework)
-   Flask (Python microframework)
-   FastAPI (Modern Python API framework)
-   Spring Boot (Java framework)

**DevOps & Infrastructure:**

-   DevOps (CI/CD, automation)
-   Docker (containerization)
-   Kubernetes (orchestration)
-   AWS, Azure, GCP (cloud platforms)

**Usage:** Specify technology using `--technology` parameter (e.g., `--technology Python`, `--technology "React.js"`, `--technology DevOps`)

### Step 1: Create Sheet Structure

```bash
# Generic agent (default)
python3 main.py interview create-sheet-from-mdx --mdx-file lab/interview-prep/dsa_requirements.mdx

# DSA-specific agent
python3 main.py interview create-sheet-from-mdx --mdx-file lab/interview-prep/dsa_requirements.mdx --agent-type dsa

# Tech-specific agent (specify technology)
python3 main.py interview create-sheet-from-mdx --mdx-file lab/interview-prep/python_requirements.mdx --agent-type tech --technology Python

# Tech agent for React
python3 main.py interview create-sheet-from-mdx --mdx-file lab/interview-prep/react_tech_questions.mdx --agent-type tech --technology "React.js"

# Tech agent for DevOps
python3 main.py interview create-sheet-from-mdx --mdx-file lab/interview-prep/devops_tech_questions.mdx --agent-type tech --technology DevOps
```

-   Creates interview sheet structure from requirements
-   Generates metadata and topic analysis
-   Output: `./output/sheet_*.json`

### Step 2: Add Metadata to Questions

```bash
# Generic agent
python3 main.py interview add-metadata-to-mdx --mdx-file lab/interview-prep/dsa_questions.mdx

# DSA-specific agent
python3 main.py interview add-metadata-to-mdx --mdx-file lab/interview-prep/dsa_questions.mdx --agent-type dsa

# Tech-specific agent
python3 main.py interview add-metadata-to-mdx --mdx-file lab/interview-prep/python_tech_questions.mdx --agent-type tech --technology Python
```

-   Adds difficulty, frequency, priority, and company type metadata
-   Processes each question individually
-   Output: `lab/interview-prep/dsa_questions_with_metadata.mdx`

### Step 3: Generate Answers

```bash
# Generic agent
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/dsa_questions_with_metadata.mdx

# DSA-specific agent (recommended for DSA questions)
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/dsa_questions_with_metadata.mdx --agent-type dsa

# Tech-specific agent (recommended for technology questions)
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/python_tech_questions_with_metadata.mdx --agent-type tech --technology Python

# Tech agent for React questions
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/react_tech_questions_with_metadata.mdx --agent-type tech --technology "React.js"
```

-   Generates detailed answers for each question
-   **Progressive Saving**: Each answer is saved immediately after generation
-   **Resume Capability**: Can resume from interruptions (laptop sleep, network issues)
-   DSA agent includes code examples, complexity analysis, and optimization tips
-   Generic agent provides general interview guidance
-   Output: `./output/sheet_*_complete.json`

#### Progressive Saving Features

🛡️ **Interruption Protection**: Your progress is never lost!

-   **Real-time Saving**: Each question is saved immediately after generation
-   **Progress Tracking**: Visual progress bar with current question info
-   **Auto-Resume**: System detects interrupted sessions and offers to resume
-   **Error Recovery**: Continue from the last successful question even after errors
-   **Session Management**: Multiple concurrent sessions supported

#### Resume Interrupted Sessions

```bash
# List all active sessions
python3 main.py interview list-sessions --agent-type dsa

# Resume a specific session
python3 main.py interview resume-session --session-id abc123 --agent-type dsa

# Resume without specifying session (shows interactive list)
python3 main.py interview resume-session --agent-type dsa
```

### Step 4: Fix MDX Formatting (New!)

```bash
# Fix MDX formatting issues in answers
python3 scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json

# Or specify output file
python3 scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json output/fixed_sheet.json
```

-   Removes `\`\`\`mdx\n`prefix and`\n\`\`\`` suffix from all answers
-   Creates automatic backup of original file
-   Ensures proper UI display without MDX formatting artifacts
-   **Run this before pushing to database!**

### Step 5: Push to Database (New!)

```bash
# Push questions to database using the new script
python3 scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031

# With custom API URL and admin secret
python3 scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031 --api-url http://localhost:3000 --admin-secret TBEAdmin
```

-   **Professional DB Script**: Replaces the old database agent
-   **Loop & Push**: Iterates through all questions with proper error handling
-   **Progress Logging**: Real-time progress tracking with success/failure counts
-   **Error Recovery**: Continues processing even if individual questions fail
-   **Validation**: Checks question data before pushing
-   **Rate Limiting**: Includes delays to avoid overwhelming the server

### ~~Step 4: Publish to Database~~ (Deprecated)

```bash
# Old method (not recommended)
python3 main.py interview publish-sheet --sheet-file ./output/sheet_*_complete.json --sheet-id your_sheet_id --agent-type dsa
```

❌ **Use the new database push script instead** (Step 5 above)

## 🔧 Utility Scripts

### Fix MDX Formatting

**Problem Solved**: Generated answers contain `\`\`\`mdx\n` prefixes that break UI formatting.

```bash
# Fix formatting in-place (creates backup)
python3 scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json

# Create new fixed file
python3 scripts/fix_mdx_formatting.py input.json output/fixed.json
```

**Features**:

-   ✅ Removes MDX code block markers
-   ✅ Creates automatic timestamped backups
-   ✅ Progress tracking with Rich UI
-   ✅ Preserves original file structure
-   ✅ Handles large files efficiently

### Database Push

**Problem Solved**: The DB agent wasn't working properly. This is a simple, reliable script.

```bash
# Basic usage
python3 scripts/push_to_database.py output/complete_sheet_general-tech.json YOUR_SHEET_ID

# Full configuration
python3 scripts/push_to_database.py \
  output/complete_sheet_general-tech.json \
  67345538bdf619907a005031 \
  --api-url http://localhost:3000 \
  --admin-secret TBEAdmin

# Dry run (validate without pushing)
python3 scripts/push_to_database.py output/file.json SHEET_ID --dry-run
```

**Features**:

-   ✅ Professional error handling and recovery
-   ✅ Real-time progress tracking
-   ✅ Detailed success/failure logging
-   ✅ Rate limiting to protect server
-   ✅ Data validation before pushing
-   ✅ Confirmation prompts for safety
-   ✅ Comprehensive results summary

**API Compatibility**:

-   Uses the exact cURL format provided
-   Headers: `x-admin-secret`, `Content-Type: application/json`
-   Endpoint: `/api/v1/interview-prep/{sheet_id}/question`
-   Supports both HTTP 200 and 201 responses

### Complete Workflow Example

```bash
# 1. Generate answers (existing workflow)
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/dsa_questions_with_metadata.mdx --agent-type dsa

# 2. Fix MDX formatting
python3 scripts/fix_mdx_formatting.py output/complete_sheet_general-tech.json

# 3. Push to database
python3 scripts/push_to_database.py output/complete_sheet_general-tech.json 67345538bdf619907a005031 --api-url http://localhost:3000

# Done! 🎉
```

## 🛠️ Available Commands

### Content Generation

```bash
# Course outlines
python3 main.py content course-outline --topic "React Development" --level intermediate

# Video suggestions
python3 main.py content video-suggestions --topic "React" --module "State Management"

# Tips and tricks
python3 main.py content tips-and-tricks --topic "JavaScript" --level advanced
```

### Project Generation

```bash
# Create project from idea
python3 main.py projects create --idea "E-commerce Platform" --description "Build a full-stack e-commerce solution"

# Create project from MDX
python3 main.py projects create-from-mdx --mdx-file lab/project/project.mdx
```

### Session Management

```bash
# List active generation sessions
python3 main.py interview list-sessions --agent-type dsa

# Resume interrupted session
python3 main.py interview resume-session --session-id abc123 --agent-type dsa

# Resume with interactive session selection
python3 main.py interview resume-session --agent-type dsa
```

### Quiz Generation

```bash
# Generate complete quiz
python3 main.py quiz generate --topic "React" --question-count 20 --target-audience developers --save

# Validate quiz file
python3 main.py quiz validate --quiz-file output/quiz_react_abc123.json

# Upload quiz to database
python3 main.py quiz upload --quiz-file output/quiz_react_abc123.json --api-url http://localhost:3000 --admin-secret TBEAdmin

# Resume interrupted session
python3 main.py quiz resume --session-id abc123
```

### Course Creation (Shiksha) - NEW!

**🎓 Complete AI-Powered Course Generation**

```bash
# Create basic course
python3 main.py shiksha create-course --course-name "Python Backend" --description "Learn Python backend development"

# Create world-class course with research
python3 main.py shiksha create-world-class-course --course-name "Advanced React" --description "Master React patterns"

# AI/ML/Data Analysis specialized courses (NEW!)
python3 main.py shiksha create-world-class-course --course-name "Machine Learning Mastery" --description "Complete ML course for Indian developers" --roadmap "Machine Learning" --difficulty "Intermediate"

# Start the API server for web integration
python3 run_api.py
# Then access: http://localhost:8088/api/v1/shiksha/course/types
```

---

## 🎓 **SHIKSHA AGENTS - AI Course Generation System**

**The most advanced AI-powered course creation platform for Indian education!**

### 🎆 **What's New in Shiksha Agents:**

✅ **Specialized AI Agents** for AI, Machine Learning, and Data Analysis courses  
✅ **REST APIs** for web platform integration  
✅ **Indian Context Focus** - Examples from Flipkart, Zomato, Indian datasets  
✅ **Background Processing** - Create courses asynchronously  
✅ **Quality Assurance** - AI-powered content review and optimization  
✅ **Database Integration** - Direct integration with Shiksha platform  

### 🚀 **Quick Start - Shiksha API Server**

```bash
# 1. Setup environment
cp .env.example .env
# Add your API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the API server
python3 run_api.py
# Server starts at: http://localhost:8088

# 4. Test the system
curl http://localhost:8088/api/v1/shiksha/ping
```

### 📚 **Supported Course Types**

**🎓 Specializations:**
- **AI & Machine Learning** - Deep Learning, Computer Vision, NLP
- **Data Analysis** - Python Data Science, SQL Analytics, Business Intelligence  
- **Traditional Tech** - Backend, Frontend, Full Stack, DevOps
- **Emerging Tech** - Blockchain, Mobile Development, Cloud Computing

**🎯 Difficulty Levels:**
- **Beginner** - No prior experience required
- **Intermediate** - Some programming knowledge
- **Advanced** - Industry-ready, expert-level content

### 🔧 **API Endpoints**

#### **1. Course Creation (Async)**
```bash
# Create course in background
curl -X POST http://localhost:8088/api/v1/shiksha/course/create \
  -H 'Content-Type: application/json' \
  -d '{
    "course_name": "Machine Learning for Indian Startups",
    "description": "Complete ML course with Indian business cases",
    "difficulty_level": "Intermediate",
    "roadmap": "Machine Learning",
    "save_to_db": true,
    "environment": "dev"
  }'

# Response: {"ok": true, "course_id": "abc-123", "message": "Course creation initiated"}
```

#### **2. Check Course Status**
```bash
# Monitor progress
curl http://localhost:8088/api/v1/shiksha/course/status/abc-123

# Response: {
#   "ok": true,
#   "course_id": "abc-123",
#   "status": "processing",
#   "progress": 0.6,
#   "current_step": "Creating chapter content..."
# }
```

#### **3. Get Completed Course**
```bash
# Retrieve finished course
curl http://localhost:8088/api/v1/shiksha/course/result/abc-123

# Returns complete course JSON with:
# - Course structure and metadata
# - 6-8 detailed chapters
# - Mini-projects and assignments
# - Video suggestions and resources
# - Tips and tricks for each chapter
# - Research insights and market analysis
```

#### **4. Synchronous Creation (Testing)**
```bash
# Create course immediately (takes 3-5 minutes)
curl -X POST http://localhost:8088/api/v1/shiksha/course/create-sync \
  -H 'Content-Type: application/json' \
  -d '{
    "course_name": "Python Data Science",
    "description": "Data science with Indian datasets",
    "roadmap": "Data Analysis"
  }'
```

#### **5. Utility Endpoints**
```bash
# Get supported course types
curl http://localhost:8088/api/v1/shiksha/course/types

# List recent courses
curl http://localhost:8088/api/v1/shiksha/course/list

# Health check
curl http://localhost:8088/api/v1/shiksha/ping
```

### 🎨 **Web UI Integration**

**Swagger/OpenAPI Documentation:**  
🌐 http://localhost:8088/docs

**Example JavaScript Integration:**
```javascript
// Create course
const response = await fetch('http://localhost:8088/api/v1/shiksha/course/create', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    course_name: "AI for Indian Healthcare",
    description: "AI applications in Indian healthcare system",
    difficulty_level: "Intermediate",
    roadmap: "AI"
  })
});

const { course_id } = await response.json();

// Poll for completion
const checkStatus = async () => {
  const status = await fetch(`http://localhost:8088/api/v1/shiksha/course/status/${course_id}`);
  const data = await status.json();
  
  if (data.status === 'completed') {
    const result = await fetch(`http://localhost:8088/api/v1/shiksha/course/result/${course_id}`);
    const courseData = await result.json();
    console.log('Course completed:', courseData.course_data);
  } else {
    console.log(`Progress: ${(data.progress * 100).toFixed(1)}% - ${data.current_step}`);
    setTimeout(checkStatus, 5000); // Check every 5 seconds
  }
};

checkStatus();
```

### 🎆 **What Makes Shiksha Agents Special**

**1. 🇮🇳 Indian Context Focus**
- Examples from Indian companies (Flipkart, Paytm, Zomato)
- Indian datasets and use cases
- Cultural references and local relevance
- Career guidance for Indian job market

**2. 🤖 Advanced AI Orchestration**
- Research Agent - Market analysis and trends
- Content Creator - Engaging chapter content
- Exercise Creator - Practical assignments
- Quality Assurance - AI-powered review
- Instructor Agent - Teaching methodology

**3. 🎨 Rich Content Generation**
- **Chapters**: Detailed content with learning objectives
- **Mini-Projects**: 3-4 hands-on projects per chapter
- **Assignments**: 5-8 varied exercises (coding, conceptual, case studies)
- **Resources**: Curated videos, articles, and tools
- **Tips & Tricks**: Practical advice for mastering each topic

**4. 📊 Industry-Ready Output**
- Portfolio projects that impress recruiters
- Interview preparation content
- Real-world case studies
- Latest tools and frameworks
- Career guidance and freelancing tips

### 🔍 **Course Structure Example**

Here's what the AI generates for each course:

```json
{
  "name": "Machine Learning for Indian Startups",
  "description": "Complete ML course...",
  "difficulty_level": "Intermediate",
  "roadmap": "Machine Learning",
  "total_chapters": 8,
  "estimated_duration": "12-16 weeks",
  "chapters": [
    {
      "chapter_number": 1,
      "name": "ML Foundations for Indian Context",
      "content": "Detailed chapter content...",
      "learning_objectives": ["Understand ML basics", "Setup Python environment"],
      "mini_projects": [
        {
          "title": "E-commerce Recommendation Engine",
          "description": "Build a basic recommendation system...",
          "indian_context": "Based on Indian shopping patterns",
          "estimated_hours": 3,
          "skills_covered": ["Python", "pandas", "scikit-learn"]
        }
      ],
      "assignments": [
        {
          "title": "Data Preprocessing Challenge",
          "type": "Coding Challenge",
          "difficulty": "Medium",
          "estimated_time": "2 hours"
        }
      ],
      "video_suggestions": [
        {
          "title": "ML Fundamentals by Indian Creator",
          "url": "https://youtube.com/watch?v=...",
          "duration": "45 minutes",
          "why_recommended": "Great explanation with Indian examples"
        }
      ],
      "tips_and_tricks": [
        {
          "category": "Learning Strategy",
          "title": "Start with Indian Datasets",
          "content": "Use familiar data to understand concepts better",
          "indian_context": "Why this matters for Indian learners"
        }
      ]
    }
  ],
  "research_insights": {
    "key_recommendations": ["Focus on practical implementation"],
    "market_trends": ["High demand for ML in Indian fintech"]
  }
}
```

## 🎯 Quiz Generation - Professional Workflow

Create comprehensive, high-quality quizzes for any technology topic with our advanced AI-powered quiz generation system.

### 🚀 **One-Command Automated Workflow (Recommended)**

**🎯 Complete Quiz Generation** - Just provide a topic, we handle everything!

```bash
# Direct workflow script (recommended)
./scripts/quiz_generation_workflow.sh
```

This launches our **production-grade quiz workflow** that requires **ONLY** a topic name and automates everything else:

### ✨ **What It Does Automatically:**

-   🎯 **Smart Topic Analysis** - Researches the technology and its ecosystem
-   🤖 **AI Question Generation** - Creates 10-50 tailored quiz questions
-   📊 **Quality Assurance** - Includes detailed explanations and code examples
-   🎨 **Professional Formatting** - Creates properly structured quiz data
-   📈 **Visual Progress** - Beautiful progress bars and status updates
-   🚨 **Error Handling** - Robust error recovery and detailed logging
-   📁 **Auto Upload** - Optional database upload with connectivity testing
-   📝 **Complete Output** - Ready-to-use quiz files

### 🛡️ **Professional Features:**

-   **Simple Configuration** - Just enter topic and question count
-   **Target Audience Selection** - Choose from beginners, developers, or experts
-   **Progress Visualization** - Real-time progress bars with percentages
-   **Comprehensive Logging** - Detailed logs for debugging and tracking
-   **Error Recovery** - Resume interrupted sessions automatically
-   **Database Integration** - Upload directly to your quiz platform

### 📊 **Supported Topics:**

**Programming Languages:**

-   React.js, Node.js, JavaScript, TypeScript
-   Python, Java, C++, C
-   HTML, CSS, Redux

**Technologies & Frameworks:**

-   MongoDB, Express.js, SQL, NoSQL
-   Data Science, Machine Learning, Deep Learning
-   Cloud Computing, DevOps, Cyber Security
-   **Any Technology** - The system adapts to any topic you provide

### 🎯 **Super Simple Usage:**

```bash
# Launch the quiz generation workflow
./scripts/quiz_generation_workflow.sh

# You'll be asked 3 simple questions:
# 1. Quiz topic: "React", "Python", "DevOps", "Machine Learning", etc.
# 2. Number of questions: 10-50 (default: 20)
# 3. Target audience: beginners, developers (default), experts

# Examples:
# ✅ "React" + 25 questions + developers → React quiz for working professionals
# ✅ "Python" + 15 questions + beginners → Python basics quiz
# ✅ "Machine Learning" + 30 questions + experts → Advanced ML quiz
# ✅ "DevOps" + 20 questions + developers → DevOps interview prep

# That's it! Everything else is automated.
```

### 📁 **Auto-Generated File Structure:**

```
output/
├── quiz_react_a1b2c3d4.json         # Generated quiz file
├── quiz_python_e5f6g7h8.json        # Another quiz file
└── logs/                             # Execution logs
    └── quiz_workflow_20241201_143022.log

temp/
└── quiz_progress/                    # Session recovery files
    └── quiz_react_a1b2c3d4.json
```

### 🔧 **Advanced Options:**

```bash
# Make scripts executable (first time setup)
chmod +x scripts/quiz_generation_workflow.sh

# Check system status before running
python3 main.py status

# View available quiz commands and parameters
python3 main.py quiz --help

# Run the workflow
./scripts/quiz_generation_workflow.sh
```

### 🚨 **Workflow Troubleshooting:**

-   **Permission Issues**: Run `chmod +x scripts/quiz_generation_workflow.sh`
-   **Python Errors**: Ensure you're in the right directory and dependencies are installed
-   **API Issues**: Check your `.env` file has valid API keys
-   **Server Connection**: The workflow tests server connectivity before upload
-   **Interrupted Generation**: Sessions are auto-saved and can be resumed
-   **Script Not Found**: Make sure you're in the `The-Boring-Agents` directory

---

## 🎯 Manual Quiz Generation Workflow

For advanced users who prefer manual control, use individual CLI commands:

### Available Commands

```bash
# Generate complete quiz
python3 main.py quiz generate --topic "React" --question-count 20 --target-audience developers --save

# Validate quiz file
python3 main.py quiz validate --quiz-file output/quiz_react_abc123.json

# Upload to database
python3 main.py quiz upload --quiz-file output/quiz_react_abc123.json --api-url http://localhost:3000 --admin-secret TBEAdmin

python3 main.py quiz upload --quiz-file output/quiz_react.json --api-url https://tbe-dev-git-development-tbe.vercel.app --admin-secret TBEAdmin

# Resume interrupted session
python3 main.py quiz resume --session-id abc123
```

### Step 1: Generate Quiz

```bash
# Basic usage
python3 main.py quiz generate --topic "Python" --save

# With custom parameters
python3 main.py quiz generate \
  --topic "React.js" \
  --question-count 25 \
  --target-audience "developers" \
  --save

# Supported target audiences
python3 main.py quiz generate --topic "DevOps" --target-audience "beginners" --save
python3 main.py quiz generate --topic "Machine Learning" --target-audience "experts" --save
```

**Features:**

-   ✅ Comprehensive topic research and analysis
-   ✅ 10-50 questions with varying difficulty levels
-   ✅ Detailed explanations for each answer
-   ✅ Code examples and practical scenarios
-   ✅ Professional quiz structure with metadata

**Output:** `./output/quiz_{topic}_{unique_id}.json`

### Step 2: Validate Quiz Quality

```bash
# Validate quiz structure and content
python3 main.py quiz validate --quiz-file output/quiz_react_abc123.json
```

**Validation Checks:**

-   ✅ Proper JSON structure
-   ✅ Required fields present
-   ✅ Question format validation
-   ✅ Answer options validation
-   ✅ Explanation quality check

### Step 3: Upload to Database (Optional)

```bash
# Upload to local development server
python3 main.py quiz upload \
  --quiz-file output/quiz_react_abc123.json \
  --api-url http://localhost:3000 \
  --admin-secret TBEAdmin

# Upload to production server
python3 main.py quiz upload \
  --quiz-file output/quiz_react_abc123.json \
  --api-url https://www.theboringeducation.com \
  --admin-secret YOUR_ADMIN_SECRET

# The system automatically tests connectivity before upload
```

**Upload Features:**

-   ✅ Automatic connection testing
-   ✅ Server compatibility validation
-   ✅ Error handling and recovery
-   ✅ Upload progress tracking
-   ✅ Success confirmation with quiz ID

### Session Management & Recovery

#### Resume Interrupted Sessions

```bash
# List all active sessions
python3 main.py quiz resume

# Resume specific session
python3 main.py quiz resume --session-id abc123
```

**Session Features:**

-   ✅ **Automatic Session Saving**: Progress saved after each question
-   ✅ **Smart Recovery**: Detect and resume from interruptions
-   ✅ **Interactive Selection**: Choose from multiple active sessions
-   ✅ **Progress Tracking**: See exactly where you left off

#### Session Recovery Example

```bash
# 1. Start quiz generation
python3 main.py quiz generate --topic "Node.js" --question-count 30 --save
# > Generating question 15/30... [INTERRUPTED]

# 2. Resume session
python3 main.py quiz resume
# > Shows list of active sessions
# > Select session to continue from question 15

# 3. Session completes automatically
# > Quiz saved to output/quiz_nodejs_xyz789.json
```

### Complete Manual Workflow Example

```bash
# 1. Generate quiz with custom parameters
python3 main.py quiz generate \
  --topic "Machine Learning" \
  --question-count 25 \
  --target-audience "experts" \
  --save

# 2. Validate the generated quiz
python3 main.py quiz validate --quiz-file output/quiz_machine-learning_def456.json

# 3. Upload to your quiz platform
python3 main.py quiz upload \
  --quiz-file output/quiz_machine-learning_def456.json \
  --api-url http://localhost:3000 \
  --admin-secret TBEAdmin

# Done! 🎉
```

### Quiz Generation Best Practices

#### **Topic Selection Tips:**

```bash
# ✅ Good topics
python3 main.py quiz generate --topic "React Hooks" --save
python3 main.py quiz generate --topic "Python Django" --save
python3 main.py quiz generate --topic "Docker Containerization" --save

# ✅ Specific technologies work better than general terms
python3 main.py quiz generate --topic "Express.js" --save  # Better than "Backend"
python3 main.py quiz generate --topic "MongoDB" --save     # Better than "Database"
```

#### **Target Audience Guidelines:**

-   **`beginners`**: New to the technology, basic concepts, simple examples
-   **`developers`**: Working professionals, practical scenarios, real-world applications
-   **`experts`**: Advanced concepts, optimization, edge cases, architectural decisions

#### **Question Count Recommendations:**

-   **10-15 questions**: Quick assessment, specific topic focus
-   **20-25 questions**: Standard comprehensive quiz
-   **30-50 questions**: Detailed examination, multiple subtopics

### Troubleshooting Quiz Generation

#### **Common Issues & Solutions:**

```bash
# ❌ API Connection Failed
python3 main.py quiz upload --quiz-file output/quiz.json --api-url http://localhost:3000
# Solution: Start your local server first or check network connectivity

# ❌ Generation Interrupted
python3 main.py quiz generate --topic "React" --question-count 30
# Solution: Use resume command to continue
python3 main.py quiz resume

# ❌ Invalid Quiz File
python3 main.py quiz validate --quiz-file output/corrupted_quiz.json
# Solution: Check validation output for specific issues

# ❌ Server Not Running
# Solution: Start your development server
cd your-server-directory && npm start
# Or use the development/production URLs instead of localhost
```

#### **API Server Setup:**

```bash
# For local development
# 1. Start your Next.js development server
cd tbe-webapp && npm run dev
# Server runs on http://localhost:3000

# 2. Use the correct API URL in upload command
python3 main.py quiz upload \
  --quiz-file output/quiz.json \
  --api-url http://localhost:3000

# For production deployment
python3 main.py quiz upload \
  --quiz-file output/quiz.json \
  --api-url https://www.theboringeducation.com
```

### Quiz Data Structure

Generated quiz files follow this structure:

```json
{
    "quiz": {
        "categoryId": "unique_category_id",
        "categoryName": "React.js",
        "categoryDescription": "React.js quiz for developers",
        "categoryIcon": "⚛️",
        "isActive": true,
        "questions": [
            {
                "question": "What is the purpose of React hooks?",
                "options": [
                    "To manage component state",
                    "To handle side effects",
                    "To reuse stateful logic",
                    "All of the above"
                ],
                "correctAnswer": 3,
                "explanation": "Brief explanation",
                "detailedExplanation": "Comprehensive explanation with examples",
                "difficulty": "medium"
            }
        ]
    },
    "metadata": {
        "totalQuestions": 20,
        "difficultyDistribution": {
            "easy": 6,
            "medium": 10,
            "hard": 4
        },
        "generatedAt": "2024-01-15T10:30:00Z",
        "qualityScore": 8.5
    }
}
```

## 🔧 API Features

### Environment Tracking

The Agents API now tracks which environment requests originate from:

-   **Quiz Generation**: Includes environment info in logs and responses
-   **Quiz Upload**: Tracks environment for platform integration
-   **Enhanced Logging**: All operations log environment context for debugging

### Enhanced Logging

-   **Structured Logging**: All API operations include detailed context
-   **Environment Context**: Requests include environment information (local/dev/prod)
-   **Error Tracking**: Comprehensive error logging with environment details
-   **Performance Monitoring**: Request timing and success/failure tracking

### Health & Monitoring

-   **Health Check**: `GET /api/v1/ping` for service status
-   **Topics Endpoint**: `GET /api/v1/quiz/topics` for dynamic Admin UI integration
-   **Environment Awareness**: Automatic environment detection and logging

## 🔧 Configuration

### Environment Variables

-   `ENVIRONMENT`: `local`, `dev`, or `prod`
-   `DEFAULT_MODEL`: AI model to use (default: `gpt-4o-mini`)
-   `MAX_TOKENS`: Maximum tokens per request (default: `4000`)
-   `TEMPERATURE`: AI creativity level (default: `1.0`)

### API URLs

-   **Local**: `http://localhost:3000`
-   **Development**: `https://tbe-dev-git-development-tbe.vercel.app`
-   **Production**: `https://www.theboringeducation.com`

## 📝 File Formats

### MDX Files

-   **Requirements**: Define interview context, difficulty, target audience
-   **Questions**: List of interview questions (numbered)
-   **Questions with Metadata**: Questions + difficulty, frequency, priority, company types

### JSON Output

-   **Sheet Structure**: Interview sheet metadata and structure
-   **Complete Sheet**: Full sheet with questions and answers
-   **Project Data**: Complete project specifications and content

## 🚨 Important Notes

1. **Progressive Saving**: Answer generation now saves progress after each question. You can safely interrupt and resume sessions.

2. **Sheet Publishing**: The `publish-sheet` command only adds questions to existing sheets. If the sheet doesn't exist, it will throw an error.

3. **File Paths**: All interview files should be placed in `lab/interview-prep/` directory.

4. **Processing Time**: Large question sets (50+ questions) may take significant time to process, but progress is saved continuously.

5. **API Limits**: Monitor your API usage, especially for large question sets.

6. **Session Recovery**: Progress files are stored in `./temp/` directory and automatically cleaned up after successful completion.

## 🧪 Testing

Use the test file for quick verification:

```bash
# Test metadata addition
python3 main.py interview add-metadata-to-mdx --mdx-file lab/interview-prep/test_questions.mdx

# Test answer generation
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/test_questions_with_metadata.mdx
```

## 🤝 Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include logging for debugging
4. Test with small datasets first
5. Update documentation for new features

## 📞 Support

For issues or questions:

1. Check the system status: `python3 main.py status`
2. Verify API keys are configured
3. Test with the provided test files
4. Review logs for detailed error messages
