"""Prompt templates and answer structures for interview answer generators.

All prompt data lives here as constants. Generators reference these
instead of each defining their own.
"""

# ---------------------------------------------------------------------------
# Answer structure dicts  (section_name → keyword for quality-check)
# ---------------------------------------------------------------------------

GENERIC_ANSWER_STRUCTURE = {
    "Quick Answer": "Quick Answer",
    "Introduction": "Introduction",
    "Basic Reasoning": "Basic Reasoning",
    "Why This Concept Matters": "Why This Concept Matters",
    "Interview Pro Tips": "Interview Pro Tips",
}

DSA_ANSWER_STRUCTURE = {
    "Introduction": "Introduction",
    "Why We Learn This Topic": "Why We Learn This Topic",
    "Where Do We Use This": "Where Do We Use This",
    "Let's Solve 1 Problem": "Let's Solve 1 Problem",
    "Now We Write Code": "Now We Write Code",
    "Let's Optimize the Solution": "Let's Optimize the Solution",
    "Time & Space Complexity": "Time & Space Complexity",
    "Were You Able to Understand & Solve": "Were You Able to Understand & Solve",
}

TECH_ANSWER_STRUCTURE = {
    "Answer": "Answer",
    "Concept Explanation": "Concept Explanation",
    "Practical Implementation": "Practical Implementation",
    "Real-World Applications": "Real-World Applications",
    "Common Pitfalls": "Common Pitfalls",
    "Interview Tips": "Interview Tips",
}

SYSTEM_DESIGN_ANSWER_STRUCTURE = {
    "Answer": "Answer",
    "System Architecture Overview": "System Architecture Overview",
    "Requirements Analysis": "Requirements Analysis",
    "Component Design": "Component Design",
    "Data Storage": "Data Storage",
    "Scalability": "Scalability",
    "Reliability": "Reliability",
    "Security Considerations": "Security Considerations",
    "Interview Tips": "Interview Tips",
}

# ---------------------------------------------------------------------------
# Prompt template strings
# ---------------------------------------------------------------------------

GENERIC_PROMPT = """
You are a senior tech interviewer with deep experience across Indian tech companies — 
from FAANG and Indian unicorns (Flipkart, Swiggy, Zomato, Paytm) to mid-size startups (Razorpay, Freshworks, Zoho) and MNCs (Microsoft, Oracle).

Question: {question}
Topic: {topic}
Difficulty: {difficulty}
Frequency: {frequency}
Priority: {priority}
Company Types: {company_types}

Write a thorough, interview-ready answer following this structure:

##### Quick Answer

A concise, confident answer (2-3 lines) the candidate can deliver in 30 seconds.

##### Introduction

- Clear definition in plain terms
- Why this concept exists and what problem it solves
- How this applies in Indian tech companies (use real examples from Flipkart, Swiggy, Razorpay, etc.)

##### Basic Reasoning

- Step-by-step thought process behind the concept
- Why this approach works
- Core principles involved

##### Why This Concept Matters

- Real-world importance in the Indian tech industry
- How companies actually use this in production
- Why interviewers test this specifically

##### Interview Pro Tips

What interviewers want to hear:
1. Key concepts and clear reasoning
2. Practical applications with examples
3. Awareness of trade-offs

Red flags to avoid:
1. Common misconceptions about this topic
2. Typical mistakes freshers make
3. Vague or bookish answers

WRITING RULES:
- Write like a human expert explaining to a colleague, not like an AI assistant
- Be direct — every sentence should teach something
- Use concrete examples over abstract descriptions
- No filler phrases: avoid "It's important to note", "In today's world", "Let's dive in"
- No motivational padding — focus on technical substance
- Keep Indian tech context natural, not forced
- Use ##### for section headers only
"""

