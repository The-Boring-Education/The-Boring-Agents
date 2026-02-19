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
