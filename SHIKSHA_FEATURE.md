# SHIKSHA Course Development Feature

This document describes the SHIKSHA course development feature implemented for The Boring Agents.

## Overview

The SHIKSHA course development feature allows automated generation of complete educational courses with the exact structure and format required by The Boring Education's SHIKSHA platform.

## Features

### 1. Complete Course Generation

Generate full courses with proper metadata and chapter structure:

```bash
python main.py content shiksha-course --topic "Node.js Backend Development" --level beginner --roadmap Backend --save
```

**Output includes:**
- Course metadata (name, slug, cover image URL, description, live date)
- Proper difficulty level and roadmap categorization
- 8+ chapters with complete MDX content
- Structured JSON matching SHIKSHA schema

### 2. Individual Chapter Generation

Create detailed content for specific chapters:

```bash
python main.py content shiksha-chapter --chapter-name "React Hooks" --course-topic "React Development" --description "Learn React Hooks in depth" --save
```

**Chapter content includes:**
- Markdown headers and structured sections
- Callout boxes (📌, 💡) for important information
- YouTube video tutorial recommendations
- Tips, tricks, and best practices
- Project ideas and exercises
- Social media sharing templates

### 3. Social Media Template Generation

Generate LinkedIn and Twitter sharing templates:

```bash
python main.py content social-media --topic "Node.js" --achievement "Built first REST API" --learning-points "Express.js,Authentication,Databases" --save
```

**Templates include:**
- Professional LinkedIn post format
- Concise Twitter post format
- Proper hashtags including #Shiksha #TheBoringEducation
- Engaging content for learning journey sharing

## Course Schema

The generated courses follow the exact SHIKSHA JSON schema:

```json
{
  "status": true,
  "data": {
    "_id": "course_unique_id",
    "name": "Complete Course Name",
    "slug": "url-friendly-slug",
    "coverImageURL": "https://ik.imagekit.io/tbe/webapp/shiksha-{slug}-cover.svg",
    "description": "Course description",
    "liveOn": "2025-01-31T06:00:00.000Z",
    "roadmap": "Backend|Frontend|Fullstack",
    "difficultyLevel": "Beginner|Intermediate|Advanced",
    "chapters": [
      {
        "name": "Chapter Name",
        "content": "# Chapter content in MDX format...",
        "_id": "chapter_unique_id",
        "createdAt": "2025-01-29T09:01:09.636Z",
        "updatedAt": "2025-01-29T09:01:09.636Z"
      }
    ]
  }
}
```

## Chapter Content Structure

Each chapter follows the SHIKSHA MDX format:

```markdown
# Chapter Title

📌
**Personal introduction explaining why this topic matters**

### Why Do You Need {Topic}?
Explanation of importance and relevance

### How Important Is It?
Industry context and career relevance

### How Long Will It Take to Learn?
Time estimates and learning approach

## Tutorial
YouTube video recommendations with descriptions and links

💡
Learning tips and guidance

### Projects to Build
1. Practical project ideas
2. Real-world applications

## Share It On Social Media

### LinkedIn
```
Professional sharing template with achievements and hashtags
```

### Twitter
```
Concise sharing template for Twitter
```
```

## Implementation Details

### ContentAgent Enhancements

The `ContentAgent` class has been enhanced with new methods:

- `create_shiksha_course()` - Generate complete courses
- `create_shiksha_chapter()` - Generate individual chapters  
- `generate_social_media_templates()` - Create sharing templates
- `_structure_shiksha_course()` - Structure output in proper format
- `_parse_chapters_from_content()` - Generate chapter content
- `_generate_sample_chapter_content()` - Create MDX formatted content

### New Prompt Templates

Added specialized templates for SHIKSHA content:

- `shiksha_course` - Complete course generation
- `shiksha_chapter` - Individual chapter content
- `social_media` - Sharing template generation

### CLI Commands

New commands available in the CLI:

- `content shiksha-course` - Generate complete course
- `content shiksha-chapter` - Generate chapter content
- `content social-media` - Generate sharing templates

## Usage Examples

### Generate Backend Course

```bash
python main.py content shiksha-course \
  --topic "Zero to One Backend Development with Node.js" \
  --level beginner \
  --roadmap Backend \
  --description "Start Your Backend Dev Journey. Projects Included." \
  --save
```

### Create Authentication Chapter

```bash
python main.py content shiksha-chapter \
  --chapter-name "Authentication Basics" \
  --course-topic "Backend Development" \
  --description "Learn user authentication and security" \
  --level intermediate \
  --save
```

### Generate Learning Posts

```bash
python main.py content social-media \
  --topic "React Development" \
  --achievement "Built complete React application" \
  --learning-points "Components,Hooks,State Management,API Integration" \
  --save
```

## Testing

The implementation includes comprehensive tests:

- `test_shiksha.py` - Core functionality tests
- `demo_shiksha.py` - Full demonstration script
- `validate_shiksha.py` - Schema validation tests

Run tests:

```bash
python test_shiksha.py      # Test core functionality
python demo_shiksha.py      # See full demo
python validate_shiksha.py  # Validate schema compliance
```

## Output Files

Generated courses are saved as JSON files in the `./output/` directory:

- Course files: `shiksha_course_{topic}_{timestamp}.json`
- Chapter files: `chapter_{name}_{timestamp}.json` 
- Social media files: `social_media_{topic}_{timestamp}.json`

## API Integration

When used with actual LLM APIs (OpenAI, etc.), set your API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

The system will generate high-quality, contextual content based on the provided parameters.

## Quality Assurance

The generated content includes:

✅ Proper SHIKSHA JSON schema compliance  
✅ MDX formatting with callouts and structure  
✅ YouTube video integration  
✅ Social media templates with branding  
✅ Engaging, conversational tone  
✅ Practical examples and projects  
✅ The Boring Education branding consistency  

This feature is production-ready and can generate courses that match the exact format and quality expected by the SHIKSHA platform.