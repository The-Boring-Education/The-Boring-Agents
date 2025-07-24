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

## 🎯 Interview Preparation Workflow

The interview preparation system follows a 4-step process:

### Step 1: Create Sheet Structure

```bash
python3 main.py interview create-sheet-from-mdx --mdx-file lab/interview-prep/dsa_requirements.mdx
```

-   Creates interview sheet structure from requirements
-   Generates metadata and topic analysis
-   Output: `./output/sheet_*.json`

### Step 2: Add Metadata to Questions

```bash
python3 main.py interview add-metadata-to-mdx --mdx-file lab/interview-prep/dsa_questions.mdx
```

-   Adds difficulty, frequency, priority, and company type metadata
-   Processes each question individually
-   Output: `lab/interview-prep/dsa_questions_with_metadata.mdx`

### Step 3: Generate Answers

```bash
python3 main.py interview generate-answers-from-mdx --mdx-file lab/interview-prep/dsa_questions_with_metadata.mdx
```

-   Generates detailed answers for each question
-   Includes code examples, explanations, and best practices
-   Output: `./output/sheet_*_complete.json`

### Step 4: Publish to Database

```bash
python3 main.py interview publish-sheet --sheet-file ./output/sheet_*_complete.json --sheet-id your_sheet_id
```

-   Validates and publishes sheet to database
-   Adds questions to existing sheet (doesn't create new sheet)
-   Requires sheet ID to exist in database

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

1. **Sheet Publishing**: The `publish-sheet` command only adds questions to existing sheets. If the sheet doesn't exist, it will throw an error.

2. **File Paths**: All interview files should be placed in `lab/interview-prep/` directory.

3. **Processing Time**: Large question sets (50+ questions) may take significant time to process.

4. **API Limits**: Monitor your API usage, especially for large question sets.

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
