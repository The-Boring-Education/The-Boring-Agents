# The Boring Agents

AI-powered content generation system for The Boring Education, designed to accelerate the creation of educational content across multiple products.

## Overview

The Boring Agents is a Python-based AI agent system that automates content generation for:

1. **Shiksha** - Tech courses with curated video content, text materials, tips and tricks
2. **Interview Prep** - Comprehensive question sheets in various formats for different technologies
3. **Projects** - Real-life project ideas with detailed implementation guides

## Features

### Content Generation (Shiksha)

-   📚 Complete course outlines with learning objectives
-   🎥 Video content suggestions and curation
-   📝 Detailed text content with tips and tricks
-   💡 Best practices and common pitfalls
-   🛠️ Practical examples and code snippets
-   🎓 **NEW: Complete Shiksha course generation with multi-agent system**
-   📋 **NEW: Comprehensive chapter planning and content creation**
-   🔍 **NEW: Quality assurance and content refinement**

### Interview Preparation

-   ❓ Technical question sheets with detailed answers
-   💻 Coding challenges with multiple solutions
-   🗣️ Behavioral interview questions with STAR method guidance
-   🏗️ System design questions with architecture examples
-   📋 Complete interview prep packages
-   🇮🇳 **NEW: Indian context integration with humor and cultural references**
-   🎯 **NEW: World-class answer structure with code examples**
-   📊 **NEW: Frequency analysis and company-specific insights**

### Project Ideas & Implementation

-   💡 **2-Parameter Simplicity**: Just provide idea + description, AI handles everything else
-   🤖 **AI-Powered Intelligence**: Auto-determines tech stack, difficulty, and roadmap
-   🎯 **Domain-Aware**: Understands 20+ domains (fintech, edtech, healthtech, etc.)
-   🏗️ **Production-Ready**: Detailed technical architecture and implementation guides
-   📋 **Career-Focused**: Every project includes salary impact and skill development
-   🗓️ **Complete Roadmaps**: Step-by-step timelines with practical assignments
-   💼 **Portfolio Optimization**: Projects designed to boost career prospects
-   📄 **MDX Support**: Create projects from markdown files for version control

## Quick Start

### Installation

1. Clone the repository:

```bash
git clone https://github.com/The-Boring-Education/The-Boring-Agents.git
cd The-Boring-Agents
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:

```bash
cp .env.example .env
# Edit .env and add your API keys
```

4. Activate the virtual environment (if using one):

```bash
# For virtualenv
source venv/bin/activate
```

### Basic Usage

#### Generate Course Content

```bash
# Create course outline
python main.py content course-outline --topic "Python Web Development" --level intermediate

# Generate video suggestions
python main.py content video-suggestions --topic "Django" --module "Authentication & Authorization"

# Get tips and tricks
python main.py content tips-and-tricks --topic "React" --level advanced

# NEW: Generate complete Shiksha course
python main.py shiksha create-course --course-name "Zero to One Frontend Development" --description "Master React.js from basics to advanced concepts" --difficulty Beginner --roadmap Frontend --save

# NEW: Generate world-class Shiksha course with Indian context
python main.py shiksha create-world-class-course --course-name "Advanced React Development for Indian Developers" --description "Build production-ready React apps with Indian startup examples and career guidance" --difficulty Advanced --roadmap Frontend --save
```

#### Create Interview Prep Materials

```bash
# Generate question sheet
python main.py interview question-sheet --technology "JavaScript" --count 30

# Create coding challenges
python main.py interview coding-challenges --technology "Python" --difficulty hard

# Complete interview package
python main.py interview complete-prep --technology "Node.js"

# NEW: Revamp existing interview sheet with world-class quality
python main.py interview revamp-sheet --sheet-id "673333d146a1961fc8b84345" --save

# NEW: Create new world-class interview sheet from scratch
python main.py interview create-world-class-sheet --sheet-name "React Advanced Concepts" --description "Master advanced React patterns, hooks, and performance optimization for Indian startups" --target-questions 50 --save

# NEW: Batch revamp all interview sheets (use with caution!)
python main.py interview revamp-all-sheets --save
```

#### Generate Intelligent Project Ideas

The AI automatically determines the best tech stack, difficulty level, and roadmap based on:

-   **Project Idea & Description**: AI analyzes your concept to determine everything else
-   **Smart Domain Detection**: Automatically identifies if it's fintech, edtech, healthtech, etc.
-   **Intelligent Tech Stack**: Chooses the optimal technologies for your project
-   **Dynamic Difficulty**: Determines complexity based on project requirements
-   **Target Audience**: Auto-determines user profile and career goals

```bash
# Create a project with just an idea and description (AI determines everything else)
python main.py projects create --idea "Food delivery app for college students" --description "Build a mobile app that lets college students order food from campus cafeterias and nearby restaurants with group ordering features and split payment options" --save

# Create project from an MDX file
python main.py projects create-from-mdx --mdx-file "./project-idea.mdx" --save
```

**Example MDX File Format:**

```markdown
# Project Idea: Smart Campus Food Delivery App

## Description

Build a comprehensive food delivery platform specifically designed for college campuses. The app should solve the unique challenges students face:

-   **Group Ordering**: Allow multiple students to order together from the same restaurant
-   **Split Payments**: Integrate with UPI and digital wallets for easy payment splitting
-   **Campus Integration**: Work with campus cafeterias and nearby restaurants
-   **Student Budget**: Focus on affordable options and student discounts
-   **Delivery Coordination**: Smart delivery to dorms and common areas