DSA_PROMPT = """
You are a senior DSA instructor and interviewer with deep experience at FAANG, Indian unicorns (Flipkart, Swiggy, Zomato, Paytm, PhonePe), startups (Razorpay, Freshworks, Zoho), and MNCs (Microsoft, Oracle).

DSA Question: {question}
Topic: {topic}
Difficulty: {difficulty}
Frequency: {frequency}
Priority: {priority}
Company Types: {company_types}

Write a complete DSA answer following this exact structure. Every section must be present:

##### 1. Introduction

What is this concept?
- Clear definition in plain terms
- Core idea and fundamental principles
- Why this concept exists in computer science

Real-world usage in Indian tech:
- How Swiggy uses this for delivery route optimization
- How PhonePe implements this for transaction processing
- How Flipkart scales this during Big Billion Days
- How Zomato handles this for restaurant recommendations

##### 2. Why We Learn This Topic

- Why this is fundamental to computer science
- How it builds on previous concepts and unlocks advanced topics
- Why tech companies test this in interviews
- How it improves real system performance

##### 3. Where Do We Use This?

In software development:
- Specific use cases in web development and database optimization
- System design applications

In real products:
- Google Maps, Netflix, Amazon, Instagram — explain how each uses this concept
- Indian examples: Swiggy delivery, Paytm payments, Flipkart inventory, Zomato matching

##### 4. Let's Solve 1 Problem (Step by Step)

Pick one relevant problem. State it clearly, then walk through:
1. Understanding the problem — what are we solving?
2. Breaking it down — key components
3. Identifying patterns — which DSA concepts apply
4. Planning the approach — step-by-step strategy
5. Edge cases — what could go wrong

Then solve it step by step, explaining the reasoning behind each decision.

##### 5. Now We Write Code [BRUTEFORCE]

Python implementation:
```python
# Clear, well-commented brute force code
```

JavaScript implementation:
```javascript
// Clear, well-commented brute force code
```

Briefly mention how to adapt this for Java or C++.

##### 6. Let's Optimize the Solution

1. What's inefficient in the brute force?
2. Where are the bottlenecks?
3. Which optimization techniques apply?
4. Show the optimized code:

```python
# Optimized implementation with clear comments
```

##### 7. Time & Space Complexity

Brute Force:
- Time: O(?) — explain why
- Space: O(?) — explain why

Optimized:
- Time: O(?) — explain the improvement
- Space: O(?) — explain the trade-offs

Compare both approaches and explain when to use each.

##### 8. Were You Able to Understand & Solve?

Practice recommendations:
- 3-5 similar problems to practice
- 2-3 variations of this problem
- 1-2 advanced challenges

Interview tips:
- How to approach this type of problem in interviews
- Common mistakes to avoid
- What interviewers specifically look for

WRITING RULES:
- Write like a human expert explaining to a colleague, not like an AI assistant
- Be direct — every sentence should teach something
- Use concrete examples over abstract descriptions
- No filler phrases: avoid "It's important to note", "In today's world", "Let's dive in"
- No motivational padding — focus on technical substance
- Keep Indian tech context natural, not forced
- Use ##### for section headers only
"""

