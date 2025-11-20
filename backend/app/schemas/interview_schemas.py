"""
Pydantic schemas for interview preparation.
Based on the structure used in interview_prep.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class InterviewQuestion(BaseModel):
    """Single technical/domain interview question"""
    question: str = Field(description="The interview question")
    category: str = Field(description="Category: technical/system_design/domain/problem_solving")
    difficulty: str = Field(description="Difficulty: easy/medium/hard")
    suggestedAnswer: str = Field(
        alias="suggested_answer",
        description="Sample answer demonstrating key points"
    )
    keyPoints: List[str] = Field(
        alias="key_points",
        description="Key points to cover in the answer"
    )
    whyThisQuestion: str = Field(
        alias="why_this_question",
        description="Why this question is likely to be asked based on JD"
    )

    class Config:
        populate_by_name = True


class BehavioralQuestion(BaseModel):
    """Behavioral/STAR interview question"""
    question: str = Field(description="The behavioral question")
    category: str = Field(description="Category: leadership/conflict/failure/success/teamwork")
    starExample: dict = Field(
        alias="star_example",
        description="STAR format example (Situation, Task, Action, Result)"
    )
    tipsForAnswering: List[str] = Field(
        alias="tips_for_answering",
        description="Tips for crafting a strong response"
    )

    class Config:
        populate_by_name = True


class InterviewPrep(BaseModel):
    """Complete interview preparation package"""
    technicalQuestions: List[InterviewQuestion] = Field(
        alias="technical_questions",
        description="5-10 likely technical questions"
    )

    behavioralQuestions: List[BehavioralQuestion] = Field(
        alias="behavioral_questions",
        description="5-8 behavioral/STAR questions"
    )

    companyResearchTips: List[str] = Field(
        alias="company_research_tips",
        description="What to research about the company"
    )

    questionsToAskInterviewer: List[dict] = Field(
        alias="questions_to_ask_interviewer",
        description="Smart questions to ask the interviewer"
    )

    redFlags: List[str] = Field(
        alias="red_flags",
        description="Potential weak areas to be ready to address"
    )

    preparationChecklist: List[str] = Field(
        alias="preparation_checklist",
        description="Pre-interview preparation checklist"
    )

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "technical_questions": [
                    {
                        "question": "Explain how you would design a microservices architecture for a high-traffic e-commerce platform",
                        "category": "system_design",
                        "difficulty": "hard",
                        "suggested_answer": "I would start by identifying bounded contexts...",
                        "key_points": [
                            "Service decomposition strategy",
                            "Inter-service communication patterns",
                            "Data consistency approaches"
                        ],
                        "why_this_question": "JD emphasizes microservices and scalability"
                    }
                ],
                "behavioral_questions": [
                    {
                        "question": "Tell me about a time you had to make a difficult technical decision with limited information",
                        "category": "decision_making",
                        "star_example": {
                            "situation": "Production system experiencing intermittent failures",
                            "task": "Needed to decide between quick fix or full refactor",
                            "action": "Analyzed metrics, consulted team, chose hybrid approach",
                            "result": "Reduced incidents by 80% within 2 weeks"
                        }
                    }
                ]
            }
        }
