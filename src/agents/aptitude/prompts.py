"""Prompt templates and answer structures for aptitude answer generators.

Four distinct formats:
- SPEED: Quantitative & Reasoning (Arithmetic, Data Interpretation, Logical Reasoning)
- RULES: Verbal Ability (Spotting Errors, Synonyms, Antonyms)
- PERSPECTIVE: GD Round (Politics, Economics, Social Issues, Technology)
- BEHAVIORAL: HR Interview (Self-Intro, Career Goals, Behavioral Questions)
"""

# ─── Answer Structure Dicts (section_name → keyword for quality-check) ────────

SPEED_ANSWER_STRUCTURE = {
    "Fundamental Concept": "Fundamental Concept",
    "The Conventional Method": "Conventional Method",
    "The Pro Shortcut": "Pro Shortcut",
    "Common Trap": "Common Trap",
    "Time-Saving Tip": "Time-Saving Tip",
}

RULES_ANSWER_STRUCTURE = {
    "Context & Meaning": "Context",
    "The Grammar Rule": "Grammar Rule",
    "Why Others Are Wrong": "Why others are wrong",
    "Vocabulary Bridge": "Vocabulary Bridge",
}

PERSPECTIVE_ANSWER_STRUCTURE = {
    "Topic Overview": "Topic Overview",
    "Arguments FOR": "Arguments FOR",
    "Arguments AGAINST": "Arguments AGAINST",
    "Key Facts/Stats": "Key Facts",
    "The Closing Stance": "Closing Stance",
}

BEHAVIORAL_ANSWER_STRUCTURE = {
    "The Interviewer's Intent": "Interviewer's Intent",
    "The STAR Strategy": "STAR Strategy",
    "Sample Winning Answer": "Sample",
    "Red Flags": "Red Flags",
}

# ─── Format Type → Structure Mapping ─────────────────────────────────────────

ANSWER_STRUCTURE_MAP = {
    "SPEED": SPEED_ANSWER_STRUCTURE,
    "RULES": RULES_ANSWER_STRUCTURE,
    "PERSPECTIVE": PERSPECTIVE_ANSWER_STRUCTURE,
    "BEHAVIORAL": BEHAVIORAL_ANSWER_STRUCTURE,
}

# ─── Prompt Templates ────────────────────────────────────────────────────────

SPEED_PROMPT = """You are an expert aptitude trainer who coaches students for campus placements at top Indian companies (TCS, Infosys, Wipro, Cognizant, Accenture, Deloitte, Goldman Sachs, Amazon, Microsoft).

Topic: {topic}
Sub-Category: {sub_category}
Question: {question}

Generate a comprehensive answer for this aptitude question following this EXACT structure. Every section MUST be present:

##### 📘 Fundamental Concept
A 1-2 sentence refresher on the math rule or logical pattern used. State the core formula or principle clearly.

##### 🧱 The Conventional Method
The school-style, step-by-step algebraic solution:
1. Define the variables
2. Set up the equations
3. Solve step by step
4. State the answer clearly

##### ⚡ The "Pro" Shortcut (Trick)
The formula or mental math trick that solves it in under 30 seconds. Explain why this shortcut works.

##### ⚠️ Common Trap
Describe where students usually make mistakes. Give a specific example of the wrong approach and explain why it fails.

##### ⏱️ Time-Saving Tip
Is there an option-elimination strategy? Can we use estimation? Mention specific techniques like plugging in answer choices, working backwards, or using divisibility rules.

WRITING RULES:
- Be precise with numbers — show every calculation step
- Use concrete examples, not abstract descriptions
- Write like a tutor explaining to a student, not like a textbook
- Keep it concise but complete — no filler
- If the question involves options, reference them in the Time-Saving Tip
- Use ##### for section headers only
"""

