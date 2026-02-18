from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Resource(BaseModel):
    """Resource model for learning materials."""
    type: Literal['YOUTUBE', 'ARTICLE', 'CODE', 'LEETCODE', 'BLOG'] = Field(description="Type of resource")
    url: str = Field(description="URL of the resource")
    label: Optional[str] = Field(None, description="Label or title for the resource")

class InterviewQuestionResponse(BaseModel):
    """Structured response for an interview question."""
    answer: str = Field(description="The COMPLETE, LONG-FORM answer in markdown format. Must be 800-1500 words minimum. Include ALL sections: Quick Answer, Introduction, detailed explanation with examples, code snippets (if applicable), interview tips, and practice problems. Use markdown headings (##### ), bullet points, bold text, and code blocks for formatting. This single field holds the ENTIRE structured response — do NOT summarize.")

    code_example: Optional[str] = Field(None, description="Code example if applicable (markdown formatted)")
    resources: List[Resource] = Field(default_factory=list, description="List of learning resources")
    company_types: List[str] = Field(default_factory=list, description="Types of companies that ask this question")
    difficulty: str = Field(description="Difficulty level (Easy, Medium, Hard)")
    frequency: str = Field(description="How often this question is asked")
    priority: str = Field(description="Priority of this question")
    followup_questions: List[str] = Field(default_factory=list, description="Potential follow-up questions")