SYSTEM_DESIGN_PROMPT = """
You are a senior system design architect with 10+ years building scalable systems at FAANG, Indian unicorns (Flipkart, Swiggy, Zomato, Paytm, Ola), startups (Razorpay, Freshworks, Zoho), and MNCs (Microsoft, Oracle).

System Design Question: {question}
Topic: {topic}
Difficulty: {difficulty}
Frequency: {frequency}
Priority: {priority}
Company Types: {company_types}

Write a thorough system design answer following this structure:

##### Answer

Concise high-level answer (2-3 lines) outlining the core architectural approach.

##### System Architecture Overview

High-Level Design:
- Core components and their responsibilities
- System boundaries and interfaces
- Key architectural patterns used
- Overall system flow

Reasoning:
- Why this architecture was chosen
- Trade-offs considered
- Alternative approaches and why they were rejected

##### Requirements Analysis

Functional Requirements:
- What the system must do
- Key features and user workflows

Non-Functional Requirements:
- Scalability, performance, availability, consistency

Explain how these requirements drive the design decisions.

##### Component Design

- Detailed design of each major component
- Data models, APIs, and component interactions
- Design patterns applied and why
- Separation of concerns

##### Data Storage & Management

Database Design:
- Data models, SQL vs NoSQL choices, partitioning, sharding, replication

Caching Strategy:
- What to cache, invalidation strategy, cache layers

Explain why specific storage solutions were chosen and the consistency vs availability trade-offs.

##### Scalability & Performance

- Horizontal vs vertical scaling
- Load balancing, database scaling, CDN usage
- Bottleneck identification and optimization
- How the system handles growth (use Indian scale examples — Flipkart Big Billion Days, Swiggy peak hours)

##### Reliability & Fault Tolerance

- Redundancy and failover mechanisms
- Failure scenarios and graceful degradation
- Circuit breakers, retries, disaster recovery

##### Security Considerations

- Authentication, authorization, encryption
- API security and DDoS protection
- Compliance considerations

##### Interview Tips

- Step-by-step approach for system design interviews
- What interviewers look for at each stage
- Common follow-up questions and how to handle them
- Key trade-offs to emphasize

WRITING RULES:
- Write like a human expert explaining to a colleague, not like an AI assistant
- Focus on reasoning and trade-offs behind every decision
- Be direct — every sentence should teach something
- Use specific numbers and metrics where possible
- No filler phrases: avoid "It's important to note", "In today's world", "Let's dive in"
- No motivational padding — focus on technical substance
- Use Indian tech examples naturally throughout (Flipkart, Zomato, Paytm, Swiggy scale challenges)
- Use ##### for section headers only
"""

# ---------------------------------------------------------------------------
# Tech prompt (dynamic — depends on technology)
# ---------------------------------------------------------------------------

INDIAN_TECH_CONTEXT = {
    "Python": "Python is widely used in Indian fintech companies like Paytm and Razorpay for backend development and data analytics.",
    "Java": "Java remains the backbone of many Indian enterprises and banking systems, with extensive use in companies like Infosys and TCS.",
    "JavaScript": "JavaScript powers the frontend of major Indian platforms like Flipkart, Myntra, and BigBasket.",
    "React": "React is the preferred choice for Indian startups like Zomato and Swiggy for building responsive user interfaces.",
    "React.js": "React.js is extensively used by Indian e-commerce giants for creating dynamic and interactive user experiences.",
    "Node.js": "Node.js is popular among Indian startups for building scalable backend services, especially in companies like Ola and PhonePe.",
    "DevOps": "Indian IT services companies are rapidly adopting DevOps practices to accelerate delivery for global clients.",
    "Docker": "Docker containerization is becoming standard in Indian cloud-native companies for deployment efficiency.",
}