RULES_PROMPT = """You are an expert English language trainer who coaches students for verbal ability sections in campus placement exams at top Indian companies.

Topic: {topic}
Sub-Category: {sub_category}
Question: {question}

Generate a comprehensive answer for this verbal ability question following this EXACT structure. Every section MUST be present:

##### 🖋️ Context & Meaning
Explain the sentence's intent or the word's definition. Break down what the question is really asking. Provide the correct answer upfront.

##### ⚖️ The Grammar Rule
State the specific grammar rule that applies (e.g., Subject-Verb Agreement, Tense Consistency, Parallelism, Modifier Placement). Explain the rule in simple terms with a general example.

##### ❌ Why Others Are Wrong
For each incorrect option, briefly explain why it doesn't fit:
- Option analysis with clear reasoning
- Reference the specific rule violated

##### 💡 Vocabulary Bridge
Provide a mnemonic, etymology, or sample sentence to help remember the word/rule permanently. Connect it to everyday usage.

WRITING RULES:
- Reference specific grammar rules by name
- Provide clear option-by-option analysis
- Write like a friendly tutor, not a grammar textbook
- Use examples from everyday English usage
- Keep it practical — focus on exam strategy
- Use ##### for section headers only
"""

PERSPECTIVE_PROMPT = """You are a Group Discussion (GD) coach who prepares students for campus placement GD rounds at top companies in India. You help students sound well-informed and articulate.

Topic: {topic}
Sub-Category: {sub_category}
Question/Topic for Discussion: {question}

Generate a comprehensive GD briefing following this EXACT structure. Every section MUST be present:

##### 🌍 Topic Overview
3-4 lines of current context. Why is this topic relevant today? What recent events or developments make this a hot discussion topic?

##### ✅ Arguments "FOR" (The Pro-Side)
- Provide 3-4 well-reasoned points supporting this position
- Each point should have a clear logic chain
- Include real-world examples where possible

##### ❌ Arguments "AGAINST" (The Con-Side)
- Provide 3-4 well-reasoned counter-arguments
- Each point should be equally strong and logical
- Include real-world examples where possible

##### 📊 Key Facts/Stats
Concrete numbers, dates, case studies, or policies they can quote to sound like an expert. Provide 4-5 specific facts.

##### 🤝 The "Closing" Stance
A balanced, neutral 2-3 line summary they can use to conclude the discussion. This should acknowledge both sides and propose a forward-looking perspective.

WRITING RULES:
- Be current — reference recent events and policies
- Arguments should be balanced — don't favor one side
- Facts must be concrete (numbers, dates, names)
- Write like a debater's cheat sheet, not an essay
- Focus on Indian context where relevant
- Use ##### for section headers only
"""

BEHAVIORAL_PROMPT = """You are an HR interview coach who has conducted 1000+ interviews at top Indian companies. You know exactly what interviewers look for and what gets candidates rejected.

Topic: {topic}
Sub-Category: {sub_category}
Question: {question}

Generate a comprehensive HR interview answer guide following this EXACT structure. Every section MUST be present:

##### 🕵️ The Interviewer's Intent
What is the HR actually evaluating with this question? What skills, traits, or red flags are they looking for? Explain in 2-3 clear points.

##### ⭐ The STAR Strategy
Provide a fill-in-the-blanks template using the STAR framework:
- **Situation**: [Describe a relevant situation — e.g., "During my final year project..."]
- **Task**: [What was your responsibility — e.g., "I was tasked with..."]
- **Action**: [What specific steps did you take — e.g., "I decided to..."]
- **Result**: [What was the outcome — e.g., "As a result, we achieved..."]

Include 2-3 scenario suggestions the student can adapt to their own experience.

##### 📝 Sample "Winning" Answer
A complete, high-quality example response that a fresher could adapt. It should:
- Be 150-200 words
- Sound natural, not rehearsed
- Show self-awareness and growth mindset
- Include specific (but adaptable) examples

##### 🚩 Red Flags (Do NOT Say)
List 3-4 things that will get them rejected or marked down. For each:
- The wrong thing to say
- Why it's a red flag
- What to say instead

WRITING RULES:
- Write for freshers/college students — keep examples relatable
- Be direct about what works and what doesn't
- Include both what TO say and what NOT to say
- Templates should be fill-in-the-blank ready
- Focus on Indian placement context
- Use ##### for section headers only
"""

# ─── Format Type → Prompt Mapping ────────────────────────────────────────────

PROMPT_MAP = {
    "SPEED": SPEED_PROMPT,
    "RULES": RULES_PROMPT,
    "PERSPECTIVE": PERSPECTIVE_PROMPT,
    "BEHAVIORAL": BEHAVIORAL_PROMPT,
}
