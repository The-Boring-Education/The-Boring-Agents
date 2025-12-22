"""Instructor Agent for creating engaging content with Indian context and humor."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate

from src.core.base_agent import BaseAgent


class InstructorAgent(BaseAgent):
    """Agent for creating engaging instructional content with Indian context, humor, and analogies."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for instructor content creation."""
        
        engaging_intro_template = PromptTemplate(
            input_variables=["chapter_name", "course_name", "difficulty_level", "key_concepts"],
            template="""
            You are the world's most engaging tech instructor from India, known for making complex concepts simple and fun.
            
            Create an engaging introduction for the chapter "{chapter_name}" in the "{course_name}" course.
            Difficulty Level: {difficulty_level}
            Key Concepts: {key_concepts}
            
            Your introduction should:
            
            1. **Hook with Indian Context**
               - Start with a relatable scenario from Indian daily life
               - Use examples from popular Indian apps (Swiggy, Zomato, PhonePe, etc.)
               - Reference Indian startups, companies, or success stories
            
            2. **Add Humor and Analogies**
               - Use funny analogies that Indians can relate to
               - Include light humor about Indian life, traffic, food, etc.
               - Make technical concepts feel like storytelling
            
            3. **Build Excitement**
               - Show real career impact in Indian context
               - Mention salary ranges and job opportunities in India
               - Connect to Indian tech ecosystem and opportunities
            
            4. **Set Clear Expectations**
               - What they'll learn in simple Hindi-English terms
               - How long it will take (be realistic for Indian learners)
               - Prerequisites in easy language
            
            Write like you're talking to a friend over chai. Be warm, funny, and incredibly clear.
            Use Hinglish occasionally but keep it professional. Make them excited to learn!
            
            Example Indian analogies to inspire you:
            - "Understanding variables is like organizing your mom's masala dabba"
            - "APIs are like ordering food on Swiggy - you don't know how they cook it, but you get what you want"
            - "Git branches are like managing multiple WhatsApp groups for different friend circles"
            """
        )
        
        concept_explanation_template = PromptTemplate(
            input_variables=["concept", "difficulty_level", "real_world_examples"],
            template="""
            You are India's favorite tech teacher. Explain {concept} in the most engaging way possible.
            
            Difficulty Level: {difficulty_level}
            Real-world Examples Context: {real_world_examples}
            
            Structure your explanation:
            
            1. **Start with a Story/Analogy**
               - Use an Indian context that everyone can relate to
               - Make it funny and memorable
               - Connect the analogy throughout the explanation
            
            2. **Simple Definition**
               - Explain in plain English first
               - Then add the technical definition
               - Use Hindi words where they help (like "samjha" for understanding)
            
            3. **Why Should You Care?**
               - Real job opportunities in Indian companies
               - Salary impact and career growth
               - How Indian startups use this concept
            
            4. **Indian Company Examples**
               - How Flipkart, Ola, Paytm, etc. use this
               - Success stories from Indian developers
               - Local case studies and implementations
            
            5. **Common Misconceptions**
               - What most Indian students get wrong
               - Myths that coaching institutes spread
               - Clear up confusion with simple examples
            
            6. **Practice Scenarios**
               - Problems they can solve in Indian context
               - Projects that will impress Indian recruiters
               - Practice exercises with Indian themes
            
            Make it conversational, warm, and incredibly clear. Add appropriate emoji and formatting.
            """
        )
        
        indian_examples_template = PromptTemplate(
            input_variables=["topic", "context", "target_audience"],
            template="""
            Create compelling Indian examples and case studies for {topic}.
            
            Context: {context}
            Target Audience: {target_audience}
            
            Generate examples in these categories:
            
            1. **Popular Indian Apps & Websites**
               - How Swiggy, Zomato, PhonePe, GPay use {topic}
               - Flipkart, Amazon India implementations
               - Ola, Uber India technical challenges
            
            2. **Indian Startup Success Stories**
               - How Indian unicorns solved problems using {topic}
               - Technical decisions that made companies successful
               - Scaling challenges in Indian market
            
            3. **Relatable Daily Life Examples**
               - Railway reservation system analogies
               - Local grocery store management examples
               - Indian festival planning scenarios
            
            4. **Indian Developer Journey**
               - Career progression stories
               - Salary growth with {topic} skills
               - Interview experiences at Indian companies
            
            5. **Cultural Context Examples**
               - Multi-language support for Indian apps
               - Payment integration challenges in India
               - Scaling for Indian internet speeds and devices
            
            Make each example practical, relatable, and inspiring for Indian developers.
            """
        )
        
        humor_and_jokes_template = PromptTemplate(
            input_variables=["topic", "learning_context"],
            template="""
            Add appropriate humor and light jokes to make learning {topic} fun and memorable.
            
            Learning Context: {learning_context}
            
            Create humor in these styles:
            
            1. **Tech Puns and Wordplay**
               - Clever puns related to {topic}
               - Programming jokes that aren't cringy
               - Indian context wordplay
            
            2. **Relatable Indian Situations**
               - Traffic jam analogies for performance issues
               - Power cut scenarios for system failures
               - Monsoon flooding for data overflow
            
            3. **Student Life Humor**
               - Engineering college memories
               - Hostel life analogies
               - Exam preparation comparisons
            
            4. **Work Life Jokes**
               - Meeting culture in Indian companies
               - Code review experiences
               - Debugging stories that everyone relates to
            
            5. **Family Context**
               - Explaining tech to Indian parents
               - Managing extended family like managing databases
               - Festival preparations like project management
            
            Keep humor:
            - Clean and professional
            - Culturally appropriate
            - Actually funny (not forced)
            - Educational and memorable
            
            Avoid:
            - Stereotypes or offensive content
            - Overly technical jokes that confuse beginners
            - References that exclude any group
            """
        )
        
        motivational_content_template = PromptTemplate(
            input_variables=["achievement", "difficulty_level", "career_context"],
            template="""
            Create motivational content to inspire students who just learned about {achievement}.
            
            Difficulty Level: {difficulty_level}
            Career Context: {career_context}
            
            Your motivational message should include:
            
            1. **Celebrate the Learning**
               - Acknowledge the effort they put in
               - Highlight what they've accomplished
               - Make them feel proud of their progress
            
            2. **Connect to Real Success**
               - Indian developers who used this skill
               - Companies that value this knowledge
               - Salary ranges and career opportunities
            
            3. **Next Steps Inspiration**
               - What doors this opens for them
               - Advanced concepts they can now tackle
               - Projects they can build with confidence
            
            4. **Community and Belonging**
               - They're part of the global developer community
               - Indian tech ecosystem achievements
               - How they can contribute to India's tech growth
            
            5. **Practical Encouragement**
               - Specific next actions they can take
               - Resources for continued learning
               - Ways to practice and improve
            
            Write like a supportive mentor who genuinely cares about their success.
            Be warm, encouraging, and specific about opportunities.
            """
        )
        
        return {
            "engaging_intro": engaging_intro_template,
            "concept_explanation": concept_explanation_template,
            "indian_examples": indian_examples_template,
            "humor_and_jokes": humor_and_jokes_template,
            "motivational_content": motivational_content_template
        }
    
    def create_engaging_introduction(self, chapter_name: str, course_name: str, 
                                   difficulty_level: str, key_concepts: List[str]) -> str:
        """Create an engaging introduction for a chapter.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            difficulty_level: Difficulty level
            key_concepts: List of key concepts to cover
            
        Returns:
            Engaging introduction content
        """
        concepts_text = ", ".join(key_concepts) if key_concepts else "core programming concepts"
        
        result = self.generate_content(
            "engaging_intro",
            chapter_name=chapter_name,
            course_name=course_name,
            difficulty_level=difficulty_level,
            key_concepts=concepts_text
        )
        
        return result["generated_content"]
    
    def explain_concept_with_stories(self, concept: str, difficulty_level: str, 
                                   real_world_examples: str = "") -> str:
        """Explain a concept using engaging stories and analogies.
        
        Args:
            concept: The concept to explain
            difficulty_level: Target difficulty level
            real_world_examples: Context for real-world examples
            
        Returns:
            Engaging concept explanation
        """
        examples_context = real_world_examples or "Indian tech industry applications"
        
        result = self.generate_content(
            "concept_explanation",
            concept=concept,
            difficulty_level=difficulty_level,
            real_world_examples=examples_context
        )
        
        return result["generated_content"]
    
    def create_indian_examples(self, topic: str, context: str = "", 
                             target_audience: str = "Indian tech students") -> str:
        """Create compelling Indian examples and case studies.
        
        Args:
            topic: Topic to create examples for
            context: Additional context
            target_audience: Target audience description
            
        Returns:
            Indian examples and case studies
        """
        result = self.generate_content(
            "indian_examples",
            topic=topic,
            context=context or "Indian tech ecosystem",
            target_audience=target_audience
        )
        
        return result["generated_content"]
    
    def add_humor_and_jokes(self, topic: str, learning_context: str = "") -> str:
        """Add appropriate humor and jokes to make learning fun.
        
        Args:
            topic: Topic to add humor for
            learning_context: Context of learning
            
        Returns:
            Humor and jokes content
        """
        context = learning_context or "technical learning for Indian students"
        
        result = self.generate_content(
            "humor_and_jokes",
            topic=topic,
            learning_context=context
        )
        
        return result["generated_content"]
    
    def create_motivational_content(self, achievement: str, difficulty_level: str, 
                                  career_context: str = "") -> str:
        """Create motivational content to inspire students.
        
        Args:
            achievement: What the student has achieved
            difficulty_level: Difficulty level
            career_context: Career context
            
        Returns:
            Motivational content
        """
        career_info = career_context or "Indian tech career opportunities"
        
        result = self.generate_content(
            "motivational_content",
            achievement=achievement,
            difficulty_level=difficulty_level,
            career_context=career_info
        )
        
        return result["generated_content"]
    
    def create_comprehensive_content(self, chapter_name: str, course_name: str,
                                   difficulty_level: str, key_concepts: List[str],
                                   main_topics: List[str]) -> Dict[str, str]:
        """Create comprehensive instructional content for a chapter.
        
        Args:
            chapter_name: Name of the chapter
            course_name: Name of the course
            difficulty_level: Difficulty level
            key_concepts: Key concepts to cover
            main_topics: Main topics in the chapter
            
        Returns:
            Dictionary with different types of content
        """
        content = {}
        
        # Create engaging introduction
        content["introduction"] = self.create_engaging_introduction(
            chapter_name, course_name, difficulty_level, key_concepts
        )
        
        # Explain each main topic with stories
        content["concept_explanations"] = {}
        for topic in main_topics:
            content["concept_explanations"][topic] = self.explain_concept_with_stories(
                topic, difficulty_level
            )
        
        # Create Indian examples
        content["indian_examples"] = self.create_indian_examples(
            chapter_name, f"Chapter in {course_name} course"
        )
        
        # Add humor and jokes
        content["humor_content"] = self.add_humor_and_jokes(
            chapter_name, f"Learning {chapter_name} in {course_name}"
        )
        
        # Create motivational content
        content["motivation"] = self.create_motivational_content(
            f"completing {chapter_name}", difficulty_level
        )
        
        return content
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate instructional content based on the content type."""
        if content_type not in self.prompt_templates:
            raise ValueError(f"Unknown content type: {content_type}")
        
        # Format the prompt
        prompt = self._format_prompt(content_type, **kwargs)
        
        # Generate content
        generated_content = self._generate_with_prompt(prompt)
        
        return {
            "generated_content": generated_content,
            "content_type": content_type,
            "parameters": kwargs
        }