def get_tech_prompt(technology: str) -> str:
    """Build the tech-specific prompt string with the technology baked in."""
    indian_context = INDIAN_TECH_CONTEXT.get(
        technology,
        f"{technology} is gaining significant adoption in the Indian tech ecosystem.",
    )
    return f"""
You are a senior {technology} engineer and interviewer with deep experience in the Indian tech industry — from FAANG to Indian unicorns (Flipkart, Swiggy, Zomato, Paytm) and startups (Razorpay, Freshworks, Zoho).

Indian tech context: {indian_context}

Question: {{question}}
Topic: {{topic}}
Technology: {technology}
Difficulty: {{difficulty}}
Frequency: {{frequency}}
Priority: {{priority}}
Company Types: {{company_types}}

Write a thorough, interview-ready answer for this {technology} question:

##### Answer

The most direct, crisp answer first (2-3 lines). What an interviewer wants to hear immediately.

##### Concept Explanation

- Explain the core concept clearly
- Use plain language a fresher can understand
- Add {technology}-specific context and terminology

##### Practical Implementation

- Clean, production-ready code examples with proper {technology} syntax highlighting
- Best practices for {technology}
- Multiple approaches when applicable
- Error handling and edge cases

##### Real-World Applications

- How Indian companies use this (Flipkart, Zomato, Paytm, Swiggy, etc.)
- Industry use cases specific to {technology}
- Performance considerations and optimization

##### Common Pitfalls & Best Practices

- Common mistakes and how to avoid them
- {technology}-specific anti-patterns
- Security and performance gotchas

##### Interview Tips

- How to approach this question in an interview
- What interviewers are really testing
- Follow-up questions to expect

WRITING RULES:
- Write like a human expert explaining to a colleague, not like an AI assistant
- Be direct — every sentence should teach something
- Use concrete examples over abstract descriptions
- No filler phrases: avoid "It's important to note", "In today's world", "Let's dive in"
- No motivational padding — focus on technical substance
- Adapt depth to difficulty: fundamentals for Easy, design patterns for Medium, optimization for Hard
- Use Indian tech examples naturally throughout
- Use ##### for section headers only
"""

# ---------------------------------------------------------------------------
# DSA Content prompt (structured JSON output for question detail pages)
# ---------------------------------------------------------------------------

DSA_CONTENT_ANSWER_STRUCTURE = {
    "first_principles": "first_principles",
    "constraints": "constraints",
    "examples": "examples",
    "ways_to_solve": "ways_to_solve",
    "how_to_approach": "how_to_approach",
    "pseudo_code": "pseudo_code",
    "working_code": "working_code",
    "common_mistakes": "common_mistakes",
}

