"""
Tech Answer Creator Agent for technology-specific interview questions.

This agent specializes in creating detailed answers for technology-specific interview questions
covering languages, frameworks, tools, and DevOps technologies.
"""

from typing import Dict, List, Any, Optional
from langchain_core.prompts import PromptTemplate
from src.core.base_agent import BaseAgent


class TechAnswerCreator(BaseAgent):
    """Agent for creating technology-specific interview answers."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Get technology from custom_params after parent initialization
        self.technology = self.custom_params.get('technology', 'General Tech')
        
        # Auto-detect technology from topic if not explicitly provided
        if self.technology == 'General Tech' and 'topic' in kwargs:
            self.technology = self._detect_technology_from_topic(kwargs['topic'])
        
        self.logger.info(f"Tech Answer Creator initialized for {self.technology}")

    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Define prompt templates for tech interview questions."""
        return {
            "tech_answer_prompt": PromptTemplate(
                input_variables=[
                    "question", "topic", "technology", "difficulty", "frequency", 
                    "priority", "company_types", "indian_context"
                ],
                template="""
You are a Senior Tech Interviewer and Expert Software Engineer with 10+ years of experience in {technology} and the Indian tech industry.

Create a comprehensive, interview-ready answer for this {technology} question:

**Question**: {question}
**Topic**: {topic}
**Technology**: {technology}
**Difficulty**: {difficulty}
**Frequency**: {frequency}
**Priority**: {priority}
**Company Types**: {company_types}

**ANSWER REQUIREMENTS:**

## 📋 Answer Structure (Mandatory Sections)

### 1. **🎯 Direct Answer** (2-3 lines)
- Give the most direct, crisp answer first
- What an interviewer wants to hear immediately

### 2. **💡 Concept Explanation**
- Explain the core concept clearly
- Use simple language that a fresher can understand
- Add {technology}-specific context and terminology

### 3. **🔧 Practical Implementation**
- Provide clean, production-ready code examples
- Include best practices for {technology}
- Show multiple approaches when applicable
- Add proper error handling and edge cases

### 4. **🌍 Real-World Applications**
- Indian company examples (Flipkart, Zomato, Paytm, etc.)
- Industry use cases specific to {technology}
- Performance considerations and optimization

### 5. **⚠️ Common Pitfalls & Best Practices**
- What NOT to do (common mistakes)
- {technology}-specific anti-patterns
- Security considerations
- Performance gotchas

### 6. **🚀 Advanced Concepts** (for Medium/Hard questions)
- Latest {technology} features and updates
- Enterprise-level considerations
- Scalability patterns
- Integration with other technologies

### 7. **🎤 Interview Tips**
- How to approach this question in an interview
- What interviewers are really testing
- Follow-up questions to expect
- Confidence-building talking points

## 🎨 FORMATTING REQUIREMENTS

- Use emojis for section headers
- Include code blocks with proper syntax highlighting
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
            ),

            "tech_code_example_prompt": PromptTemplate(
                input_variables=["question", "technology", "difficulty"],
                template="""
Create detailed code examples for this {technology} question: "{question}"

Requirements:
1. **Production-ready code** with proper structure
2. **Multiple approaches** if applicable (beginner → advanced)
3. **Error handling** and edge cases
4. **Comments explaining key concepts**
5. **{technology}-specific best practices**
6. **Testing examples** where relevant

Difficulty Level: {difficulty}

For {technology}:
- Use latest syntax and features
- Include relevant imports/dependencies
- Follow established conventions
- Add performance considerations
- Include configuration examples if needed

Format each example with:
- Clear description of the approach
- Complete, runnable code
- Explanation of key parts
- Time/space complexity if relevant
- When to use this approach
"""
            ),

            "tech_best_practices_prompt": PromptTemplate(
                input_variables=["question", "technology", "topic"],
                template="""
Generate {technology}-specific best practices for: "{question}"

Cover:
1. **Industry Standards**
   - What top Indian tech companies expect
   - Latest {technology} conventions

2. **Performance Optimization**
   - Common bottlenecks in {technology}
   - Monitoring and profiling tools
   - Caching strategies

3. **Security Considerations**
   - {technology}-specific vulnerabilities
   - Security best practices
   - Authentication/authorization patterns

4. **Scalability Patterns**
   - How to scale {technology} applications
   - Database integration patterns
   - Microservices considerations

5. **Testing Strategies**
   - Unit testing frameworks for {technology}
   - Integration testing approaches
   - Mocking and stubbing patterns

6. **DevOps Integration**
   - CI/CD pipelines for {technology}
   - Containerization best practices
   - Deployment strategies

Topic: {topic}
Focus on practical, implementable advice that interviewers value.
"""
            ),

            "tech_troubleshooting_prompt": PromptTemplate(
                input_variables=["question", "technology"],
                template="""
Create a troubleshooting guide for {technology} related to: "{question}"

Include:
1. **Common Issues & Solutions**
   - Typical problems developers face
   - Step-by-step debugging approaches
   - Tools for diagnosis

2. **Error Patterns**
   - Common error messages in {technology}
   - How to interpret and fix them
   - Prevention strategies

3. **Performance Issues**
   - How to identify bottlenecks
   - Profiling tools for {technology}
   - Optimization techniques

4. **Environment Issues**
   - Setup and configuration problems
   - Version compatibility issues
   - Development vs production differences

Make it practical and actionable for interview scenarios.
"""
            )
        }

    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate tech-specific content."""
        if content_type == "interview_answer":
            return self.generate_tech_answer(**kwargs)
        elif content_type == "code_examples":
            return self.generate_code_examples(**kwargs)
        elif content_type == "best_practices":
            return self.generate_best_practices(**kwargs)
        else:
            return {"status": "error", "message": f"Unknown content type: {content_type}"}

    def generate_answer(self, question: str, topic: str, difficulty: str = "Medium",
                       frequency: str = "Asked Sometimes", priority: str = "Medium", 
                       company_types: list = None) -> str:
        """Generate a tech-specific interview answer."""
        return self.generate_tech_answer(
            question=question, topic=topic, difficulty=difficulty,
            frequency=frequency, priority=priority, company_types=company_types
        )

    def generate_tech_answer(self, question: str, topic: str, difficulty: str = "Medium",
                            frequency: str = "Asked Sometimes", priority: str = "Medium", 
                            company_types: list = None, technology: str = None) -> str:
        """Generate comprehensive tech interview answer."""
        
        # Use provided technology or fall back to instance technology
        tech = technology or self.technology or "General Tech"
        
        # Set Indian context based on technology
        indian_context = self._get_indian_context(tech)
        
        # Generate the main answer
        answer = self._generate_with_prompt(
            self._format_prompt(
                "tech_answer_prompt",
                question=question,
                topic=topic,
                technology=tech,
                difficulty=difficulty,
                frequency=frequency,
                priority=priority,
                company_types=", ".join(company_types) if company_types else "All types",
                indian_context=indian_context
            )
        )
        
        # Apply quality improvements
        answer = self._apply_tech_quality_improvements(answer, question, difficulty, tech)
        
        return answer

    def _apply_tech_quality_improvements(self, answer: str, question: str, difficulty: str, technology: str) -> str:
        """Apply technology-specific quality improvements."""
        
        # Check for missing essential sections
        missing_sections = self._check_missing_tech_sections(answer)
        if missing_sections:
            answer = self._add_missing_tech_sections(answer, missing_sections, question, technology)
        
        # Ensure proper code formatting
        answer = self._ensure_tech_code_formatting(answer, technology)
        
        # Add technology-specific enhancements
        answer = self._add_tech_specific_enhancements(answer, technology, difficulty)
        
        # Add Indian tech context if missing
        answer = self._enhance_indian_tech_context(answer, technology)
        
        return answer

    def _check_missing_tech_sections(self, answer: str) -> List[str]:
        """Check for missing essential sections in tech answers."""
        required_sections = [
            "🎯 Direct Answer",
            "💡 Concept Explanation", 
            "🔧 Practical Implementation",
            "🌍 Real-World Applications",
            "⚠️ Common Pitfalls",
            "🎤 Interview Tips"
        ]
        
        missing = []
        for section in required_sections:
            if section not in answer and section.lower() not in answer.lower():
                missing.append(section)
        
        return missing

    def _add_missing_tech_sections(self, answer: str, missing_sections: List[str], 
                                  question: str, technology: str) -> str:
        """Add missing sections to tech answers."""
        
        additional_content = "\n\n"
        
        for section in missing_sections:
            if "Direct Answer" in section:
                additional_content += f"""
## {section}

{self._generate_direct_answer(question, technology)}
"""
            elif "Concept Explanation" in section:
                additional_content += f"""
## {section}

{self._generate_concept_explanation(question, technology)}
"""
            elif "Practical Implementation" in section:
                additional_content += f"""
## {section}

{self._generate_implementation_examples(question, technology)}
"""
            elif "Real-World Applications" in section:
                additional_content += f"""
## {section}

{self._generate_real_world_examples(question, technology)}
"""
            elif "Common Pitfalls" in section:
                additional_content += f"""
## {section}

{self._generate_common_pitfalls(question, technology)}
"""
            elif "Interview Tips" in section:
                additional_content += f"""
## {section}

{self._generate_interview_tips(question, technology)}
"""
        
        return answer + additional_content

    def _ensure_tech_code_formatting(self, answer: str, technology: str) -> str:
        """Ensure proper code formatting for technology-specific examples."""
        import re
        
        # Map technology to language identifier for syntax highlighting
        lang_map = {
            "Python": "python",
            "Java": "java", 
            "JavaScript": "javascript",
            "TypeScript": "typescript",
            "React": "jsx",
            "React.js": "jsx",
            "Node.js": "javascript",
            "Express.js": "javascript",
            "Spring Boot": "java",
            "Django": "python",
            "Flask": "python",
            "DevOps": "bash",
            "Docker": "dockerfile",
            "Kubernetes": "yaml"
        }
        
        lang = lang_map.get(technology, "text")
        
        # Fix code blocks without language specification
        answer = re.sub(r'```\n(?!```)', f'```{lang}\n', answer)
        
        return answer

    def _add_tech_specific_enhancements(self, answer: str, technology: str, difficulty: str) -> str:
        """Add technology-specific enhancements based on the tech stack."""
        
        enhancements = {
            "Python": self._add_python_enhancements,
            "Java": self._add_java_enhancements,
            "JavaScript": self._add_javascript_enhancements,
            "React": self._add_react_enhancements,
            "React.js": self._add_react_enhancements,
            "Node.js": self._add_nodejs_enhancements,
            "DevOps": self._add_devops_enhancements
        }
        
        if technology in enhancements:
            answer = enhancements[technology](answer, difficulty)
        
        return answer

    def _add_python_enhancements(self, answer: str, difficulty: str) -> str:
        """Add Python-specific enhancements."""
        if "virtual environment" not in answer.lower() and difficulty in ["Medium", "Hard"]:
            answer += "\n\n**💡 Python Best Practice**: Always use virtual environments for project isolation."
        
        if "pip" not in answer.lower() and "package" in answer.lower():
            answer += "\n\n**📦 Package Management**: Use `pip install` for dependencies and `requirements.txt` for reproducible builds."
        
        return answer

    def _add_java_enhancements(self, answer: str, difficulty: str) -> str:
        """Add Java-specific enhancements."""
        if "jvm" not in answer.lower() and difficulty == "Hard":
            answer += "\n\n**⚙️ JVM Consideration**: Consider memory management and garbage collection for production applications."
        
        return answer

    def _add_javascript_enhancements(self, answer: str, difficulty: str) -> str:
        """Add JavaScript-specific enhancements."""
        if "async" not in answer.lower() and "promise" not in answer.lower() and difficulty in ["Medium", "Hard"]:
            answer += "\n\n**🔄 Async Consideration**: Consider using async/await for better readability in asynchronous operations."
        
        return answer

    def _add_react_enhancements(self, answer: str, difficulty: str) -> str:
        """Add React-specific enhancements."""
        if "useeffect" not in answer.lower() and "lifecycle" in answer.lower():
            answer += "\n\n**⚛️ React Hooks**: Modern React applications prefer hooks over class components for state management."
        
        return answer

    def _add_nodejs_enhancements(self, answer: str, difficulty: str) -> str:
        """Add Node.js-specific enhancements."""
        if "npm" not in answer.lower() and "package" in answer.lower():
            answer += "\n\n**📦 Node.js Package Management**: Use `npm` or `yarn` for dependency management and `package-lock.json` for version locking."
        
        return answer

    def _add_devops_enhancements(self, answer: str, difficulty: str) -> str:
        """Add DevOps-specific enhancements."""
        if "ci/cd" not in answer.lower() and difficulty in ["Medium", "Hard"]:
            answer += "\n\n**🚀 DevOps Practice**: Implement CI/CD pipelines for automated testing and deployment."
        
        return answer

    def _enhance_indian_tech_context(self, answer: str, technology: str) -> str:
        """Enhance with Indian tech industry context."""
        indian_companies = ["Flipkart", "Paytm", "Zomato", "Swiggy", "BYJU'S", "Ola", "PhonePe"]
        
        if not any(company in answer for company in indian_companies):
            context = self._get_indian_context(technology)
            if context:
                answer += f"\n\n**🇮🇳 Indian Tech Context**: {context}"
        
        return answer

    def _get_indian_context(self, technology: str) -> str:
        """Get Indian tech industry context for the technology."""
        contexts = {
            "Python": "Python is widely used in Indian fintech companies like Paytm and Razorpay for backend development and data analytics.",
            "Java": "Java remains the backbone of many Indian enterprises and banking systems, with extensive use in companies like Infosys and TCS.",
            "JavaScript": "JavaScript powers the frontend of major Indian platforms like Flipkart, Myntra, and BigBasket.",
            "React": "React is the preferred choice for Indian startups like Zomato and Swiggy for building responsive user interfaces.",
            "React.js": "React.js is extensively used by Indian e-commerce giants for creating dynamic and interactive user experiences.",
            "Node.js": "Node.js is popular among Indian startups for building scalable backend services, especially in companies like Ola and PhonePe.",
            "DevOps": "Indian IT services companies are rapidly adopting DevOps practices to accelerate delivery for global clients.",
            "Docker": "Docker containerization is becoming standard in Indian cloud-native companies for deployment efficiency."
        }
        
        return contexts.get(technology, "This technology is gaining significant adoption in the Indian tech ecosystem.")

    def _generate_direct_answer(self, question: str, technology: str) -> str:
        """Generate a direct answer for the question."""
        prompt = f"Provide a concise, direct answer (2-3 lines) for this {technology} question: {question}"
        return self._generate_with_prompt(prompt)

    def _generate_concept_explanation(self, question: str, technology: str) -> str:
        """Generate concept explanation."""
        prompt = f"Explain the core concept behind this {technology} question in simple terms: {question}"
        return self._generate_with_prompt(prompt)

    def _generate_implementation_examples(self, question: str, technology: str) -> str:
        """Generate implementation examples."""
        prompt = f"Provide practical code examples for this {technology} question: {question}"
        return self._generate_with_prompt(prompt)

    def _generate_real_world_examples(self, question: str, technology: str) -> str:
        """Generate real-world application examples."""
        prompt = f"Provide real-world applications and use cases for this {technology} question: {question}"
        return self._generate_with_prompt(prompt)

    def _generate_common_pitfalls(self, question: str, technology: str) -> str:
        """Generate common pitfalls and best practices."""
        prompt = f"List common mistakes and best practices for this {technology} question: {question}"
        return self._generate_with_prompt(prompt)

    def _generate_interview_tips(self, question: str, technology: str) -> str:
        """Generate interview-specific tips."""
        prompt = f"Provide interview tips and talking points for this {technology} question: {question}"
        return self._generate_with_prompt(prompt)

    def _detect_technology_from_topic(self, topic: str) -> str:
        """Auto-detect technology from topic/context."""
        topic_lower = topic.lower()
        
        # Define technology detection patterns
        tech_patterns = {
            "Python": ["python", "django", "flask", "fastapi", "pandas", "numpy", "pytest"],
            "Java": ["java", "spring", "spring boot", "maven", "gradle", "junit"],
            "JavaScript": ["javascript", "js", "node", "npm", "yarn"],
            "React": ["react", "react.js", "jsx", "redux", "hooks"],
            "React.js": ["react", "react.js", "jsx", "redux", "hooks"],
            "Node.js": ["node", "node.js", "express", "npm", "yarn"],
            "Angular": ["angular", "typescript", "rxjs"],
            "Vue.js": ["vue", "vue.js", "vuex", "nuxt"],
            "DevOps": ["devops", "docker", "kubernetes", "jenkins", "ci/cd", "aws", "azure"],
            "Docker": ["docker", "container", "dockerfile"],
            "Kubernetes": ["kubernetes", "k8s", "kubectl", "helm"]
        }
        
        # Check for exact matches first
        for tech, patterns in tech_patterns.items():
            for pattern in patterns:
                if pattern in topic_lower:
                    return tech
        
        # If no specific technology detected, return General Tech
        return "General Tech"

    def set_technology(self, technology: str) -> None:
        """Set the technology focus for this agent."""
        self.technology = technology
        self.logger.info(f"Technology focus updated to: {technology}")

    def get_supported_technologies(self) -> List[str]:
        """Get list of supported technologies."""
        return [
            "Python", "Java", "JavaScript", "TypeScript",
            "React", "React.js", "Angular", "Vue.js", 
            "Node.js", "Express.js", "Spring Boot",
            "Django", "Flask", "FastAPI",
            "DevOps", "Docker", "Kubernetes",
            "General Tech"
        ] 