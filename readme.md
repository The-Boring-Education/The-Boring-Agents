# The Boring Agents

AI-powered content generation for The Boring Education platform.

## 🎯 Overview

The Boring Agents is an intelligent system that generates high-quality educational content, interview preparation materials, and project ideas. It features an **adaptive interview system** that can understand your requirements from MDX files and generate tailored content.

## 🚀 Key Features

### 1. **Intelligent Interview System**

-   **MDX-based workflow** - Write your requirements in MDX files
-   **Adaptive content generation** - Automatically adapts to different interview types (DSA, Python, Java, etc.)
-   **Human review integration** - Review and edit at each step
-   **World-class quality** - 20+ years of FAANG experience perspective

### 2. **Content Generation**

-   **Shiksha courses** - Complete course structures with Indian context
-   **Interview preparation** - Comprehensive question sheets
-   **Project ideas** - Real-world project suggestions with implementation guides

### 3. **Adaptive Intelligence**

-   **DSA Questions**: Explain like teaching a 10-year-old with analogies
-   **Python/Java**: Technical depth with practical examples
-   **System Design**: Architecture thinking with scalability focus
-   **Aptitude**: Clear problem-solving with step-by-step methods

## 📋 Intelligent Interview Workflow

### Simple 4-Step Process

#### **Step 1: Create Sheet JSON**

```bash
python main.py interview create-sheet-from-mdx --mdx-file your_requirements.mdx
```

-   Analyzes your MDX file requirements
-   Creates sheet JSON for database creation
-   Extracts topic and requirements automatically

#### **Step 2: Generate Questions**

```bash
python main.py interview generate-questions-from-mdx --mdx-file your_requirements.mdx --count 50
```

-   Generates questions based on your MDX requirements
-   Saves to MDX file for your review and editing
-   Includes frequency, priority, company types

#### **Step 3: Generate Answers**

```bash
python main.py interview generate-answers-from-mdx --mdx-file ./output/questions_topic.mdx
```

-   Generates comprehensive answers for all questions
-   Applies MDX styling for readability
-   Creates complete sheet ready for database

#### **Step 4: Publish to Database**

```bash
python main.py interview publish-sheet --sheet-file ./output/complete_sheet_topic.json --sheet-id your_sheet_id
```

-   Publishes to database using existing workflow
-   Maintains all validation and quality checks

## 📝 MDX File Format

### Example: DSA Interview Requirements

```mdx
# DSA Interview Questions

## My Requirements and Experience

I want to create a comprehensive DSA interview preparation guide for college students.
The questions should explain concepts like teaching a 10-year-old - simple, clear, and memorable.

### Target Audience

-   College students preparing for placements
-   Beginners learning DSA concepts
-   Working professionals looking to refresh skills

### Content Style

-   Explain concepts with real-world analogies
-   Use simple language, avoid jargon
-   Include memory tricks and mnemonics
-   Focus on understanding over memorization

### Question Categories Needed

-   Array and String manipulation
-   Linked Lists and Trees
-   Dynamic Programming basics
-   Graph algorithms
-   Time and Space complexity analysis

### Special Requirements

-   Include coding examples in multiple languages
-   Add visual diagrams where helpful
-   Provide step-by-step problem-solving approach
-   Include common mistakes and how to avoid them
```

## 🎨 Content Adaptation Examples

### DSA Questions

-   **Style**: Explain like teaching a 10-year-old
-   **Headings**: Quick Answer, Understanding Concept, Step-by-Step Solution, Memory Tricks
-   **Content**: Real-world analogies, visual explanations, memory tricks

### Python Questions

-   **Style**: Technical depth with practical examples
-   **Headings**: Quick Answer, Technical Deep Dive, Code Examples, Best Practices
-   **Content**: Code snippets, real-world scenarios, performance considerations

### System Design Questions

-   **Style**: Architecture thinking with scalability focus
-   **Headings**: Quick Answer, Architecture Overview, Scalability Considerations
-   **Content**: High-level thinking, trade-off analysis, real-world examples

