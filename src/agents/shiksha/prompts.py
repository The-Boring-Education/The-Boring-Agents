"""Prompt templates for Shiksha course outline and chapter generation."""

SHIKSHA_OUTLINE_PROMPT = """
You are an expert course designer creating a draft Shiksha course outline.

Topic: {topic}
Chapter count: {chapter_count}
Difficulty: {difficulty}

Return ONLY one JSON object with exactly this shape:
{{
  "name": "Course title",
  "slug": "kebab-case-course-slug",
  "description": "1-2 sentence course description",
  "coverImageURL": "",
  "roadmap": "FRONTEND",
  "difficultyLevel": "EASY",
  "isPremium": false,
  "features": ["Hands-on examples"],
  "credits": [],
  "chapters": [
    {{"key": "kebab-case-chapter-key", "title": "Chapter title"}}
  ]
}}

Constraints:
- "chapters" has exactly {chapter_count} items, ordered as the learner should read them.
- "slug" and every chapter "key" are kebab-case (lowercase letters, numbers, hyphens only).
- Chapter "key" values are unique within this course and stable (derived from the title, never reused).
- "roadmap" is one of: FRONTEND, BACKEND, FULLSTACK, DSA, AI, DATA, GTM.
- "difficultyLevel" is one of: EASY, MEDIUM, HARD (uppercase, matching {difficulty}).
- "isPremium" is false. Omit "price" entirely when not premium.
- "credits" is an empty array (admins attribute authors at review time).
- Do NOT emit any lifecycle status field (no status, lifecycleStatus, or published flag).
- No markdown fences and no explanation text, JSON only.
"""

SHIKSHA_CHAPTER_PROMPT = """
You are writing one chapter of a Shiksha course as MDX.

Course: {course_name}
Topic: {topic}
Chapter key: {chapter_key}
Chapter title: {chapter_title}
Difficulty: {difficulty}

Return ONLY one JSON object with exactly this shape:
{{
  "key": "{chapter_key}",
  "title": "{chapter_title}",
  "content": "# MDX chapter content",
  "isOptional": false,
  "credits": []
}}

Constraints:
- "key" MUST equal "{chapter_key}" exactly. "title" MUST equal "{chapter_title}" exactly.
- "content" is a self-contained MDX string: start with "# {chapter_title}",
  then 2-5 short sections with ## headings, one fenced code block where relevant.
- MDX must not contain <script> tags or raw HTML event handlers.
- "isOptional" is false unless the chapter is clearly supplementary.
- "credits" is an empty array.
- Do NOT emit any lifecycle status field.
- No markdown fences around the JSON and no explanation text, JSON only.
"""
