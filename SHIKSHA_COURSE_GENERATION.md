# Shiksha Course Generation System

## Overview

The Shiksha Course Generation System is a multi-agent AI system designed to create complete tech courses for The Boring Education's Shiksha platform. It follows the exact JSON schema used by Shiksha and generates comprehensive courses with all required components.

## Architecture

### Multi-Agent System

The system uses a coordinated approach with specialized agents:

1. **ShikshaOrchestrator** - Main coordinator that manages the entire process
2. **CoursePlannerAgent** - Plans course structure and chapter breakdown
3. **ContentCreatorAgent** - Generates chapter content in MDX format
4. **QualityAssuranceAgent** - Reviews and refines content quality

### Course Structure

Each generated course follows the Shiksha JSON schema:

```json
{
    "status": true,
    "data": {
        "_id": "unique_course_id",
        "name": "Course Name",
        "slug": "course-slug",
        "coverImageURL": "https://ik.imagekit.io/tbe/webapp/shiksha-slug-cover.svg",
        "description": "Course description",
        "liveOn": "2025-01-31T06:00:00.000Z",
        "roadmap": "Backend",
        "difficultyLevel": "Beginner",
        "chapters": [
            {
                "name": "Chapter Name",
                "content": "MDX formatted content",
                "_id": "unique_chapter_id",
                "createdAt": "2025-01-29T09:01:09.636Z",
                "updatedAt": "2025-01-29T09:01:09.636Z"
            }
        ],
        "meta": "Introduction text",
        "isPremium": true,
        "price": 1,
        "features": [],
        "isEnrolled": false
    }
}
```

## Chapter Content Structure

Each chapter includes:

1. **Chapter Introduction** - Why this topic is important
2. **Why Do You Need This?** - Real-world importance
3. **How Important Is It?** - Industry relevance
4. **How Long Will It Take?** - Time estimates
5. **Tutorial Section** - Curated YouTube videos
6. **Projects to Build** - Practical projects
7. **Share It On Social Media** - LinkedIn and Twitter templates
8. **Tips and Best Practices** - Practical advice
9. **Practice Problems** - Hands-on exercises

## Usage

### Command Line Interface

```bash
# Create a complete Shiksha course
python main.py shiksha create-course \
  --course-name "Zero to One Backend Development" \
  --description "Master Node.js and Express.js from basics to advanced concepts" \
  --difficulty Beginner \
  --roadmap Backend \
  --save
```

### Programmatic Usage

```python
from the_boring_agents.agents import ShikshaOrchestrator

# Initialize the orchestrator
orchestrator = ShikshaOrchestrator()

# Create a complete course
course_data = orchestrator.create_complete_course(
    course_name="Zero to One Frontend Development with React",
    description="Master React.js from basics to advanced concepts. Build real projects and become a frontend developer.",
    difficulty_level="Beginner",
    roadmap="Frontend"
)

# Save the course
filepath = orchestrator.save_course(course_data)
print(f"Course saved to: {filepath}")
```

## Agent Details

### CoursePlannerAgent

**Purpose**: Plans course structure and chapter breakdown

**Key Features**:

-   Creates logical course progression
-   Defines learning objectives for each chapter
-   Estimates time requirements
-   Identifies prerequisites

**Usage**:

```python
from the_boring_agents.agents import CoursePlannerAgent

planner = CoursePlannerAgent()
course_plan = planner.create_course_structure(
    course_name="Python Web Development",
    description="Learn Python web development with Django and Flask",
    difficulty_level="Intermediate",
    roadmap="Backend"
)
```

### ContentCreatorAgent

**Purpose**: Generates comprehensive chapter content in MDX format

**Key Features**:

-   Creates engaging chapter content
-   Curates high-quality YouTube videos
-   Generates social media templates
-   Creates practice problems
-   Enhances content with various components

**Usage**:

```python
from the_boring_agents.agents import ContentCreatorAgent

creator = ContentCreatorAgent()
chapter_content = creator.create_chapter_content(
    chapter_name="Introduction to React",
    course_name="React Development",
    chapter_number=1,
    total_chapters=15,
    difficulty_level="Beginner",
    learning_objectives=["Understand React basics", "Learn JSX syntax"],
    key_concepts=["Components", "JSX", "Props"]
)
```

### QualityAssuranceAgent

**Purpose**: Reviews and refines content quality

**Key Features**:

-   Reviews course structure and flow
-   Evaluates content quality and engagement
-   Provides specific recommendations
-   Validates final course JSON
-   Refines content based on feedback

**Usage**:

```python
from the_boring_agents.agents import QualityAssuranceAgent

qa = QualityAssuranceAgent()
review_results = qa.review_course_structure(
    course_data, course_name, difficulty_level
)

if review_results.get("overall_score", 0) < 7.0:
    # Refine the course based on feedback
    refined_course = qa.refine_content(
        course_data, review_results.get("recommendations", [])
    )
```

## Content Generation Process

### Step 1: Course Planning

-   Analyzes course requirements
-   Creates logical chapter progression
-   Defines learning objectives
-   Estimates time requirements

### Step 2: Meta Content Generation

-   Creates engaging course introduction
-   Highlights real-world applications
-   Sets learning expectations
-   Motivates learners

### Step 3: Chapter Content Creation