## 🔧 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
ENVIRONMENT=local  # local, dev, or prod
```

### 3. Verify Setup

```bash
python main.py status
```

## 🚀 Usage Examples

### Create DSA Interview Sheet

```bash
# 1. Create MDX file with DSA requirements
# 2. Generate sheet JSON
python main.py interview create-sheet-from-mdx --mdx-file dsa_requirements.mdx

# 3. Generate questions from MDX
python main.py interview generate-questions-from-mdx --mdx-file dsa_requirements.mdx --count 40

# 4. Review and edit questions in MDX file
# 5. Generate answers
python main.py interview generate-answers-from-mdx --mdx-file ./output/questions_dsa.mdx

# 6. Publish to database
python main.py interview publish-sheet --sheet-file ./output/complete_sheet_dsa.json --sheet-id your_sheet_id
```

### Create Python Interview Sheet

```bash
# 1. Create MDX file with Python requirements
# 2. Generate sheet JSON
python main.py interview create-sheet-from-mdx --mdx-file python_requirements.mdx

# 3. Generate questions
python main.py interview generate-questions-from-mdx --mdx-file python_requirements.mdx --count 60

# 4. Review and edit questions
# 5. Generate answers
python main.py interview generate-answers-from-mdx --mdx-file ./output/questions_python.mdx

# 6. Publish to database
python main.py interview publish-sheet --sheet-file ./output/complete_sheet_python.json --sheet-id your_sheet_id
```

## 📊 Available Commands

### Interview Commands

```bash
# Intelligent Interview System (New)
python main.py interview create-sheet-from-mdx --mdx-file requirements.mdx
python main.py interview generate-questions-from-mdx --mdx-file requirements.mdx --count 50
python main.py interview generate-answers-from-mdx --mdx-file questions.mdx
python main.py interview publish-sheet --sheet-file sheet.json --sheet-id id

# Traditional Interview System
python main.py interview question-sheet --topic "JavaScript"
python main.py interview revamp-sheet --sheet-id your_sheet_id
python main.py interview revamp-all-sheets
```

### Content Commands

```bash
python main.py content course-outline --topic "React Development" --level intermediate
python main.py content video-suggestions --topic "Node.js" --module "Authentication"
python main.py content tips-and-tricks --topic "Python" --level advanced
```

### Project Commands

```bash
python main.py projects create --idea "E-commerce App" --description "Build a full-stack e-commerce platform"
python main.py projects create-from-mdx --mdx-file project_idea.mdx
```

### Shiksha Commands

```bash
python main.py shiksha create-course --course-name "Python Backend" --description "Complete Python backend course"
python main.py shiksha create-world-class-course --course-name "React Frontend" --description "Advanced React course"
```

## 🎯 Benefits

### 1. **MDX-First Approach**

-   Write your heart about any interview requirements
-   Flexible and human-readable format
-   Easy to review and edit

### 2. **Adaptive Intelligence**

-   Automatically detects interview type
-   Adapts content style and tone
-   Generates appropriate question categories

### 3. **Quality Assurance**

-   Human review at each step
-   Intelligent validation
-   Professional content standards

### 4. **World-Class Perspective**

-   20+ years of FAANG experience
-   Indian tech industry context
-   Real interview patterns and trends

## 📁 Output Structure

```
output/
├── sheet_[topic].json                    # Step 1: Sheet JSON for database
├── questions_[topic].mdx                 # Step 2: Questions for review
└── complete_sheet_[topic].json          # Step 3: Complete sheet with answers
```

## 🎉 Success Metrics

-   ✅ **Adaptive Content Generation** - Content tailored to interview type
-   ✅ **MDX-Based Workflow** - Flexible input format
-   ✅ **Human Review Integration** - Quality control at each stage
-   ✅ **World-Class Quality** - Professional content standards
-   ✅ **Simplified Process** - Easy 4-step workflow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

**The Boring Agents** - Making content generation intelligent, adaptive, and human-friendly! 🚀
