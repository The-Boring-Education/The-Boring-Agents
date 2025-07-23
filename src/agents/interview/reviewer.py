"""Reviewer Agent - Reviews and validates interview content quality."""

from typing import Dict, List, Any, Optional
from langchain.prompts import PromptTemplate

from ...core.base_agent import BaseAgent


class Reviewer(BaseAgent):
    """Agent for reviewing and validating interview content quality."""
    
    def __init__(self, **kwargs):
        """Initialize the reviewer with lower temperature for consistent review."""
        super().__init__(temperature=0.3, **kwargs)  # Lower temperature for consistent review
    
    def _get_prompt_templates(self) -> Dict[str, PromptTemplate]:
        """Get prompt templates for content review."""
        
        review_qa_pair_template = PromptTemplate(
            input_variables=["question", "answer", "topic"],
            template="""
You are a senior tech interviewer and content quality reviewer with 20+ years of experience.

**Question:** {question}
**Answer:** {answer}
**Topic:** {topic}

Review this Q&A pair and provide:

## Quality Assessment

**Overall Score (1-10):** [Score]
**Strengths:**
- [List 3-5 strengths]

**Areas for Improvement:**
- [List 2-3 areas that need improvement]

## Content Analysis

**Technical Accuracy:** [High/Medium/Low]
**Completeness:** [High/Medium/Low]
**Clarity:** [High/Medium/Low]
**Practical Relevance:** [High/Medium/Low]

## Specific Feedback

**What works well:**
- [Specific points about what's good]

**What needs improvement:**
- [Specific suggestions for improvement]

**Missing elements:**
- [List any missing important elements]

## Recommendations

**Immediate fixes:**
1. [First recommendation]
2. [Second recommendation]

**Enhancement suggestions:**
1. [First enhancement]
2. [Second enhancement]

## Final Verdict

**Publish Ready:** [Yes/No/With Modifications]
**Priority Level:** [High/Medium/Low]
"""
        )
        
        review_sheet_template = PromptTemplate(
            input_variables=["sheet_name", "question_count", "topic"],
            template="""
You are a senior content quality reviewer for interview preparation materials.

**Sheet Name:** {sheet_name}
**Question Count:** {question_count}
**Topic:** {topic}

Review this interview sheet and provide:

## Overall Assessment

**Quality Score (1-10):** [Score]
**Completeness:** [High/Medium/Low]
**Difficulty Distribution:** [Appropriate/Needs Adjustment]
**Topic Coverage:** [Comprehensive/Partial/Incomplete]

## Content Analysis

**Question Quality:**
- [Assessment of question quality]

**Answer Quality:**
- [Assessment of answer quality]

**Difficulty Balance:**
- [Assessment of difficulty distribution]

**Practical Relevance:**
- [Assessment of real-world relevance]

## Recommendations

**Immediate Actions:**
1. [First action needed]
2. [Second action needed]

**Quality Improvements:**
1. [First improvement]
2. [Second improvement]

**Content Gaps:**
- [List any missing important topics]

## Final Recommendation

**Ready for Publication:** [Yes/No/With Modifications]
**Priority Level:** [High/Medium/Low]
**Estimated Review Time:** [Time estimate]
"""
        )
        
        return {
            "review_qa_pair": review_qa_pair_template,
            "review_sheet": review_sheet_template
        }
    
    def generate_content(self, content_type: str, **kwargs) -> Dict[str, Any]:
        """Generate content based on type."""
        if content_type == "review_qa_pair":
            return self.review_qa_pair(
                question=kwargs.get("question"),
                answer=kwargs.get("answer"),
                topic=kwargs.get("topic")
            )
        elif content_type == "review_sheet":
            return self.review_sheet(
                sheet_name=kwargs.get("sheet_name"),
                question_count=kwargs.get("question_count"),
                topic=kwargs.get("topic")
            )
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    def review_qa_pair(self, question: str, answer: str, topic: str) -> Dict[str, Any]:
        """Review a single Q&A pair."""
        self.logger.info(f"Reviewing Q&A pair for topic: {topic}")
        
        prompt = self._format_prompt("review_qa_pair",
                                   question=question,
                                   answer=answer,
                                   topic=topic)
        
        review_result = self._generate_with_prompt(prompt)
        
        # Parse review result
        parsed_review = self._parse_review_result(review_result)
        
        return {
            "status": "success",
            "review": parsed_review,
            "raw_review": review_result
        }
    
    def review_sheet(self, sheet_name: str, question_count: int, topic: str) -> Dict[str, Any]:
        """Review a complete interview sheet."""
        self.logger.info(f"Reviewing sheet: {sheet_name}")
        
        prompt = self._format_prompt("review_sheet",
                                   sheet_name=sheet_name,
                                   question_count=question_count,
                                   topic=topic)
        
        review_result = self._generate_with_prompt(prompt)
        
        # Parse review result
        parsed_review = self._parse_sheet_review(review_result)
        
        return {
            "status": "success",
            "review": parsed_review,
            "raw_review": review_result
        }
    
    def suggest_improvements(self, content: str, review_feedback: List[str]) -> List[str]:
        """Suggest specific improvements based on review feedback."""
        improvement_prompt = f"""
Based on the following review feedback, suggest specific improvements:

Review Feedback:
{chr(10).join(review_feedback)}

Content:
{content}

Provide 3-5 specific, actionable improvements:
"""
        
        improvement_result = self._generate_with_prompt(improvement_prompt)
        
        # Parse improvements
        improvements = []
        lines = improvement_result.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('1.') or line.startswith('2.') or line.startswith('3.')):
                improvement = line.lstrip('-•123456789. ').strip()
                if improvement:
                    improvements.append(improvement)
        
        return improvements
    
    def _parse_review_result(self, review_text: str) -> Dict[str, Any]:
        """Parse review result into structured format."""
        review = {
            "overall_score": 0,
            "strengths": [],
            "improvements": [],
            "technical_accuracy": "Medium",
            "completeness": "Medium",
            "clarity": "Medium",
            "practical_relevance": "Medium",
            "publish_ready": "No",
            "priority_level": "Medium"
        }
        
        lines = review_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            if "Overall Score" in line:
                try:
                    score_text = line.split(':')[1].strip()
                    score = int(score_text.split()[0])
                    review["overall_score"] = score
                except:
                    pass
            
            elif "Strengths:" in line:
                current_section = "strengths"
            elif "Areas for Improvement:" in line:
                current_section = "improvements"
            elif "Technical Accuracy:" in line:
                review["technical_accuracy"] = line.split(':')[1].strip()
            elif "Completeness:" in line:
                review["completeness"] = line.split(':')[1].strip()
            elif "Clarity:" in line:
                review["clarity"] = line.split(':')[1].strip()
            elif "Practical Relevance:" in line:
                review["practical_relevance"] = line.split(':')[1].strip()
            elif "Publish Ready:" in line:
                review["publish_ready"] = line.split(':')[1].strip()
            elif "Priority Level:" in line:
                review["priority_level"] = line.split(':')[1].strip()
            
            elif line.startswith('-') and current_section:
                item = line.lstrip('- ').strip()
                if item:
                    review[current_section].append(item)
        
        return review
    
    def _parse_sheet_review(self, review_text: str) -> Dict[str, Any]:
        """Parse sheet review result into structured format."""
        review = {
            "quality_score": 0,
            "completeness": "Medium",
            "difficulty_distribution": "Appropriate",
            "topic_coverage": "Comprehensive",
            "ready_for_publication": "No",
            "priority_level": "Medium",
            "estimated_review_time": "Unknown"
        }
        
        lines = review_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if "Quality Score" in line:
                try:
                    score_text = line.split(':')[1].strip()
                    score = int(score_text.split()[0])
                    review["quality_score"] = score
                except:
                    pass
            
            elif "Completeness:" in line:
                review["completeness"] = line.split(':')[1].strip()
            elif "Difficulty Distribution:" in line:
                review["difficulty_distribution"] = line.split(':')[1].strip()
            elif "Topic Coverage:" in line:
                review["topic_coverage"] = line.split(':')[1].strip()
            elif "Ready for Publication:" in line:
                review["ready_for_publication"] = line.split(':')[1].strip()
            elif "Priority Level:" in line:
                review["priority_level"] = line.split(':')[1].strip()
            elif "Estimated Review Time:" in line:
                review["estimated_review_time"] = line.split(':')[1].strip()
        
        return review 