-   Generates comprehensive MDX content
-   Curates high-quality YouTube videos
-   Creates social media templates
-   Develops practice problems
-   Includes tips and best practices

### Step 4: Quality Assurance

-   Reviews overall course structure
-   Evaluates individual chapters
-   Provides improvement recommendations
-   Validates final output

### Step 5: Content Refinement

-   Applies feedback from QA review
-   Enhances content quality
-   Ensures proper formatting
-   Validates against Shiksha schema

## Video Curation Criteria

The system curates YouTube videos based on:

-   **Recency**: Videos not older than 2 years
-   **Quality**: Good view counts (10K+ views preferred)
-   **Content**: Practical, hands-on approach
-   **Clarity**: Well-structured and clear content
-   **Language**: English language content
-   **Relevance**: Directly related to chapter topics

## Social Media Templates

Each chapter includes ready-to-use templates for:

### LinkedIn Posts

-   Professional tone
-   Key learning points
-   Career impact
-   Call to action
-   Relevant hashtags

### Twitter Posts

-   Concise, engaging content
-   Key achievements
-   Learning journey focus
-   Relevant hashtags

## Testing

### Run the Test Suite

```bash
# Test the complete system
python test_shiksha_course.py

# Test individual components
python test_structure.py
```

### Test Individual Agents

```python
# Test course planning
planner = CoursePlannerAgent()
plan = planner.create_course_structure("Test Course", "Description", "Beginner", "Backend")

# Test content creation
creator = ContentCreatorAgent()
content = creator.create_chapter_content("Test Chapter", "Test Course", 1, 10, "Beginner")

# Test quality assurance
qa = QualityAssuranceAgent()
review = qa.review_chapter_content(content, "Test Chapter", "Test Course", "Beginner")
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_api_key_here
LOG_LEVEL=INFO
OUTPUT_DIR=./output
DEFAULT_MODEL=gpt-3.5-turbo
TEMPERATURE=0.7
MAX_TOKENS=2000
```

### Model Settings

-   **Default Model**: gpt-3.5-turbo
-   **Temperature**: 0.7 (balanced creativity and consistency)
-   **Max Tokens**: 2000 (sufficient for chapter content)
-   **Output Format**: Structured JSON and MDX

## Output Files

Generated courses are saved as JSON files in the output directory:

```
output/
├── shiksha_course_zero_to_one_frontend_development_20250129_143022.json
├── shiksha_course_python_web_development_20250129_150145.json
└── ...
```

## Quality Metrics

The system evaluates courses on:

1. **Structure & Flow** (1-10)

    - Logical progression
    - Appropriate difficulty
    - Complete coverage

2. **Content Quality** (1-10)

    - Engaging explanations
    - Practical approach
    - Real-world relevance

3. **Learning Experience** (1-10)

    - Clear objectives
    - Appropriate time estimates
    - Effective video curation

4. **Technical Accuracy** (1-10)

    - Correct information
    - Up-to-date content
    - Proper code examples

5. **Engagement & Motivation** (1-10)
    - Inspiring content
    - Clear value proposition
    - Social sharing elements

## Best Practices

### Course Creation

1. **Clear Course Names**: Use descriptive, engaging names
2. **Detailed Descriptions**: Explain what learners will gain
3. **Appropriate Difficulty**: Match content to target audience
4. **Relevant Roadmap**: Choose appropriate category

### Content Quality

1. **Engaging Tone**: Write conversationally and inspirationally
2. **Practical Focus**: Emphasize real-world applications
3. **Progressive Difficulty**: Build from basics to advanced
4. **Hands-on Projects**: Include practical exercises
5. **Social Sharing**: Encourage learning in public

### Technical Requirements

1. **Proper MDX Formatting**: Use correct markdown syntax
2. **Valid JSON Schema**: Follow Shiksha platform requirements
3. **Unique IDs**: Generate proper MongoDB-style IDs
4. **Timestamps**: Include proper ISO format dates
5. **URL Generation**: Create valid slugs and image URLs

## Troubleshooting

### Common Issues

1. **API Key Issues**

    ```bash
    # Check environment variables
    echo $OPENAI_API_KEY

    # Test API connection
    python main.py status
    ```

2. **Content Generation Errors**

    ```bash
    # Check logs
    tail -f logs/the_boring_agents.log

    # Test individual agents
    python test_shiksha_course.py
    ```

3. **File Permission Issues**

    ```bash
    # Ensure output directory exists
    mkdir -p output

    # Check permissions
    ls -la output/
    ```

### Debug Mode

Enable detailed logging:

```bash
export LOG_LEVEL=DEBUG
python main.py shiksha create-course --course-name "Test Course" --description "Test" --save
```

## Future Enhancements

1. **Multi-language Support**: Generate courses in different languages
2. **Custom Templates**: Allow custom content templates
3. **Batch Processing**: Generate multiple courses simultaneously
4. **Advanced QA**: More sophisticated content validation
5. **Integration APIs**: Direct integration with Shiksha platform
6. **Content Analytics**: Track content quality metrics
7. **Collaborative Features**: Team-based course creation

## Support

For questions and support:

-   📧 Email: support@theboring.education
-   💬 Discord: [The Boring Education Community](https://discord.gg/boring-education)
-   📖 Documentation: [docs.theboring.education](https://docs.theboring.education)

---

Built with ❤️ by The Boring Education Team
