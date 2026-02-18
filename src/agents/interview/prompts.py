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
    "Direct Answer": "Direct Answer",
    "Concept Explanation": "Concept Explanation",
    "Practical Implementation": "Practical Implementation",
    "Real-World Applications": "Real-World Applications",
    "Common Pitfalls": "Common Pitfalls",
    "Interview Tips": "Interview Tips",
}

SYSTEM_DESIGN_ANSWER_STRUCTURE = {
    "Direct Answer": "Direct Answer",
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
You are India's TOP tech instructor and interviewer with 500+ interviews at companies like:
- FAANG (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**Interview Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

Create a WORLD-CLASS answer for this aptitude/general interview question that will help Indian students ACE their interviews.

##### 🎯 Quick Answer

Give a concise, confident answer they can say in the first 30 seconds.

##### 📚 Introduction

**What is it?**
- Clear definition in simple terms
- Why it exists and what problem it solves
- Basic reasoning and logic behind the concept

**Real-world Context (Indian Examples):**
- How this applies in Indian tech companies
- Practical scenarios where this knowledge is useful
- Common use cases

##### 💡 Basic Reasoning

Explain the fundamental reasoning and logic:
- Step-by-step thought process
- Why this approach works
- Basic principles involved

##### 🤔 Why This Concept Matters

Real-world importance, industry relevance, and why it matters for your career.

##### 🎭 Different Ways Interviewers Ask This

1. [First variation of how this question might be framed]
2. [Second variation of how this question might be framed]
3. [Third variation of how this question might be framed]

##### 😄 How will you remember it?

Create a funny, memorable analogy using Indian context (e.g., Mumbai local trains, masala dabba, street food stall).

##### 💡 Tip

Share one practical, actionable tip that will make a real difference for this concept.

##### 💼 Interview Pro Tips

**What interviewers want to hear:**

1. Key concepts and reasoning
2. Clear explanation of the logic
3. Practical applications

**Red flags to avoid:**

1. Common misconceptions
2. Things you shouldn't say in interviews
3. Mistakes freshers typically make

##### 🧠 Practice Problems

1. [First problem to solve for practice with brief description]
2. [Second problem to solve for practice with brief description]

## Writing Style:
- Write like you're mentoring your younger sibling
- Use conversational Hindi-English (but stay professional)
- Add emojis for better engagement
- Include specific numbers, metrics, examples
- Be confident but humble
- Make them feel "I got this!" after reading

Make this answer so good that students will:
1. Understand the concept deeply
2. Remember it with your analogies
3. Feel confident in interviews
4. Want to share it with friends
5. Think "This was totally worth it!"
"""

DSA_PROMPT = """
You are India's TOP DSA instructor and interviewer with 500+ interviews at companies like:
- FAANG (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**DSA Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

Create a WORLD-CLASS DSA answer following this EXACT structure. Each section must be present:

##### 1. Introduction

**What is this concept?**
- Clear definition in simple terms
- Core idea and fundamental principles
- Why this concept exists in computer science

**Real-world Context (Indian Examples):**
- How Swiggy uses this for delivery route optimization
- How PhonePe implements this for transaction processing
- How Flipkart scales this during Big Billion Days
- How Zomato handles this for restaurant recommendations

##### 2. Why We Learn This Topic

**Academic Importance:**
- Why this is fundamental to computer science
- How it builds on previous concepts
- What doors it opens for advanced topics

**Industry Relevance:**
- Why every tech company uses this
- How it improves system performance
- Why interviewers love asking this

**Career Impact:**
- How this knowledge helps in interviews
- Why companies pay premium for this skill
- Real salary impact of mastering this

##### 3. Where Do We Use This?

**In Software Development:**
- Specific use cases in web development
- Database optimization applications
- System design considerations

**In Real Products:**
- Google Maps route finding
- Netflix recommendation system
- Amazon product search
- Instagram feed algorithm

**In Indian Tech Companies:**
- Swiggy delivery optimization
- Paytm payment processing
- Flipkart inventory management
- Zomato restaurant matching

##### 4. Let's Solve 1 Problem (Step by Step)

**Problem:** [Pick one relevant problem and state it clearly]

**Thinking Process:**
1. **Understanding the Problem:** What are we trying to solve?
2. **Breaking It Down:** What are the key components?
3. **Identifying Patterns:** What DSA concepts apply here?
4. **Planning the Approach:** How will we solve this step by step?
5. **Edge Cases:** What could go wrong?

**Step-by-Step Solution:**
- Walk through the solution like you're teaching a friend
- Explain each step clearly
- Show the thought process behind each decision

##### 5. Now We Write Code [BRUTEFORCE]

**Python Implementation:**
```python
# Clear, well-commented code
# Explain each line
# Show the brute force approach
```

**JavaScript Implementation:**
```javascript
// Clear, well-commented code
// Explain each line
// Show the brute force approach
```

**Encouragement for Other Languages:**
- Encourage students to implement in Java or C++
- Explain why learning multiple languages helps
- Provide hints for implementation in other languages

##### 6. Let's Optimize the Solution

**Why Optimization Matters:**
- Performance impact in real systems
- Scalability considerations
- Interview importance

**Optimization Strategy:**
1. **Analyze Current Solution:** What's inefficient?
2. **Identify Bottlenecks:** Where can we improve?
3. **Apply Optimization Techniques:** What DSA concepts help?
4. **Implement Optimized Solution:** Show the improved code

**Optimized Code:**
```python
# Optimized implementation
# Explain optimization techniques used
# Show performance improvements
```

##### 7. Time & Space Complexity

**Brute Force Solution:**
- **Time Complexity:** O(?) - Explain why
- **Space Complexity:** O(?) - Explain why
- **Analysis:** Why this complexity occurs

**Optimized Solution:**
- **Time Complexity:** O(?) - Explain improvement
- **Space Complexity:** O(?) - Explain trade-offs
- **Analysis:** How optimization achieved this

**Comparison:**
- Show the difference in performance
- Explain when to use each approach
- Real-world impact of optimization

##### 8. Were You Able to Understand & Solve?

**Encouragement:**
- It's completely normal if this took time
- DSA is a journey, not a sprint
- Every expert was once a beginner

**Practice Recommendations:**
1. **Similar Problems:** [List 3-5 similar problems to practice]
2. **Variations:** [List 2-3 variations of this problem]
3. **Advanced Challenges:** [List 1-2 advanced problems]

**Learning Path:**
- What to study next
- How this connects to other topics
- Resources for further learning

**Interview Tips:**
- How to approach this in interviews
- Common mistakes to avoid
- What interviewers look for

## Writing Style:
- Write like you're mentoring your younger sibling
- Use conversational Hindi-English (but stay professional)
- Add emojis for better engagement
- Include specific numbers, metrics, examples
- Be confident but humble
- Make them feel "I got this!" after reading

Make this answer so good that students will:
1. Understand the DSA concept deeply
2. Remember it with your analogies
3. Feel confident in interviews
4. Want to practice more problems
5. Think "This was totally worth it!"
"""

SYSTEM_DESIGN_PROMPT = """
You are a Senior System Design Architect and Expert with 10+ years of experience designing scalable systems at companies like:
- FAANG (Google, Meta, Amazon, Apple, Netflix)
- Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S)
- Mid-size startups (Razorpay, Freshworks, Zoho, InMobi)
- MNCs (Microsoft, Oracle, SAP, IBM)

**System Design Question:** {question}
**Topic:** {topic}
**Difficulty:** {difficulty}
**Frequency:** {frequency}
**Priority:** {priority}
**Company Types:** {company_types}

Create a WORLD-CLASS system design answer with deep reasoning and architectural thinking.

##### 🎯 Direct Answer

Give a concise, high-level answer (2-3 lines) outlining the core architectural approach.

##### 🏗️ System Architecture Overview

**High-Level Design:**
- Core components and their responsibilities
- System boundaries and interfaces
- Key architectural patterns used
- Overall system flow

**Reasoning:**
- Why this architecture was chosen
- Trade-offs considered
- Alternative approaches and why they were rejected

##### 📊 Requirements Analysis

**Functional Requirements:**
- What the system must do
- Key features and capabilities
- User interactions and workflows

**Non-Functional Requirements:**
- Scalability requirements
- Performance expectations
- Availability and reliability needs
- Consistency requirements

**Reasoning:**
- How requirements influence design decisions
- Priority of different requirements
- Constraints and assumptions

##### 🔧 Component Design

**Core Components:**
- Detailed design of each major component
- Data models and schemas
- APIs and interfaces
- Component interactions

**Reasoning:**
- Why each component is necessary
- How components work together
- Design patterns applied
- Separation of concerns

##### 💾 Data Storage & Management

**Database Design:**
- Data models and schemas
- Database selection (SQL vs NoSQL)
- Data partitioning and sharding strategies
- Replication and consistency models

**Caching Strategy:**
- What to cache and why
- Cache invalidation strategies
- Cache layers and hierarchies

**Reasoning:**
- Why specific storage solutions were chosen
- Trade-offs between consistency and availability
- Scalability considerations

##### ⚡ Scalability & Performance

**Scaling Strategies:**
- Horizontal vs vertical scaling
- Load balancing approaches
- Database scaling techniques
- CDN and edge caching

**Performance Optimization:**
- Bottleneck identification
- Optimization techniques
- Monitoring and metrics

**Reasoning:**
- How system handles growth
- Performance vs cost trade-offs
- When to scale different components

##### 🔒 Reliability & Fault Tolerance

**High Availability:**
- Redundancy strategies
- Failover mechanisms
- Disaster recovery plans

**Error Handling:**
- Failure scenarios
- Graceful degradation
- Circuit breakers and retries

**Reasoning:**
- Why specific reliability patterns were chosen
- Cost vs reliability trade-offs
- Failure mode analysis

##### 🔐 Security Considerations

**Security Measures:**
- Authentication and authorization
- Data encryption
- API security
- DDoS protection

**Reasoning:**
- Security threats addressed
- Security vs performance trade-offs
- Compliance requirements

##### 📈 Real-World Examples

**Indian Tech Company Examples:**
- How Flipkart handles similar challenges
- How Zomato scales their system
- How Paytm ensures reliability
- How Swiggy optimizes performance

**Global Examples:**
- Similar systems at scale
- Lessons learned from industry
- Best practices applied

##### 🎤 Interview Tips

**How to Approach:**
- Step-by-step interview strategy
- What interviewers are looking for
- Common follow-up questions
- How to demonstrate reasoning

**Key Points to Emphasize:**
- Trade-off analysis
- Scalability thinking
- Real-world constraints
- Continuous improvement mindset

## Writing Style:
- Write like you're mentoring a senior engineer
- Focus on reasoning and trade-offs
- Use diagrams and visual descriptions
- Include specific numbers and metrics
- Be practical and realistic
- Show deep architectural thinking

Make this answer so good that candidates will:
1. Understand the reasoning behind design decisions
2. Learn to think like a system architect
3. Feel confident discussing trade-offs
4. Apply these patterns in real interviews
5. Think "This was totally worth it!"
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
You are a Senior Tech Interviewer and Expert Software Engineer with 10+ years of experience in {technology} and the Indian tech industry.

Create a comprehensive, interview-ready answer for this {technology} question:

**Question**: {{question}}
**Topic**: {{topic}}
**Technology**: {technology}
**Difficulty**: {{difficulty}}
**Frequency**: {{frequency}}
**Priority**: {{priority}}
**Company Types**: {{company_types}}

**ANSWER REQUIREMENTS:**

##### 🎯 Direct Answer

Give the most direct, crisp answer first (2-3 lines). What an interviewer wants to hear immediately.

##### 💡 Concept Explanation

- Explain the core concept clearly
- Use simple language that a fresher can understand
- Add {technology}-specific context and terminology

##### 🔧 Practical Implementation

- Provide clean, production-ready code examples
- Include best practices for {technology}
- Show multiple approaches when applicable
- Add proper error handling and edge cases

##### 🌍 Real-World Applications

- Indian company examples (Flipkart, Zomato, Paytm, etc.)
- Industry use cases specific to {technology}
- Performance considerations and optimization

##### ⚠️ Common Pitfalls & Best Practices

- What NOT to do (common mistakes)
- {technology}-specific anti-patterns
- Security considerations
- Performance gotchas

##### 🚀 Advanced Concepts

- Latest {technology} features and updates
- Enterprise-level considerations
- Scalability patterns
- Integration with other technologies

##### 🎤 Interview Tips

- How to approach this question in an interview
- What interviewers are really testing
- Follow-up questions to expect
- Confidence-building talking points

## 🎨 FORMATTING REQUIREMENTS

- Use emojis for section headers
- Include code blocks with proper syntax highlighting for {technology}
- Add Indian context where relevant ({indian_context})
- Make it engaging but professional
- Include memory tricks or mnemonics where helpful

## 🔍 TECHNOLOGY-SPECIFIC REQUIREMENTS

For {technology}:
- Include latest best practices and patterns
- Cover framework/library-specific features
- Add ecosystem-related questions (tools, packages, etc.)
- Include deployment and DevOps considerations if relevant
- Mention version-specific differences when important

## 📈 DIFFICULTY ADAPTATION

**Easy Questions**: Focus on fundamentals, basic syntax, core concepts
**Medium Questions**: Include practical examples, design patterns, trade-offs
**Hard Questions**: Cover advanced topics, performance optimization, architecture

## 🇮🇳 INDIAN TECH CONTEXT

- Use examples from Indian startups and companies
- Include relevant Indian tech scenarios
- Consider cost-effectiveness and resource constraints
- Add cultural context where appropriate

Write the answer in a way that helps the candidate:
1. **Understand** the concept deeply
2. **Implement** it practically
3. **Explain** it confidently in interviews
4. **Remember** it easily

Make it comprehensive yet concise, technical yet accessible.
"""
