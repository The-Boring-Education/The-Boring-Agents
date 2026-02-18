"""Generic answer generator for aptitude and basic interview questions."""

from typing import Dict
from langchain_core.prompts import PromptTemplate

from src.agents.interview.generators.base_generator import BaseAnswerGenerator


class GenericAnswerGenerator(BaseAnswerGenerator):
    """Generator for generic/aptitude interview questions with basic reasoning."""

    def _get_answer_prompt_template(self) -> PromptTemplate:
        return PromptTemplate(
            input_variables=["question", "topic", "difficulty", "frequency", "priority", "company_types"],
            template="""
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
            """,
        )

    def _get_answer_structure(self) -> Dict[str, str]:
        return {
            "Quick Answer": "Quick Answer",
            "Introduction": "Introduction",
            "Basic Reasoning": "Basic Reasoning",
            "Why This Concept Matters": "Why This Concept Matters",
            "Interview Pro Tips": "Interview Pro Tips",
        }