The app should be mobile-first, work with slow internet connections, and integrate with popular Indian payment methods like UPI, Paytm, and GPay.
```

**🤖 AI Auto-Determines:**

-   Domain: Food delivery / EdTech
-   Tech Stack: React Native, Node.js, MongoDB, UPI APIs
-   Difficulty: Intermediate
-   Target Role: Full Stack Mobile Developer
-   Roadmap: Full Stack
-   Career Impact: 20-30% salary boost potential

**🎯 Pro Engineering Approach:**

-   **Just 2 Parameters**: Only idea and description needed - AI handles the rest
-   **Intelligent Analysis**: AI analyzes your concept to determine optimal tech stack
-   **Domain Expertise**: AI understands 20+ domains (fintech, edtech, healthtech, etc.)
-   **Career-Focused**: Every project includes salary impact analysis and skill development
-   **Indian Context**: Projects tailored for Indian market and job requirements

## Project Structure

```
the_boring_agents/
├── __init__.py                 # Package initialization
├── agents/                     # AI agent implementations
│   ├── __init__.py
│   ├── content_agent.py        # General content generation
│   ├── shiksha/               # Shiksha course agents
│   │   ├── __init__.py
│   │   ├── enhanced_shiksha_orchestrator.py
│   │   ├── shiksha_orchestrator.py
│   │   ├── course_planner_agent.py
│   │   ├── content_creator_agent.py
│   │   ├── quality_assurance_agent.py
│   │   ├── research_agent.py
│   │   ├── instructor_agent.py
│   │   └── exercise_creator_agent.py
│   ├── interview/              # Interview preparation agents
│   │   ├── __init__.py
│   │   ├── interview_agent.py
│   │   ├── interview_sheet_orchestrator.py
│   │   ├── answer_enhancement_agent.py
│   │   ├── database_integration_agent.py
│   │   ├── frequency_analysis_agent.py
│   │   ├── question_generator_agent.py
│   │   ├── interview_research_agent.py
│   │   ├── quality_review_agent.py
│   │   └── mdx_styling_agent.py
│   └── project/                # Project generation agents
│       ├── __init__.py
│       └── project_agent.py
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   └── config.py              # Configuration management
└── utils/                      # Utility functions
    ├── __init__.py
    └── helpers.py              # Helper functions

main.py                         # CLI entry point
requirements.txt                # Python dependencies
.env.example                    # Environment template
.gitignore                      # Git ignore rules
```

## Configuration

The system uses environment variables for configuration. Key settings:

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional

# Application Settings
LOG_LEVEL=INFO
OUTPUT_DIR=./output
DEFAULT_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=2000
```

## Advanced Usage

### Programmatic API

```python
from the_boring_agents.agents import ContentAgent, InterviewAgent, ProjectAgent

# Initialize agents
content_agent = ContentAgent()
interview_agent = InterviewAgent()
project_agent = ProjectAgent()

# Generate content
course = content_agent.create_course_outline("Machine Learning", "beginner")
questions = interview_agent.create_question_sheet("Python", "intermediate", 20)
projects = project_agent.generate_project_ideas("Vue.js", "medium", 3, "fintech")

# Save results
content_agent.save_content(course, "ml_course_outline")
interview_agent.save_content(questions, "python_interview_questions")
project_agent.save_content(projects, "vuejs_fintech_projects")
```

### Extending the System

Create custom agents by extending the `BaseAgent` class:

```python
from the_boring_agents.core.base_agent import BaseAgent
from langchain.prompts import PromptTemplate

class CustomAgent(BaseAgent):
    def _get_prompt_templates(self):
        return {
            "custom_template": PromptTemplate(
                input_variables=["param1", "param2"],
                template="Custom prompt with {param1} and {param2}"
            )
        }

    def generate_content(self, **kwargs):
        # Custom generation logic
        pass
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Architecture Decisions

### Framework Choice: Langchain

-   **Mature ecosystem** with extensive LLM integrations
-   **Modular design** supporting multiple providers (OpenAI, Anthropic, etc.)
-   **Rich prompt templating** system for consistent content generation
-   **Built-in parsing** and output formatting capabilities
-   **Active community** and regular updates

### Design Principles

-   **Simplicity First** - Just 2 parameters (idea + description) for maximum usability
-   **AI-Powered Intelligence** - Let AI handle complex decisions about tech stack and difficulty
-   **Domain Expertise** - Deep understanding of 20+ industries and their requirements
-   **Career-Focused** - Every output designed to boost professional growth
-   **Modular Architecture** - Each product type has its own specialized agent
-   **CLI-First Approach** - Simple command-line interface for quick usage
-   **Structured Output** - Consistent JSON format for easy integration
-   **Configuration-Driven** - Environment-based settings for flexibility

## Roadmap

-   [ ] **Multi-language support** for international content
-   [ ] **Content templates** and customization options
-   [ ] **Batch processing** for large-scale content generation
-   [ ] **Web dashboard** for non-technical users
-   [ ] **Integration APIs** for external systems
-   [ ] **Content quality metrics** and validation
-   [ ] **Collaborative features** for team content creation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:

-   📧 Email: support@theboring.education
-   💬 Discord: [The Boring Education Community](https://discord.gg/boring-education)
-   📖 Documentation: [docs.theboring.education](https://docs.theboring.education)

---

Built with ❤️ by The Boring Education Team
