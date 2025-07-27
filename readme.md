# The Boring Agents

AI-powered content generation for The Boring Education platform.

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
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
    pip install -r requirements.txt
    ```

2. **Configure environment**:

    ```bash
    cp .env.example .env
    # Edit .env with your API keys
    ```

3. **Test the system**:
    ```bash
    python3 main.py status
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

**🎯 One-Command Complete Automation** - No more manual steps!

```bash
# Run the professional automated workflow
./interview-prep.sh
```

This launches our **production-grade workflow automation** that:

### ✨ **What It Does Automatically:**

-   🎯 **Interactive Setup** - Asks skill name, agent type, technology focus
-   📁 **Auto Directory Creation** - Creates proper folder structure
-   📝 **Requirements Template** - Generates customizable requirements file
-   🤖 **AI Question Generation** - Creates 50-100 interview questions
-   📊 **Metadata Addition** - Adds difficulty, frequency, company types
-   💬 **Answer Generation** - Creates detailed answers with examples
-   🎨 **Formatting Fix** - Cleans up MDX formatting issues
-   🚀 **Database Publishing** - Optionally publishes to live database
-   📋 **Progress Tracking** - Beautiful visual progress indicators
-   📝 **Comprehensive Logging** - Detailed execution logs
-   🔄 **Error Recovery** - Graceful failure handling and recovery options

### 🛡️ **Professional Features:**

-   **Error Handling** - Recovers from failures gracefully
-   **Progress Visualization** - Real-time progress bars and status
-   **Configuration Validation** - Checks system requirements
-   **Logging System** - Detailed logs for debugging
-   **Interactive Prompts** - User-friendly configuration
-   **Resume Capability** - Can resume interrupted workflows

### 📊 **Supported Workflows:**

-   **DSA Sheets** - Data structures & algorithms with complexity analysis
-   **Tech Sheets** - Python, Java, React, DevOps, Node.js, Angular, etc.
-   **Generic Sheets** - General purpose interview questions
-   **Custom Skills** - Any technology you specify

### 🎯 **Example Usage:**

```bash
# Launch the workflow
./interview-prep.sh

# Follow the interactive prompts:
# 1. Enter skill name (e.g., "Python", "React", "DevOps")
# 2. Choose agent type (generic/dsa/tech)
# 3. Set technology focus (for tech agent)
# 4. Configure database publishing
# 5. Sit back and watch it work!
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

-   **Permission Issues**: Run `chmod +x interview-prep.sh` and `chmod +x scripts/interview_prep_workflow.sh`
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

### Course Creation (Shiksha)

```bash
# Create basic course
python3 main.py shiksha create-course --course-name "Python Backend" --description "Learn Python backend development"

# Create world-class course with research
python3 main.py shiksha create-world-class-course --course-name "Advanced React" --description "Master React patterns"
```

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
