"""Prompt templates and constants for quiz generation.

All prompt data lives here as constants so generators stay lean.
"""

# ---------------------------------------------------------------------------
# Category metadata prompt
# ---------------------------------------------------------------------------

CATEGORY_METADATA_PROMPT = """\
Generate metadata for a {topic} quiz category.

Topic: {topic}
Question Count: {question_count}
Target Audience: {target_audience}

Provide:
1. **Category Name**: Display name for the quiz (should be the topic name or a variation)
2. **Category Description**: Engaging description (2-3 sentences) that:
   - Explains what the quiz covers
   - Mentions the target audience
   - Highlights key learning outcomes
   - Makes it appealing to take
3. **Category Icon**: Suggest an appropriate emoji or icon name (single emoji preferred)

Format as JSON:
{{
    "categoryName": "Display Name",
    "categoryDescription": "Description here",
    "categoryIcon": "🎯"
}}

Keep the description concise (100-150 words), engaging, and professional."""

# ---------------------------------------------------------------------------
# Single question prompt
# ---------------------------------------------------------------------------

SINGLE_QUESTION_PROMPT = """\
You are an expert quiz creator for {topic}. Create a high-quality multiple-choice quiz question.

Topic: {topic}
Concept to Test: {concept}
Difficulty Level: {difficulty}
Target Audience: {target_audience}
Question Type: {question_type}

Requirements:
1. **Question**: Clear, unambiguous, directly tests the concept
2. **Options**: Exactly 4 options (A, B, C, D)
   - One correct answer
   - Three plausible distractors (wrong but believable)
   - Options should be similar in length and complexity
3. **Correct Answer**: Index 0-3 (which option is correct)
4. **Explanation**: Brief explanation (2-3 sentences) of why the answer is correct
5. **Detailed Explanation**: Comprehensive explanation (1-2 paragraphs) that:
   - Explains why the correct answer is right
   - Explains why each wrong answer is incorrect
   - Provides additional context or tips
   - References best practices when applicable

For {difficulty} difficulty:
- Easy: Test basic understanding, straightforward concepts
- Medium: Apply knowledge, some analysis required
- Hard: Complex scenarios, deep understanding, edge cases

Format your response as JSON:
{{
    "question": "Your question here",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correctAnswer": 0,
    "explanation": "Brief explanation",
    "detailedExplanation": "Comprehensive explanation"
}}"""

# ---------------------------------------------------------------------------
# Batch questions prompt
# ---------------------------------------------------------------------------

BATCH_QUESTIONS_PROMPT = """\
You are an expert quiz creator for {topic}. Generate {question_count} diverse quiz questions.

Topic: {topic}
Question Count: {question_count}
Difficulty: {difficulty}
Target Audience: {target_audience}
Concepts to Cover: {concepts}

Create a balanced set of questions that:
1. Cover different concepts from the list
2. Use various question types (conceptual, code-based, scenario)
3. Follow the difficulty level ({difficulty})
4. Avoid repetition and ensure variety

For each question, provide:
- Clear, unambiguous question text
- 4 well-crafted options
- Correct answer index (0-3)
- Brief and detailed explanations
- Appropriate difficulty level

Return as a JSON array of question objects:
[
    {{
        "question": "Question 1",
        "options": ["A", "B", "C", "D"],
        "correctAnswer": 0,
        "explanation": "Brief",
        "detailedExplanation": "Detailed"
    }},
    ...
]"""

# ---------------------------------------------------------------------------
# Default icon map (topic keyword -> emoji)
# ---------------------------------------------------------------------------

DEFAULT_ICON_MAP = {
    "react": "⚛️",
    "node": "🟩",
    "javascript": "🟨",
    "python": "🐍",
    "java": "☕",
    "html": "🌐",
    "css": "🎨",
    "mongodb": "🍃",
    "sql": "🗄️",
    "devops": "⚙️",
    "cloud": "☁️",
    "security": "🔒",
    "ai": "🤖",
    "machine learning": "🧠",
    "data science": "📊",
    "dsa": "📚",
    "algorithms": "🔢",
}

DEFAULT_ICON = "📝"
