"""Project Content Agent for generating engaging, mentor-like content with Indian context."""

from typing import Dict, Any, List, Optional
from langchain_core.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class ProjectContentAgent(BaseAgent):
    """Agent for creating engaging project content with mentoring tone, humor, and Indian context."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for content generation."""
        
        chapter_content_template = PromptTemplate(
            input_variables=["chapter_name", "project_name", "section_goal", "learning_objectives", "tech_stack", "indian_context"],
            template="""
            You are THE MOST LOVED technical mentor in India. You've guided 1000+ students to get jobs at top companies.
            You speak like a caring older sibling who genuinely wants students to succeed. You use humor, Indian references, and practical wisdom.
            
            **Chapter:** {chapter_name}
            **Project:** {project_name}
            **Section Goal:** {section_goal}
            **Learning Objectives:** {learning_objectives}
            **Tech Stack:** {tech_stack}
            **Indian Context:** {indian_context}
            
            Write chapter content that makes students think "Yaar, this mentor really gets me!" 
            
            # {chapter_name}
            
            ## 🎯 What We're Building Today
            
            [Start with an engaging hook - maybe a relatable scenario like "Remember when you tried to book train tickets during Diwali rush?" or "Ever wondered how Swiggy knows exactly when your food will arrive?"]
            
            Today we're going to solve [specific problem] by building [specific feature/component]. By the end of this chapter, you'll not only understand how to build this, but you'll also know why companies like [Indian company example] use similar approaches.
            
            **Real Talk:** This might seem complex at first (trust me, even senior developers at Flipkart started exactly where you are), but we'll break it down step by step. No one becomes a pro overnight - not even those IIT graduates you see on LinkedIn! 😄
            
            ## 📚 Before We Start Coding...
            
            ### Why This Chapter Matters 🤔
            
            [Explain the real-world importance with Indian context]
            - How this solves actual problems for Indian users
            - Why companies like Paytm, Ola, or Zomato need this functionality
            - What you'll be able to say in interviews about this feature
            
            ### The Big Picture 🖼️
            
            Think of this like [funny Indian analogy - e.g., "organizing a wedding in India" or "managing a cricket team" or "running a chai stall"]. You need to:
            1. [Step 1 with analogy]
            2. [Step 2 with analogy] 
            3. [Step 3 with analogy]
            
            **Pro Tip from Experience:** I've seen students rush into coding without understanding the "why." Don't be that person! Take 5 minutes to understand the problem first. Future you will thank present you! 🙏
            
            ## 🛠️ Let's Build This Thing!
            
            ### Step 1: Understanding the Requirements
            
            Before we write a single line of code, let's think like a product manager at [relevant Indian startup]. What would they want?
            
            **User Story:** As a [type of Indian user], I want to [specific need] so that [benefit in Indian context].
            
            **Example:** "As a college student in Bangalore, I want to find affordable PG accommodations near my campus so that I don't spend my entire scholarship on rent."
            
            ### Step 2: Technical Approach
            
            Now, how do we solve this technically? Here's how I'd approach it (and this is exactly how teams at [Indian tech company] would think about it):
            
            **Architecture Decision:**
            ```
            [Simple ASCII diagram or explanation]
            User → Frontend → API → Database → Response
            ```
            
            **Why This Approach?**
            - [Reason 1] - Scales well (important when you have millions of users like Indian apps do)
            - [Reason 2] - Easy to maintain (crucial for small startup teams)
            - [Reason 3] - Cost-effective (every rupee matters in Indian startups!)
            
            ### Step 3: Implementation (Finally, Some Code! 🎉)
            
            **Quick Pep Talk:** Don't worry if this feels overwhelming. Even the CTO of [famous Indian startup] started by copying code from Stack Overflow. The difference between a beginner and expert is that experts know WHY the code works. Let's understand both the HOW and WHY.
            
            #### Phase 1: Setting Up the Foundation
            
            First, let's set up our basic structure:
            
            ```{tech_stack.lower()}
            // This is like setting up the foundation of your house
            // You can't see it, but everything depends on it!
            
            [Specific starter code with comments explaining each part]
            ```
            
            **What's Happening Here?**
            - Line X: [Explanation in simple terms]
            - Line Y: [Why this is important]
            - Line Z: [How this helps our users]
            
            **Indian Context Note:** Notice how we're thinking about [specific Indian consideration - like mobile-first design, low bandwidth, multilingual support, etc.]? That's because [explanation of why this matters in India].
            
            #### Phase 2: Adding the Core Logic
            
            Now for the interesting part - the actual problem-solving logic:
            
            ```{tech_stack.lower()}
            // This is where the magic happens!
            // Think of this as the brain of your application
            
            [Core implementation code with detailed comments]
            ```
            
            **Code Walkthrough:**
            1. **What we're doing:** [Simple explanation]
            2. **Why this approach:** [Reasoning with real-world analogy]
            3. **How it helps users:** [User benefit]
            
            **Debugging Tip:** If this doesn't work on your first try, don't panic! Even developers at [Indian tech company] spend 70% of their time debugging. It's not a bug, it's a learning opportunity! 😅
            
            #### Phase 3: Making It User-Friendly
            
            Code that works is good. Code that users love is GREAT! Let's add some polish:
            
            ```{tech_stack.lower()}
            // Making it smooth like butter chicken! 🧈
            // This is what separates good developers from great ones
            
            [User experience improvements with explanations]
            ```
            
            **Why This Matters:** Users don't care about your beautiful code if the experience is terrible. This is why apps like [Indian app example] are successful - they prioritize user experience over showing off their technical skills.
            
            ## 🧪 Testing Your Implementation
            
            **Reality Check Time:** Does your implementation actually work? Let's test it like a QA engineer at [Indian company]:
            
            ### Test Case 1: Happy Path
            - **Scenario:** [Normal user behavior]
            - **Expected Result:** [What should happen]
            - **Test It:** [How to verify]
            
            ### Test Case 2: Edge Cases
            - **Scenario:** [Unusual but possible situation]
            - **Why Test This:** [Real-world relevance]
            - **Expected Result:** [How it should gracefully handle]
            
            ### Test Case 3: Error Handling
            - **Scenario:** [When things go wrong]
            - **Indian Context:** [Why this is especially important in India - network issues, power cuts, etc.]
            - **Implementation:** [How to handle gracefully]
            
            **Testing Mantra:** If you're not testing edge cases, your users will find them for you - and they won't be happy about it! 😬
            
            ## 💡 Making It Production-Ready
            
            ### Performance Considerations
            
            **Think Like a Startup:** Your app needs to work smoothly even when thousands of users are using it simultaneously (like during IPL season or festival sales!).
            
            **Optimization Tips:**
            1. [Performance tip 1] - Why this matters for Indian users
            2. [Performance tip 2] - How this saves money on servers
            3. [Performance tip 3] - Why this improves user experience
            
            ### Security Best Practices
            
            **Real Talk:** Security isn't optional. With digital payments becoming common in India, users trust apps with their money. Don't break that trust!
            
            **Essential Security Measures:**
            - [Security practice 1] - [Why this prevents specific attacks]
            - [Security practice 2] - [How this protects user data]
            - [Security practice 3] - [Why this is legally required in India]
            
            ## 🚀 Career Connection
            
            ### How to Talk About This in Interviews
            
            **Interviewer:** "Tell me about a challenging feature you implemented."
            
            **Your Answer:** "I built [feature name] which [specific problem it solved]. The interesting challenge was [technical challenge], which I solved by [your approach]. This is similar to how [Indian company] handles [similar scenario]. The result was [impact on users/metrics]."
            
            **Why This Works:** You're showing problem-solving skills, technical knowledge, industry awareness, and impact measurement - exactly what Indian tech companies want!
            
            ### LinkedIn Post Template
            
            ```
            🚀 Just implemented [feature name] for my [project name] project!
            
            Key learnings:
            ✅ [Technical skill gained]
            ✅ [Problem-solving insight]
            ✅ [Industry knowledge gained]
            
            This feature [specific user benefit]. Similar to how [Indian startup] approaches [similar problem].
            
            #TechSkills #ProjectBuilding #[TechStack] #IndianStartups
            ```
            
            ## 🤔 Reflection Questions
            
            Before moving to the next chapter, think about:
            
            1. **User Impact:** How does this feature make life better for your target users?
            2. **Technical Growth:** What new concepts did you learn that you can apply elsewhere?
            3. **Business Understanding:** Why would a startup prioritize building this feature?
            4. **Next Steps:** What would you add next if this were a real product?
            
            ## 🎯 What's Next?
            
            **Congratulations!** 🎉 You just built [achievement]. That's exactly the kind of problem-solving that gets people hired at [relevant companies].
            
            **Coming Up:** Next, we'll tackle [next topic], which will teach you [next skill]. This is crucial for [career relevance].
            
            **Homework:** Try explaining what you just built to a friend or family member. If they understand it, you've truly mastered it! Plus, practice explaining technical concepts - it's a superpower in interviews.
            
            **Motivation:** You're not just learning to code. You're learning to solve real problems that affect millions of Indians. That's the mindset that creates successful developers and entrepreneurs! 💪
            
            ---
            
            **Quick Shoutout:** If you're stuck, don't suffer in silence! Post your questions in our community. We're all rooting for your success! 🤗
            
            Keep building, keep learning, and remember - every expert was once a beginner! 🌟
            """
        )
        
        assignment_template = PromptTemplate(
            input_variables=["assignment_name", "project_context", "skills_to_practice", "deliverable", "indian_context"],
            template="""
            You are creating an assignment that's engaging, practical, and directly relevant to getting hired in India's tech industry.
            
            **Assignment:** {assignment_name}
            **Project Context:** {project_context}
            **Skills to Practice:** {skills_to_practice}
            **Deliverable:** {deliverable}
            **Indian Context:** {indian_context}
            
            # {assignment_name}
            
            ## 🎯 Mission Brief
            
            **Your Challenge:** [Describe the challenge like it's a real startup task]
            
            **Why This Matters:** This assignment simulates exactly what you'd be asked to do at [relevant Indian startup]. I've seen similar tasks given to candidates during interviews at [company examples].
            
            **Real Story:** A student from our previous batch got hired at [Indian company] specifically because they could demonstrate this exact skill during their interview. True story! 💯
            
            ## 📋 What You Need to Deliver
            
            **Primary Deliverable:** {deliverable}
            
            **Success Criteria:**
            ✅ [Specific measurable criterion 1]
            ✅ [Specific measurable criterion 2]  
            ✅ [Specific measurable criterion 3]
            ✅ [User experience criterion]
            ✅ [Code quality criterion]
            
            **Bonus Points (Optional but Impressive):**
            🌟 [Advanced feature that would impress employers]
            🌟 [Optimization that shows senior-level thinking]
            🌟 [Innovation that demonstrates creativity]
            
            ## 🛣️ Step-by-Step Approach
            
            **Don't just jump into coding!** Follow this proven process that successful developers use:
            
            ### Phase 1: Understanding & Research (30 minutes)
            1. **User Research:** Who will use this feature? What are their pain points?
            2. **Competitive Analysis:** How do [Indian app examples] handle similar features?
            3. **Technical Research:** What approaches are available? What are the trade-offs?
            
            **Deliverable:** A simple document answering these questions
            
            ### Phase 2: Planning & Design (45 minutes)
            1. **Feature Breakdown:** Break the big problem into smaller, manageable pieces
            2. **Technical Architecture:** How will the pieces fit together?
            3. **User Flow:** Step-by-step journey from user's perspective
            
            **Deliverable:** Simple diagrams or sketches (even hand-drawn is fine!)
            
            ### Phase 3: Implementation (2-3 hours)
            1. **Start Small:** Build the simplest version that works
            2. **Test Early:** Verify each piece works before moving to the next
            3. **Iterate:** Improve based on what you learn
            
            **Deliverable:** Working code with proper comments
            
            ### Phase 4: Polish & Documentation (30 minutes)
            1. **User Testing:** Try using your feature as a real user would
            2. **Code Review:** Clean up and document your code
            3. **Showcase Prep:** Prepare to explain your work
            
            **Deliverable:** Polished, documented solution ready to showcase
            
            ## 💡 Hints & Tips
            
            **Stuck? Try This:**
            1. **Break it down further:** If a task feels overwhelming, make it smaller
            2. **Google like a pro:** Search for "[specific problem] in [technology]"
            3. **Learn from others:** Look at open-source projects for inspiration
            4. **Ask for help:** Post in our community - we're here to help!
            
            **Time Management:**
            - Set a timer for each phase
            - Don't aim for perfection on first try
            - It's better to have a working simple solution than a broken complex one
            
            **Indian Context Considerations:**
            - [Specific consideration 1] - Why this matters for Indian users
            - [Specific consideration 2] - How this affects implementation
            - [Specific consideration 3] - What this means for scalability
            
            ## 🧪 Testing Your Solution
            
            **Test Like a User:** 
            - Can you complete the main user journey without confusion?
            - Does it work on mobile (crucial in India)?
            - How does it behave with slow internet?
            
            **Test Like a Developer:**
            - Does your code handle edge cases?
            - Are error messages helpful?
            - Is your code readable by someone else?
            
            **Test Like a Business Owner:**
            - Does this solve the actual problem?
            - Would users pay for this feature?
            - Can this scale to thousands of users?
            
            ## 📤 Submission Guidelines
            
            **What to Submit:**
            1. **GitHub Repository:** With clean, commented code
            2. **README File:** Explaining what you built and how to run it
            3. **Demo Video:** 2-3 minute walkthrough showing it working
            4. **Reflection Report:** What you learned and what you'd do differently
            
            **GitHub Repository Structure:**
            ```
            your-project-name/
            ├── README.md (clear instructions)
            ├── src/ (your source code)
            ├── docs/ (any documentation)
            └── demo/ (screenshots or demo files)
            ```
            
            **README Template:**
            ```markdown
            # [Your Project Name]
            
            ## Problem Statement
            [What problem does this solve?]
            
            ## Solution
            [How does your implementation solve it?]
            
            ## Technologies Used
            [List of technologies and why you chose them]
            
            ## How to Run
            [Step-by-step instructions]
            
            ## Key Features
            [What can users do with this?]
            
            ## Challenges & Learnings
            [What was difficult and what you learned]
            
            ## Next Steps
            [What would you add next?]
            ```
            
            ## 🏆 Evaluation Criteria
            
            **Technical Excellence (40%):**
            - Code quality and organization
            - Proper error handling
            - Performance considerations
            
            **Problem Solving (30%):**
            - Understanding of the problem
            - Appropriateness of solution
            - Handling of edge cases
            
            **User Experience (20%):**
            - Ease of use
            - Mobile responsiveness
            - Clear feedback to users
            
            **Documentation & Communication (10%):**
            - Clear README and code comments
            - Quality of demo video
            - Reflection and learning articulation
            
            ## 🌟 Success Stories
            
            **Inspiration:** Here are some ways previous students showcased similar work:
            - [Student A] got hired at [Company] after showing a similar feature in their interview
            - [Student B] used this project as the foundation for their own startup
            - [Student C] got promoted after applying these skills at their current job
            
            ## 🚀 Submission & Next Steps
            
            **Submit Your Work:** [Submission link/form will be provided]
            
            **After Submission:**
            1. We'll review your work and provide detailed feedback
            2. Outstanding submissions will be featured in our showcase
            3. You'll receive a completion certificate for your portfolio
            
            **Community Showcase:** With your permission, we'd love to feature exceptional work on our social media and website. It's great exposure for your personal brand!
            
            ---
            
            **Remember:** This isn't just an assignment - it's a stepping stone to your dream job. Give it your best effort, but don't stress about perfection. Every professional developer started exactly where you are! 💪
            
            **You've got this!** 🌟
            """
        )
        
        intro_template = PromptTemplate(
            input_variables=["project_name", "problem_statement", "target_users", "tech_stack", "career_relevance"],
            template="""
            You are introducing a life-changing project to ambitious Indian students and professionals. Make them excited!
            
            **Project:** {project_name}
            **Problem:** {problem_statement}
            **Target Users:** {target_users}
            **Tech Stack:** {tech_stack}
            **Career Relevance:** {career_relevance}
            
            # Welcome to Building {project_name}! 🚀
            
            ## 🔥 Why This Project Will Change Your Career
            
            **Real Talk:** You know those portfolio projects that everyone builds? Todo lists, weather apps, basic calculators? Yeah, this isn't one of those. 
            
            We're building something that could actually become the next big Indian startup. Something that solves a REAL problem affecting millions of Indians. Something that will make recruiters at [relevant companies] stop scrolling and start calling.
            
            **True Story:** A student from Pune built something similar last year and got hired at [Indian unicorn] with a 40% salary jump. Another student from Bangalore used their project as the foundation for their own startup and raised ₹50 lakhs in seed funding. These aren't exceptional cases - this is what happens when you build something meaningful instead of just following tutorials! 💪
            
            ## 🎯 The Problem We're Solving
            
            [Embed a relevant video introduction explaining the problem]
            
            Let's be honest - {problem_statement}
            
            **Why This Problem Matters:**
            - [Specific impact on Indian users]
            - [Market size and opportunity]  
            - [Why existing solutions fail]
            - [What success would look like]
            
            **Personal Connection:** I bet you've faced this problem yourself. Maybe when you were [relatable scenario]. Or when your family was trying to [common Indian situation]. That frustration you felt? That's exactly what motivates great entrepreneurs and developers! 🎯
            
            ## 💡 Our Solution
            
            We're going to build {project_name} - a platform that [core solution in one sentence].
            
            **Think of it like this:** [Powerful analogy using Indian context - like comparing to how local businesses work, how families make decisions, how cricket teams coordinate, etc.]
            
            **What Makes This Special:**
            1. **Indian-First Design:** Built specifically for how Indians behave and what they need
            2. **Real Problem Solving:** Not just a technical exercise, but a genuine solution
            3. **Scalable Architecture:** Uses the same patterns as successful Indian startups
            4. **Career Boosting:** The exact kind of project that impresses hiring managers
            
            ## 🏗️ What We'll Build Together
            
            **Core Features:**
            - [Feature 1] - [Why users will love this]
            - [Feature 2] - [How this solves the problem] 
            - [Feature 3] - [What makes this unique]
            - [Feature 4] - [Why this impresses employers]
            
            **Technical Highlights:**
            - Built with {tech_stack} (exactly what companies are hiring for!)
            - Includes authentication, database design, API development
            - Mobile-responsive (crucial for Indian market)
            - Deployed to production with monitoring
            - Comprehensive documentation and testing
            
            **Business Impact:**
            - Could realistically serve [number] of Indian users
            - Addresses a [size] market opportunity
            - Has clear monetization potential
            - Solves a problem people would pay for
            
            ## 🚀 Your Career Transformation
            
            **Before This Project:** You're another developer with basic skills and tutorial projects
            **After This Project:** You're a problem-solver with real-world experience and a portfolio that stands out
            
            **Interview Confidence:** Instead of saying "I built a todo app," you'll say "I identified a real problem affecting millions of Indians and built a scalable solution that could serve thousands of users. Let me show you the architecture and business impact..."
            
            **Skills You'll Gain:**
            - Full-stack development with modern technologies
            - Product thinking and user research
            - Business analysis and market understanding  
            - Professional development workflows
            - Deployment and DevOps practices
            - Technical communication and documentation
            
            **Career Opportunities This Opens:**
            - Product-focused startups (they love builders who understand users)
            - Growth-stage companies (they need people who can own features end-to-end)
            - Consulting roles (you'll understand business problems, not just code)
            - Entrepreneurship (you'll have the skills to build your own ideas)
            
            ## 📊 Project Overview
            
            **Timeline:** [Duration] of intensive, hands-on building
            **Commitment:** 15-20 hours per week (totally manageable alongside studies/work)
            **Support:** Community, office hours, and mentor guidance throughout
            **Outcome:** Production-ready application + portfolio + interview confidence
            
            **Week-by-Week Journey:**
            - Weeks 1-2: Problem research and technical planning
            - Weeks 3-4: Foundation and architecture  
            - Weeks 5-6: Core feature development
            - Weeks 7-8: Advanced features and polish
            - Weeks 9-10: Deployment and career preparation
            
            ## 🌟 Success Stories from Previous Builders
            
            **[Student Name] - Software Engineer at [Indian Unicorn]:**
            "The project I built using this methodology was the main talking point in all my interviews. Recruiters were impressed that I could discuss business impact, not just technical implementation."
            
            **[Student Name] - Startup Founder:**
            "This project taught me to think like a product manager, not just a developer. I used these skills to identify another problem and build my own startup. We're now a team of 12!"
            
            **[Student Name] - Senior Developer at [MNC]:**
            "When I showed my project to the hiring manager, she said it was exactly the kind of problem-solving they needed on their team. I got the job and a 50% salary increase!"
            
            ## 🎯 Ready to Transform Your Career?
            
            **This isn't just another course. This is your launchpad to becoming the kind of developer that companies fight to hire.**
            
            **What You Need:**
            - Basic programming knowledge (we'll teach you everything else)
            - Willingness to think beyond just coding
            - Commitment to building something meaningful
            - Excitement about solving real problems
            
            **What You DON'T Need:**
            - Years of experience (enthusiasm beats experience every time)
            - Expensive tools or courses (we'll use free, industry-standard tools)
            - Perfect code on first try (we'll iterate and improve together)
            
            ## 🚀 Let's Start Building!
            
            **Your journey from tutorial-follower to problem-solver starts now.**
            
            In the next chapter, we'll dive deep into understanding the problem from our users' perspective. You'll learn how successful Indian startups approach market research and user analysis.
            
            **Fair Warning:** After completing this project, you might never want to build another todo app again. You'll be addicted to solving real problems and creating actual value. Consider yourself warned! 😄
            
            **Ready? Let's go change your career trajectory!** 🌟
            
            ---
            
            **Community Connect:** Join our WhatsApp group [link] where 500+ builders share progress, help each other, and celebrate wins. You're not just learning alone - you're joining a movement of Indian developers who believe in building meaningful things!
            """
        )
        
        return {
            "chapter_content": chapter_content_template,
            "assignment": assignment_template,
            "intro": intro_template
        }
    
    def generate_chapter_content(self, chapter_name: str, project_name: str, 
                               section_goal: str, learning_objectives: List[str], 
                               tech_stack: str, indian_context: str = "") -> str:
        """Generate engaging chapter content with mentoring tone.
        
        Args:
            chapter_name: Name of the chapter
            project_name: Name of the project
            section_goal: Goal of this section
            learning_objectives: What students should learn
            tech_stack: Technology stack being used
            indian_context: Specific Indian context for the project
            
        Returns:
            Complete chapter content in MDX format
        """
        objectives_text = "\n".join([f"- {obj}" for obj in learning_objectives])
        context = indian_context or f"Building solutions for Indian users with {tech_stack}"
        
        result = self.generate_content(
            "chapter_content",
            chapter_name=chapter_name,
            project_name=project_name,
            section_goal=section_goal,
            learning_objectives=objectives_text,
            tech_stack=tech_stack,
            indian_context=context
        )
        
        return result["generated_content"]
    
    def generate_assignment(self, assignment_name: str, project_context: str, 
                          skills_to_practice: List[str], deliverable: str,
                          indian_context: str = "") -> str:
        """Generate practical assignment with clear guidelines.
        
        Args:
            assignment_name: Name of the assignment
            project_context: Context within the project
            skills_to_practice: Skills this assignment practices
            deliverable: What students should submit
            indian_context: Indian market context
            
        Returns:
            Complete assignment content
        """
        skills_text = ", ".join(skills_to_practice)
        context = indian_context or "Relevant to Indian tech industry"
        
        result = self.generate_content(
            "assignment",
            assignment_name=assignment_name,
            project_context=project_context,
            skills_to_practice=skills_text,
            deliverable=deliverable,
            indian_context=context
        )
        
        return result["generated_content"]
    
    def generate_project_introduction(self, project_name: str, problem_statement: str,
                                    target_users: str, tech_stack: str, 
                                    career_relevance: str) -> str:
        """Generate an exciting project introduction.
        
        Args:
            project_name: Name of the project
            problem_statement: Problem being solved
            target_users: Who will use this
            tech_stack: Technologies used
            career_relevance: How this helps careers
            
        Returns:
            Engaging project introduction
        """
        result = self.generate_content(
            "intro",
            project_name=project_name,
            problem_statement=problem_statement,
            target_users=target_users,
            tech_stack=tech_stack,
            career_relevance=career_relevance
        )
        
        return result["generated_content"]
    
    def generate_section_intro(self, section_name: str, section_goal: str, 
                             chapters: List[str], project_context: str) -> str:
        """Generate introduction content for a section.
        
        Args:
            section_name: Name of the section
            section_goal: Goal of this section
            chapters: List of chapter names in this section
            project_context: Overall project context
            
        Returns:
            Section introduction content
        """
        chapters_list = "\n".join([f"- {chapter}" for chapter in chapters])
        
        intro_content = f"""
        # {section_name}
        
        ## 🎯 What We'll Accomplish
        
        {section_goal}
        
        By the end of this section, you'll have hands-on experience with the exact skills that Indian tech companies are hiring for right now.
        
        ## 📚 Chapters in This Section
        
        {chapters_list}
        
        Each chapter builds on the previous one, so make sure to complete them in order. And remember - it's not about speed, it's about understanding!
        
        ## 💡 Section Strategy
        
        **Our Approach:** We'll start with understanding the problem from a user perspective, then move into technical implementation, and finally ensure everything is production-ready.
        
        **Why This Order:** This is exactly how product teams at successful Indian startups work. You're not just learning to code - you're learning to think like a professional developer!
        
        **Ready? Let's dive in!** 🚀
        """
        
        return intro_content
    
    def add_code_examples(self, content: str, tech_stack: str, 
                         feature_description: str) -> str:
        """Add relevant code examples to content.
        
        Args:
            content: Existing content
            tech_stack: Technology stack
            feature_description: What the code should demonstrate
            
        Returns:
            Content with integrated code examples
        """
        code_prompt = f"""
        Add practical code examples to this content for {tech_stack} technology.
        The code should demonstrate: {feature_description}
        
        Include:
        1. Starter code with extensive comments
        2. Step-by-step implementation
        3. Error handling examples
        4. Best practices for Indian market (mobile-first, performance, etc.)
        
        Make sure code is:
        - Production-ready quality
        - Well-commented for learning
        - Follows industry standards
        - Includes common pitfalls to avoid
        
        Original content: {content}
        """
        
        enhanced_content = self._generate_with_prompt(code_prompt)
        return enhanced_content
    
    def add_indian_context(self, content: str, domain: str) -> str:
        """Add relevant Indian context and examples to content.
        
        Args:
            content: Original content
            domain: Domain/industry context (fintech, edtech, etc.)
            
        Returns:
            Content enhanced with Indian context
        """
        context_prompt = f"""
        Enhance this content with relevant Indian context for the {domain} domain.
        
        Add:
        1. Examples from successful Indian startups
        2. Indian user behavior considerations
        3. Local market insights
        4. Cultural references that resonate
        5. Regulatory considerations for India
        
        Keep the tone engaging and mentor-like.
        
        Original content: {content}
        """
        
        enhanced_content = self._generate_with_prompt(context_prompt)
        return enhanced_content
    
    def generate_video_script(self, topic: str, duration: str = "5-7 minutes",
                            learning_objective: str = "") -> str:
        """Generate script for video content.
        
        Args:
            topic: Topic for the video
            duration: Target duration
            learning_objective: What viewers should learn
            
        Returns:
            Video script with timing and visual cues
        """
        script_prompt = f"""
        Create a {duration} video script for: {topic}
        Learning objective: {learning_objective}
        
        Format:
        [Time] - Visual Cue: Narration
        
        Style: Conversational, encouraging, with Indian context
        Include: Screen recordings, diagrams, real examples
        
        Make it engaging for Indian students and professionals.
        """
        
        script = self._generate_with_prompt(script_prompt)
        return script
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate project content based on the content type."""
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