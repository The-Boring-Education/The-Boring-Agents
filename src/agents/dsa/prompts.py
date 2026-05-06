"""Prompt templates for DSA question and study guide generation."""

DSA_QUESTIONS_PROMPT = """
You are an expert DSA educator creating production-ready content for interview prep.

Topic: {topic}
Question count: {question_count}
Difficulty: {difficulty}
Include real-world problems: {include_real_world}

Return ONLY a JSON array with exactly {question_count} items.
Each item MUST follow this shape:
{{
  "title": "string",
  "answer": "string",
  "difficulty": "EASY|MEDIUM|HARD",
  "domain": ["DSA"],
  "companyTypes": ["FAANG","MNC","Startup"],
  "topics": ["ARRAY|STRING|HASHMAP|SLIDING_WINDOW|..."],
  "isRealWorldProblem": boolean,
  "resources": {{
    "youtubeURL": "string or empty",
    "leetcodeURL": "string or empty",
    "blogURL": "string or empty"
  }},
  "sections": {{
    "first_principles": {{
      "paragraphs": ["string"],
      "key_observation": "string"
    }},
    "examples": [{{
      "label": "Example 1",
      "input": "string",
      "output": "string",
      "explanation": "string",
      "step_by_step": ["string"]
    }}],
    "ways_to_solve": [{{
      "approach_number": 1,
      "name": "string",
      "description": "string",
      "time_complexity": "string",
      "time_reason": "string",
      "space_complexity": "string",
      "space_reason": "string",
      "verdict": "optimal",
      "verdict_label": "Optimal"
    }}],
    "working_code": {{
      "default_language": "python",
      "languages": {{
        "python": {{ "code": "string" }}
      }}
    }}
  }}
}}

Constraints:
- At least one item must have "isRealWorldProblem": true when include_real_world=true.
- Use only allowed domain values: FRONTEND, BACKEND, GENERAL, FULLSTACK, DSA.
- Use only allowed companyTypes values with exact casing.
- Keep answers practical and interview oriented.
- No markdown fences and no explanation text, JSON only.
"""

DSA_STUDY_GUIDE_PROMPT = """
You are generating a compact DSA study guide for topic: {topic}

Based on these generated question titles:
{question_titles}

Return ONLY one JSON object with shape:
{{
  "topicId": "topic-slug",
  "title": "Topic - Complete Study Guide",
  "hasGuide": true,
  "sections": [
    {{"type":"intro","sortOrder":1,"content":{{"pageTitle":"string","subtitle":"string","openingParagraph":"string","prereqCards":[],"callouts":[]}}}},
    {{"type":"concept","sortOrder":2,"content":{{"pageTitle":"string","subtitle":"string","subsections":[{{"subheading":"string","bodyText":"string","codeBlocks":[]}}]}}}},
    {{"type":"pattern","sortOrder":3,"content":{{"pageTitle":"string","subtitle":"string","whatIsIt":"string","triggerPhrases":["string"],"whenNotToUse":"string","codeTemplates":[],"workedExample":{{"problemTitle":"string","problemStatement":"string","coreTrick":"string"}},"practiceQuestions":[]}}}},
    {{"type":"cheatsheet","sortOrder":4,"content":{{"pageTitle":"string","subtitle":"string","patternRows":[],"decisionGuide":"string","questionGroups":[],"oneThingToRemember":["string"]}}}}
  ]
}}

No markdown fences. Return valid JSON only.
"""
