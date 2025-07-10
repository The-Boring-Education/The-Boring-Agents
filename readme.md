# The Boring Agents

AI-powered content generation system for The Boring Education, designed to accelerate the creation of educational content across multiple products.

## Overview

The Boring Agents is a Python-based AI agent system that automates content generation for:

1. **Shiksha** - Tech courses with curated video content, text materials, tips and tricks
2. **Interview Prep** - Comprehensive question sheets in various formats for different technologies  
3. **Projects** - Real-life project ideas with detailed implementation guides

## Features

### Content Generation (Shiksha)
- 📚 Complete course outlines with learning objectives
- 🎥 Video content suggestions and curation
- 📝 Detailed text content with tips and tricks
- 💡 Best practices and common pitfalls
- 🛠️ Practical examples and code snippets

### Interview Preparation
- ❓ Technical question sheets with detailed answers
- 💻 Coding challenges with multiple solutions
- 🗣️ Behavioral interview questions with STAR method guidance  
- 🏗️ System design questions with architecture examples
- 📋 Complete interview prep packages

### Project Ideas & Implementation
- 💡 Real-world project ideas across different domains
- 🏗️ Detailed technical architecture designs
- 📋 Step-by-step implementation guides
- 🗓️ Project roadmaps and timelines
- 💼 Portfolio optimization recommendations

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

### Basic Usage

#### Generate Course Content
```bash
# Create course outline
python main.py content course-outline --topic "Python Web Development" --level intermediate

# Generate video suggestions  
python main.py content video-suggestions --topic "Django" --module "Authentication & Authorization"

# Get tips and tricks
python main.py content tips-and-tricks --topic "React" --level advanced
```

#### Create Interview Prep Materials
```bash
# Generate question sheet
python main.py interview question-sheet --technology "JavaScript" --count 30

# Create coding challenges
python main.py interview coding-challenges --technology "Python" --difficulty hard

# Complete interview package
python main.py interview complete-prep --technology "Node.js"
```

#### Generate Project Ideas
```bash
# Get project ideas
python main.py projects ideas --technology "React" --domain "e-commerce"

# Create project architecture
python main.py projects architecture --project "Social Media App" --technologies "MERN Stack"

# Complete project package
python main.py projects complete-package --technology "Django" --difficulty advanced
```

## Project Structure

```
the_boring_agents/
├── __init__.py                 # Package initialization
├── agents/                     # AI agent implementations
│   ├── __init__.py
│   ├── content_agent.py        # Shiksha content generation
│   ├── interview_agent.py      # Interview prep materials
│   └── project_agent.py        # Project ideas & guides
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
- **Mature ecosystem** with extensive LLM integrations
- **Modular design** supporting multiple providers (OpenAI, Anthropic, etc.)
- **Rich prompt templating** system for consistent content generation
- **Built-in parsing** and output formatting capabilities
- **Active community** and regular updates

### Design Principles
- **Modular architecture** - Each product type has its own specialized agent
- **Extensible base classes** - Easy to add new agent types
- **Configuration-driven** - Environment-based settings for flexibility
- **CLI-first approach** - Simple command-line interface for quick usage
- **Structured output** - Consistent JSON format for easy integration

## Roadmap

- [ ] **Multi-language support** for international content
- [ ] **Content templates** and customization options  
- [ ] **Batch processing** for large-scale content generation
- [ ] **Web dashboard** for non-technical users
- [ ] **Integration APIs** for external systems
- [ ] **Content quality metrics** and validation
- [ ] **Collaborative features** for team content creation

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:
- 📧 Email: support@theboring.education
- 💬 Discord: [The Boring Education Community](https://discord.gg/boring-education)
- 📖 Documentation: [docs.theboring.education](https://docs.theboring.education)

---

Built with ❤️ by The Boring Education Team
