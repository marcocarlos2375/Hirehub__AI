"""
Pydantic schemas for smart question generation.
Based on the structure used in question_gen.py
"""

from pydantic import BaseModel, Field
from typing import List


class Question(BaseModel):
    """Single smart question to uncover hidden experience"""
    question: str = Field(description="The actual question to ask the candidate")
    category: str = Field(description="Category: technical/domain/experience/soft_skills")
    priority: str = Field(description="Priority level: critical/high/medium/low")
    potentialImpact: str = Field(
        alias="potential_impact",
        description="Potential score impact if answered positively (e.g., '+10% score')"
    )
    whyAsking: str = Field(
        alias="why_asking",
        description="Explanation of what gap this question addresses"
    )
    suggestedAnswers: List[str] = Field(
        alias="suggested_answers",
        default_factory=list,
        description="3-4 pre-written answer options for user to select from"
    )

    class Config:
        populate_by_name = True  # Allow both camelCase and snake_case


class QuestionsList(BaseModel):
    """List of smart questions"""
    questions: List[Question] = Field(description="List of 5-8 smart questions")

    class Config:
        json_schema_extra = {
            "example": {
                "questions": [
                    {
                        "question": "Have you worked with Kubernetes or container orchestration in production environments?",
                        "category": "technical",
                        "priority": "critical",
                        "potential_impact": "+12% if yes",
                        "why_asking": "JD requires Kubernetes experience which wasn't found in CV",
                        "suggested_answers": [
                            "Yes, I've deployed and managed Kubernetes clusters in production for 2+ years",
                            "I have basic Kubernetes experience through personal projects and learning",
                            "No direct Kubernetes experience, but I've used Docker extensively",
                            "No experience with Kubernetes yet"
                        ]
                    }
                ]
            }
        }
