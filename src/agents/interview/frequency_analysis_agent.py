"""Frequency Analysis Agent for determining question frequency and company patterns."""

from typing import Dict, Any, List, Optional
from langchain.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class FrequencyAnalysisAgent(BaseAgent):
    """Agent for analyzing question frequency and company-specific patterns."""
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for frequency analysis."""
        
        frequency_analysis_template = PromptTemplate(
            input_variables=["question", "sheet_topic", "difficulty_context"],
            template="""
            You are an expert interview data analyst with access to 500+ interview experiences across Indian tech companies.
            
            **Question:** {question}
            **Topic/Sheet:** {sheet_topic}
            **Context:** {difficulty_context}
            
            Based on your extensive experience, analyze this question and provide:
            
            ## Frequency Analysis
            
            **Overall Frequency:** [Very High/High/Medium/Low/Very Low]
            
            **Reasoning:**
            - Why this question is asked frequently/rarely
            - What specific skills it tests
            - How important this concept is in the industry
            
            ## Company-wise Breakdown
            
            **FAANG Companies (Google, Meta, Amazon, Apple, Netflix):**
            - Frequency: [Very High/High/Medium/Low/Very Low]
            - Context: When they ask this (screening/technical/system design)
            - Variations: How they might twist this question
            
            **Indian Unicorns (Flipkart, Paytm, Ola, Swiggy, Zomato, BYJU'S):**
            - Frequency: [Very High/High/Medium/Low/Very Low]
            - Focus: What they care about most
            - Real scenarios: Practical contexts they use
            
            **Mid-size Startups (Razorpay, Freshworks, Zoho, InMobi):**
            - Frequency: [Very High/High/Medium/Low/Very Low]
            - Practical focus: How they relate it to real work
            - Growth stage relevance: Why they ask this
            
            **Service Companies (TCS, Infosys, Wipro, Accenture):**
            - Frequency: [Very High/High/Medium/Low/Very Low]
            - Style: How they typically frame this
            - Client project context: Real-world applications
            
            ## Interview Round Analysis
            
            **Phone/Video Screening:** [Yes/No] - Likelihood and typical format
            **Technical Round 1:** [Yes/No] - How it's usually asked
            **Technical Round 2:** [Yes/No] - Advanced variations
            **System Design:** [Yes/No] - When it comes up in design discussions
            **Manager Round:** [Yes/No] - High-level conceptual questions
            
            ## Experience Level Breakdown
            
            **Fresher (0-2 years):**
            - Probability: [High/Medium/Low]
            - Expected depth: Basic/intermediate concepts
            - Common follow-ups: What they ask next
            
            **Mid-level (2-5 years):**
            - Probability: [High/Medium/Low]
            - Expected depth: Implementation details
            - Architecture focus: Design considerations
            
            **Senior (5+ years):**
            - Probability: [High/Medium/Low]
            - Expected depth: Trade-offs and scaling
            - Leadership angle: Team and mentoring aspects
            
            ## Seasonal/Trends Analysis
            
            **Peak Hiring Seasons:**
            - Jan-Mar: [High/Medium/Low frequency]
            - Jul-Sep: [High/Medium/Low frequency]
            - Campus hiring: [Relevant/Not relevant]
            
            **Technology Trends:**
            - Rising popularity: [Yes/No] - Why
            - Market demand: Current industry need
            - Future relevance: 2-3 year outlook
            
            Be specific, data-driven, and realistic based on actual Indian tech interview patterns.
            """
        )
        
        company_specific_analysis_template = PromptTemplate(
            input_variables=["question", "company_category", "position_level"],
            template="""
            Deep dive into how different company categories would ask this question:
            
            **Question:** {question}
            **Company Category:** {company_category}
            **Position Level:** {position_level}
            
            ## Detailed Company Analysis
            
            **Interview Style for this Category:**
            - Typical format and approach
            - What they prioritize in answers
            - Common variations they use
            - Red flags they watch for
            
            **Specific Companies in this Category:**
            List 5-6 specific companies and how each might ask this:
            1. Company A: Their unique angle
            2. Company B: Their focus area
            3. Company C: Their practical context
            
            **Success Metrics:**
            - What constitutes a good answer for these companies
            - Common mistakes candidates make
            - How to stand out in responses
            
            Provide actionable, company-specific insights.
            """
        )
        
        return {
            "frequency_analysis": frequency_analysis_template,
            "company_specific": company_specific_analysis_template
        }
    
    def analyze_question_frequency(self, question: str, sheet_topic: str, 
                                 difficulty_context: str = "General interview context") -> Dict[str, Any]:
        """Analyze the frequency and patterns of an interview question.
        
        Args:
            question: The interview question to analyze
            sheet_topic: Topic/subject of the interview sheet
            difficulty_context: Context about difficulty level
            
        Returns:
            Comprehensive frequency analysis
        """
        result = self.generate_content(
            "frequency_analysis",
            question=question,
            sheet_topic=sheet_topic,
            difficulty_context=difficulty_context
        )
        
        # Parse the analysis to extract structured data
        analysis_text = result["generated_content"]
        structured_analysis = self._parse_frequency_analysis(analysis_text)
        
        return {
            "question": question,
            "overall_frequency": structured_analysis.get("overall_frequency", "Medium"),
            "company_breakdown": structured_analysis.get("company_breakdown", {}),
            "round_analysis": structured_analysis.get("round_analysis", {}),
            "experience_breakdown": structured_analysis.get("experience_breakdown", {}),
            "seasonal_trends": structured_analysis.get("seasonal_trends", {}),
            "full_analysis": analysis_text,
            "confidence_score": self._calculate_confidence_score(question, sheet_topic)
        }
    
    def get_company_specific_insights(self, question: str, company_category: str, 
                                    position_level: str = "Mid-level") -> Dict[str, Any]:
        """Get detailed insights for specific company categories.
        
        Args:
            question: Interview question
            company_category: Type of company (FAANG, Unicorn, etc.)
            position_level: Experience level
            
        Returns:
            Company-specific analysis
        """
        result = self.generate_content(
            "company_specific",
            question=question,
            company_category=company_category,
            position_level=position_level
        )
        
        return {
            "company_category": company_category,
            "position_level": position_level,
            "analysis": result["generated_content"],
            "actionable_insights": self._extract_actionable_insights(result["generated_content"])
        }
    
    def batch_analyze_questions(self, questions: List[str], sheet_topic: str) -> Dict[str, Any]:
        """Analyze frequency for a batch of questions.
        
        Args:
            questions: List of questions to analyze
            sheet_topic: Topic of the sheet
            
        Returns:
            Batch analysis results
        """
        batch_results = []
        frequency_distribution = {"Very High": 0, "High": 0, "Medium": 0, "Low": 0, "Very Low": 0}
        
        for question in questions:
            try:
                analysis = self.analyze_question_frequency(question, sheet_topic)
                batch_results.append(analysis)
                
                # Update frequency distribution
                freq = analysis.get("overall_frequency", "Medium")
                if freq in frequency_distribution:
                    frequency_distribution[freq] += 1
                    
            except Exception as e:
                self.logger.error(f"Error analyzing question: {question[:50]}... - {str(e)}")
        
        return {
            "sheet_topic": sheet_topic,
            "total_questions": len(questions),
            "analyzed_questions": len(batch_results),
            "frequency_distribution": frequency_distribution,
            "detailed_results": batch_results,
            "recommendations": self._generate_batch_recommendations(batch_results, frequency_distribution)
        }
    
    def get_trending_questions(self, sheet_topic: str, time_period: str = "current") -> List[Dict[str, Any]]:
        """Get trending questions for a topic based on market analysis.
        
        Args:
            sheet_topic: Topic to analyze
            time_period: Time period for trends (current, emerging, declining)
            
        Returns:
            List of trending questions with context
        """
        trending_prompt = f"""
        Based on current Indian tech market trends, what interview questions are trending for {sheet_topic}?
        
        Time period: {time_period}
        
        List 10-15 questions that are:
        - Currently hot in interviews
        - Reflecting market demands
        - Asked by top companies
        - Relevant to industry changes
        
        For each question, provide:
        1. The question
        2. Why it's trending
        3. Which companies are asking it
        4. Difficulty level
        5. Market relevance score (1-10)
        """
        
        trending_content = self._generate_with_prompt(trending_prompt)
        return self._parse_trending_questions(trending_content)
    
    def _parse_frequency_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """Parse the frequency analysis text into structured data."""
        structured = {
            "overall_frequency": "Medium",
            "company_breakdown": {},
            "round_analysis": {},
            "experience_breakdown": {},
            "seasonal_trends": {}
        }
        
        lines = analysis_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Extract overall frequency
            if "Overall Frequency:" in line:
                freq = line.split(":")[-1].strip()
                for level in ["Very High", "High", "Medium", "Low", "Very Low"]:
                    if level in freq:
                        structured["overall_frequency"] = level
                        break
            
            # Extract company-specific data
            elif any(company in line for company in ["FAANG", "Unicorns", "Mid-size", "Service"]):
                current_section = "companies"
            elif current_section == "companies" and "Frequency:" in line:
                freq = line.split(":")[-1].strip()
                # Add to company breakdown (simplified)
                
            # Extract round analysis
            elif any(round_type in line for round_type in ["Screening", "Technical", "System Design", "Manager"]):
                current_section = "rounds"
                
            # Extract experience breakdown
            elif any(level in line for level in ["Fresher", "Mid-level", "Senior"]):
                current_section = "experience"
        
        return structured
    
    def _calculate_confidence_score(self, question: str, sheet_topic: str) -> float:
        """Calculate confidence score for the frequency analysis."""
        # Simple heuristic based on question characteristics
        score = 0.7  # Base score
        
        # Adjust based on question complexity
        if len(question.split()) > 15:
            score += 0.1  # More complex questions
        
        # Adjust based on common keywords
        common_keywords = ["what", "how", "explain", "difference", "implement", "design"]
        if any(keyword in question.lower() for keyword in common_keywords):
            score += 0.1
        
        # Adjust based on topic familiarity
        popular_topics = ["javascript", "python", "react", "node", "database", "system design"]
        if any(topic in sheet_topic.lower() for topic in popular_topics):
            score += 0.1
        
        return min(score, 1.0)
    
    def _extract_actionable_insights(self, analysis_text: str) -> List[str]:
        """Extract actionable insights from analysis text."""
        insights = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ["tip:", "insight:", "recommendation:", "key:"]):
                insights.append(line.strip())
        
        return insights[:5]  # Top 5 insights
    
    def _generate_batch_recommendations(self, batch_results: List[Dict], 
                                      frequency_distribution: Dict[str, int]) -> List[str]:
        """Generate recommendations based on batch analysis."""
        recommendations = []
        
        total_questions = sum(frequency_distribution.values())
        if total_questions == 0:
            return recommendations
        
        # Analyze distribution
        high_freq_ratio = (frequency_distribution.get("Very High", 0) + 
                          frequency_distribution.get("High", 0)) / total_questions
        
        if high_freq_ratio > 0.6:
            recommendations.append("This sheet has many high-frequency questions - excellent for interview prep")
        elif high_freq_ratio < 0.3:
            recommendations.append("Consider adding more commonly asked questions to improve relevance")
        
        # Check for balance
        medium_ratio = frequency_distribution.get("Medium", 0) / total_questions
        if medium_ratio > 0.4:
            recommendations.append("Good balance of question difficulties for comprehensive preparation")
        
        return recommendations
    
    def _parse_trending_questions(self, trending_content: str) -> List[Dict[str, Any]]:
        """Parse trending questions from generated content."""
        questions = []
        lines = trending_content.split('\n')
        
        current_question = {}
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
                if current_question:
                    questions.append(current_question)
                current_question = {"question": line, "trending_score": 8}
            elif "Why trending:" in line:
                current_question["reason"] = line.split(":", 1)[1].strip()
            elif "Companies:" in line:
                current_question["companies"] = line.split(":", 1)[1].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate frequency analysis content based on the content type."""
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