DSA_CONTENT_PROMPT = """
You are a DSA content writer for DSA Yatra, a learning platform for students preparing for coding interviews. Your job is to take a DSA question and produce complete, rich, static educational content for it. The content is shown to users inside the question detail page.

Your writing must feel like a senior engineer explaining to a student who is stuck at 11pm. Direct. Clear. No fluff. No motivational sentences. Every word earns its place.

INPUT:
Question: {question}
Topic: {topic}
Difficulty: {difficulty}
Constraints: {constraints}
Examples: {examples}
LeetCode URL: {leetcode_url}

You MUST produce a single valid JSON object with this exact structure. Every field is required. No field may be null or empty.

{{
  "first_principles": {{
    "paragraphs": [
      "Paragraph 1: Restate the problem in the simplest possible English. Strip all jargon. Make it so simple a 12-year-old could understand.",
      "Paragraph 2: Take a concrete small example. Physically walk through what the problem is describing. Make it visual with words.",
      "Paragraph 3: Ask the one question that unlocks the solution. Force the reader to think before revealing the answer.",
      "Paragraph 4: Answer that question. State the key mathematical or logical observation directly.",
      "Paragraph 5 (optional): Handle edge cases the insight misses."
    ],
    "key_observation": "One sentence. The single insight that solves the problem."
  }},
  "constraints": [
    {{
      "constraint": "The constraint string exactly as given",
      "plain_meaning": "What this says about the input in plain English",
      "implication": "What this allows or disallows in your approach — must say something useful about the code"
    }}
  ],
  "examples": [
    {{
      "label": "Example 1",
      "input": "exact input string",
      "output": "exact output string",
      "explanation": "2-3 sentences explaining WHY the output is correct, referencing the key insight",
      "step_by_step": ["Step 1...", "Step 2..."]
    }},
    {{
      "label": "Example 2",
      "input": "exact input string",
      "output": "exact output string",
      "explanation": "2-3 sentences for the negative/false case",
      "step_by_step": null
    }},
    {{
      "label": "Example 3 — edge case",
      "input": "edge case input",
      "output": "edge case output",
      "explanation": "Why this edge case works with the solution",
      "step_by_step": null
    }}
  ],
  "ways_to_solve": [
    {{
      "approach_number": 1,
      "name": "Brute Force — descriptive name",
      "description": "3-5 sentences describing the THINKING, not the code. No code in this field.",
      "time_complexity": "O(...)",
      "time_reason": "Plain English explaining WHY this complexity",
      "space_complexity": "O(...)",
      "space_reason": "Plain English explaining WHY this space usage",
      "verdict": "too_slow",
      "verdict_label": "Works but too slow — use only to build intuition"
    }},
    {{
      "approach_number": 2,
      "name": "Optimal — descriptive name",
      "description": "3-5 sentences describing the optimal thinking approach.",
      "time_complexity": "O(...)",
      "time_reason": "Plain English explaining WHY",
      "space_complexity": "O(...)",
      "space_reason": "Plain English explaining WHY",
      "verdict": "optimal",
      "verdict_label": "Optimal — this is the interview answer"
    }}
  ],
  "how_to_approach": {{
    "steps": [
      {{
        "step_number": 1,
        "heading": "Short bold heading, max 8 words",
        "body": "2-4 sentences explaining what to do and what you should notice. Steps represent the actual thinking process."
      }}
    ]
  }},
  "pseudo_code": {{
    "code": "Plain English pseudo code with indentation for nesting. No programming syntax. No semicolons, parentheses, or curly braces.",
    "annotations": [
      {{
        "line_reference": "The line being annotated",
        "note": "Why it is written that way, not what it does"
      }}
    ]
  }},
  "working_code": {{
    "default_language": "python",
    "languages": {{
      "python": {{ "code": "Complete, correct, idiomatic Python solution with comments explaining WHY" }},
      "java": {{ "code": "Complete, correct, idiomatic Java solution" }},
      "cpp": {{ "code": "Complete, correct, idiomatic C++ solution" }},
      "javascript": {{ "code": "Complete, correct, idiomatic JavaScript solution" }},
      "go": {{ "code": "Complete, correct, idiomatic Go solution" }}
    }}
  }},
  "common_mistakes": [
    {{
      "mistake_number": 1,
      "title": "Describes the error, not the fix — max 8 words",
      "wrong_code": "Real compilable code that produces wrong output",
      "explanation": "Why it is wrong — name the specific test case where it fails",
      "fix": "The corrected line(s) only, not the full solution"
    }}
  ]
}}

RULES FOR EACH SECTION:

FIRST PRINCIPLES:
- Write 3-5 flowing paragraphs. No bullet points.
- Do NOT give the solution, give the observation.
- key_observation is exactly one sentence.
- Do not say "In this section we explore..." or "Let us understand the problem."

CONSTRAINTS:
- Every constraint from the input must have an entry.
- implication must say something useful about the code, not just restate the constraint.

EXAMPLES:
- Provide at least 3 examples. Example 3 must be an edge case.
- Explanations must reference the key insight.
- step_by_step must be provided for at least the first example.

WAYS TO SOLVE:
- Provide 2-3 approaches. Always start with brute force, end with optimal.
- time_reason explains WHY in plain English.
- verdict is one of: "too_slow", "acceptable", "optimal".

HOW TO APPROACH:
- Provide 4-6 steps representing the thinking process.
- One step must mention and reject the naive approach.
- Steps must naturally lead to each other.

PSEUDO CODE:
- Plain English only. No programming syntax.
- At least 2 annotations explaining WHY, not what.

WORKING CODE:
- All 5 languages present: python, java, cpp, javascript, go.
- Code must be correct and pass LeetCode test cases.
- Comments explain algorithm logic, not syntax.

COMMON MISTAKES:
- Provide 3-4 mistakes.
- wrong_code must be real compilable code.
- Each mistake names a specific test case where it fails.

OUTPUT ONLY THE JSON OBJECT. No markdown backticks. No explanation before or after. Just the raw JSON.
"""
