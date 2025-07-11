"""Quality Review Agent for ensuring high-quality interview content."""

from typing import Dict, Any, List, Optional
from ...core.base_agent import BaseAgent


class QualityReviewAgent(BaseAgent):
    """Agent for reviewing and ensuring quality of interview sheets and answers."""
    
    def _get_prompt_templates(self) -> Dict[str, Any]:
        """Return empty dict since we'll use direct prompts."""
        return {}
    
    def generate_content(self, **kwargs) -> Dict[str, Any]:
        """Generate quality review content."""
        return {"generated_content": "Quality review completed"}
    
    def review_qa_pair(self, question: str, answer: str, sheet_name: str) -> Dict[str, Any]:
        """Review a question-answer pair for quality.
        
        Args:
            question: Interview question
            answer: Answer content
            sheet_name: Name of the interview sheet
            
        Returns:
            Quality review with score and suggestions
        """
        review_prompt = f"""
        You are a senior interview content reviewer ensuring world-class quality for ₹49 premium sheets.
        
        **Sheet Topic:** {sheet_name}
        **Question:** {question}
        **Answer Length:** {len(answer)} characters
        
        **Answer Content:** {answer[:1000]}{'...' if len(answer) > 1000 else ''}
        
        Review this Q&A pair against these criteria:
        
        ## Technical Accuracy (1-10)
        - Is the information correct and up-to-date?
        - Are there any technical errors?
        - Is the depth appropriate for the question?
        
        ## Indian Context Integration (1-10)
        - Does it use relevant Indian company examples?
        - Are cultural references appropriate and helpful?
        - Is it relatable to Indian students?
        
        ## Engagement & Humor (1-10)
        - Is it engaging and fun to read?
        - Are analogies helpful and memorable?
        - Does it maintain professional tone while being entertaining?
        
        ## Career Relevance (1-10)
        - Does it help with actual interview preparation?
        - Are salary/company insights accurate?
        - Will this knowledge help in getting jobs?
        
        ## Learning Experience (1-10)
        - Is it easy to understand?
        - Does it build from basics to advanced?
        - Are examples clear and helpful?
        
        **Overall Score:** (1-10)
        **Key Strengths:** (3-4 bullet points)
        **Areas for Improvement:** (3-4 specific suggestions)
        **Worth ₹49?** (Yes/No with reasoning)
        
        Be constructive but maintain high standards for premium content.
        """
        
        try:
            response = self._generate_with_prompt(review_prompt)
            return self._parse_quality_review(response, question, answer)
        except Exception as e:
            self.logger.error(f"Error reviewing Q&A pair: {str(e)}")
            return self._fallback_quality_review(question, answer)
    
    def review_complete_sheet(self, sheet_name: str, qa_pairs: List[Dict[str, Any]], 
                            research_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Review a complete interview sheet for quality.
        
        Args:
            sheet_name: Name of the sheet
            qa_pairs: List of question-answer pairs
            research_insights: Research insights used
            
        Returns:
            Complete sheet quality review
        """
        qa_summary = f"Total Q&A Pairs: {len(qa_pairs)}"
        if qa_pairs:
            avg_answer_length = sum(len(qa.get('answer', '')) for qa in qa_pairs) / len(qa_pairs)
            qa_summary += f"\nAverage Answer Length: {avg_answer_length:.0f} characters"
            
            # Sample questions for review
            sample_questions = [qa.get('question', '') for qa in qa_pairs[:5]]
            qa_summary += f"\nSample Questions:\n" + "\n".join([f"- {q}" for q in sample_questions])
        
        sheet_review_prompt = f"""
        Review the complete interview sheet "{sheet_name}" for world-class quality.
        
        **Sheet Overview:**
        {qa_summary}
        
        **Research Context:** {research_insights.get('key_recommendations', ['Standard research insights']) if research_insights else ['No research provided']}
        
        Evaluate the entire sheet:
        
        ## Content Completeness (1-10)
        - Does it cover all essential topics?
        - Is the question distribution appropriate?
        - Are difficulty levels well-balanced?
        
        ## Quality Consistency (1-10)
        - Are all answers of similar high quality?
        - Is the tone consistent throughout?
        - Are Indian context examples well-distributed?
        
        ## Market Relevance (1-10)
        - Are questions current and relevant?
        - Do they reflect actual interview patterns?
        - Will this help students get jobs in 2024-2025?
        
        ## Value Proposition (1-10)
        - Is this worth ₹49 for Indian students?
        - Does it offer unique value vs free resources?
        - Would students recommend this to friends?
        
        ## Overall Assessment
        **Sheet Score:** (1-10)
        **Top 3 Strengths:**
        **Top 3 Improvement Areas:**
        **Recommendation:** (Publish/Revise/Major Overhaul)
        **Student Success Probability:** (What % of students will ace interviews with this?)
        
        Be honest and maintain premium quality standards.
        """
        
        try:
            response = self._generate_with_prompt(sheet_review_prompt)
            return self._parse_sheet_review(response, sheet_name, len(qa_pairs))
        except Exception as e:
            self.logger.error(f"Error reviewing complete sheet: {str(e)}")
            return self._fallback_sheet_review(sheet_name, len(qa_pairs))
    
    def suggest_improvements(self, content: str, review_feedback: List[str]) -> List[str]:
        """Suggest specific improvements based on review feedback.
        
        Args:
            content: Content to improve
            review_feedback: Feedback from quality review
            
        Returns:
            List of specific improvement suggestions
        """
        improvement_prompt = f"""
        Based on this feedback, suggest specific actionable improvements:
        
        **Content Length:** {len(content)} characters
        **Feedback:**
        {chr(10).join(['- ' + feedback for feedback in review_feedback])}
        
        **Content Sample:** {content[:500]}...
        
        Provide 5-7 specific, actionable improvements:
        1. Technical accuracy fixes
        2. Indian context enhancements
        3. Engagement improvements
        4. Career relevance additions
        5. Learning experience enhancements
        
        Be specific and practical.
        """
        
        try:
            response = self._generate_with_prompt(improvement_prompt)
            return self._parse_improvement_suggestions(response)
        except Exception as e:
            self.logger.error(f"Error generating improvements: {str(e)}")
            return ["Review content for technical accuracy", "Add more Indian company examples", "Improve engagement with analogies"]
    
    def _parse_quality_review(self, response: str, question: str, answer: str) -> Dict[str, Any]:
        """Parse quality review response."""
        review = {
            "question": question,
            "answer_length": len(answer),
            "technical_accuracy": 7,
            "indian_context": 6,
            "engagement": 6,
            "career_relevance": 7,
            "learning_experience": 7,
            "overall_score": 6.6,
            "strengths": [],
            "improvements": [],
            "worth_price": True,
            "raw_review": response
        }
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            
            # Extract scores
            if "Technical Accuracy" in line and any(char.isdigit() for char in line):
                score = self._extract_score(line)
                if score:
                    review["technical_accuracy"] = score
            elif "Indian Context" in line and any(char.isdigit() for char in line):
                score = self._extract_score(line)
                if score:
                    review["indian_context"] = score
            elif "Engagement" in line and any(char.isdigit() for char in line):
                score = self._extract_score(line)
                if score:
                    review["engagement"] = score
            elif "Career Relevance" in line and any(char.isdigit() for char in line):
                score = self._extract_score(line)
                if score:
                    review["career_relevance"] = score
            elif "Learning Experience" in line and any(char.isdigit() for char in line):
                score = self._extract_score(line)
                if score:
                    review["learning_experience"] = score
            elif "Overall Score" in line and any(char.isdigit() for char in line):
                score = self._extract_score(line)
                if score:
                    review["overall_score"] = score
            
            # Extract improvements
            elif "improvement" in line.lower() and len(line) > 20:
                review["improvements"].append(line)
            elif "strength" in line.lower() and len(line) > 20:
                review["strengths"].append(line)
            elif "Worth ₹49" in line:
                review["worth_price"] = "Yes" in line
        
        return review
    
    def _parse_sheet_review(self, response: str, sheet_name: str, qa_count: int) -> Dict[str, Any]:
        """Parse complete sheet review response."""
        review = {
            "sheet_name": sheet_name,
            "qa_count": qa_count,
            "content_completeness": 7,
            "quality_consistency": 7,
            "market_relevance": 7,
            "value_proposition": 7,
            "overall_score": 7.0,
            "strengths": [],
            "improvements": [],
            "recommendation": "Revise",
            "success_probability": "70%",
            "raw_review": response
        }
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            
            # Extract scores
            if "Content Completeness" in line:
                score = self._extract_score(line)
                if score:
                    review["content_completeness"] = score
            elif "Quality Consistency" in line:
                score = self._extract_score(line)
                if score:
                    review["quality_consistency"] = score
            elif "Market Relevance" in line:
                score = self._extract_score(line)
                if score:
                    review["market_relevance"] = score
            elif "Value Proposition" in line:
                score = self._extract_score(line)
                if score:
                    review["value_proposition"] = score
            elif "Sheet Score" in line or "Overall" in line:
                score = self._extract_score(line)
                if score:
                    review["overall_score"] = score
            
            # Extract other information
            elif "Recommendation:" in line:
                rec = line.split(":", 1)[1].strip()
                if rec in ["Publish", "Revise", "Major Overhaul"]:
                    review["recommendation"] = rec
            elif "Success Probability" in line:
                if "%" in line:
                    review["success_probability"] = line.split(":", 1)[1].strip()
        
        return review
    
    def _parse_improvement_suggestions(self, response: str) -> List[str]:
        """Parse improvement suggestions from response."""
        suggestions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')) or 
                        line.startswith('-') or 
                        len(line) > 30):
                # Clean up the suggestion
                suggestion = line.lstrip('0123456789.- ').strip()
                if len(suggestion) > 15:  # Meaningful suggestions
                    suggestions.append(suggestion)
        
        return suggestions[:7]  # Top 7 suggestions
    
    def _extract_score(self, line: str) -> Optional[float]:
        """Extract numeric score from a line."""
        import re
        # Look for patterns like "8/10", "8.5", "(8)", etc.
        patterns = [
            r'(\d+\.?\d*)/10',
            r'(\d+\.?\d*)/10',
            r'\((\d+\.?\d*)\)',
            r':?\s*(\d+\.?\d*)\s*$',
            r'Score:\s*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                try:
                    score = float(match.group(1))
                    if 0 <= score <= 10:
                        return score
                except ValueError:
                    continue
        
        return None
    
    def _fallback_quality_review(self, question: str, answer: str) -> Dict[str, Any]:
        """Provide fallback quality review if AI fails."""
        return {
            "question": question,
            "answer_length": len(answer),
            "technical_accuracy": 7,
            "indian_context": 6,
            "engagement": 6,
            "career_relevance": 7,
            "learning_experience": 7,
            "overall_score": 6.6,
            "strengths": ["Covers basic concepts", "Provides practical information"],
            "improvements": ["Add more Indian examples", "Include humor and analogies", "Provide career insights"],
            "worth_price": True,
            "raw_review": "Fallback review due to AI processing error"
        }
    
    def _fallback_sheet_review(self, sheet_name: str, qa_count: int) -> Dict[str, Any]:
        """Provide fallback sheet review if AI fails."""
        return {
            "sheet_name": sheet_name,
            "qa_count": qa_count,
            "content_completeness": 7,
            "quality_consistency": 7,
            "market_relevance": 7,
            "value_proposition": 7,
            "overall_score": 7.0,
            "strengths": ["Comprehensive coverage", "Good question count"],
            "improvements": ["Enhance Indian context", "Improve engagement", "Add career guidance"],
            "recommendation": "Revise",
            "success_probability": "70%",
            "raw_review": "Fallback review due to AI processing error"
        }