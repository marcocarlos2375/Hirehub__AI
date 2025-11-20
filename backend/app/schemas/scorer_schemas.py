"""
Pydantic schemas for scorer output.
Based on the structure used in scorer.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class GapAnalysis(BaseModel):
    """Single gap identified in CV vs JD comparison"""
    gap: str = Field(description="Description of what's missing")
    priority: str = Field(description="Priority level: critical/high/medium/low")
    impact: str = Field(description="Potential impact if addressed (e.g., '+15% score')")


class CategoryScore(BaseModel):
    """Score for a specific category"""
    score: int = Field(description="Score out of 100 for this category")
    weight: int = Field(description="Weight percentage of this category in overall score")
    matched: List[str] = Field(default_factory=list, description="Matched items")
    missing: List[str] = Field(default_factory=list, description="Missing items")
    assessment: Optional[str] = Field(None, description="Qualitative assessment")
    candidateYears: Optional[int] = Field(None, description="Candidate years (for experience category)")
    requiredYears: Optional[int] = Field(None, description="Required years (for experience category)")


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of compatibility score"""
    hardSkills: CategoryScore = Field(alias="hard_skills", description="Hard skills match")
    softSkills: CategoryScore = Field(alias="soft_skills", description="Soft skills match")
    experience: CategoryScore = Field(description="Experience level match")
    domain: CategoryScore = Field(description="Domain expertise match")
    portfolio: CategoryScore = Field(description="Portfolio/projects match")
    logistics: CategoryScore = Field(description="Logistics (location, availability) match")

    class Config:
        populate_by_name = True  # Allow both camelCase and snake_case


class ScorerAnalysis(BaseModel):
    """AI-generated qualitative analysis (used with vector scores)"""
    topGaps: List[GapAnalysis] = Field(alias="top_gaps", default_factory=list, description="Top 5-8 gaps to address")
    strengths: List[str] = Field(default_factory=list, description="Candidate's key strengths for this role")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")

    class Config:
        populate_by_name = True


class ScorerOutput(BaseModel):
    """Complete scorer output structure"""
    overallScore: int = Field(alias="overall_score", description="Overall compatibility score (0-100)")
    breakdown: ScoreBreakdown = Field(description="Detailed category breakdown")
    topGaps: List[GapAnalysis] = Field(alias="top_gaps", default_factory=list, description="Top 5-8 gaps to address")
    strengths: List[str] = Field(default_factory=list, description="Candidate's key strengths for this role")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "overall_score": 72,
                "breakdown": {
                    "hard_skills": {
                        "score": 80,
                        "weight": 35,
                        "matched": ["Python", "Django", "PostgreSQL"],
                        "missing": ["Kubernetes", "AWS"]
                    },
                    "experience": {
                        "score": 70,
                        "weight": 20,
                        "candidate_years": 5,
                        "required_years": 7,
                        "assessment": "Good foundation but slightly below target"
                    }
                },
                "top_gaps": [
                    {
                        "gap": "No Kubernetes experience mentioned",
                        "priority": "critical",
                        "impact": "+12% if added"
                    }
                ],
                "strengths": [
                    "Strong Python and Django expertise",
                    "Proven track record in scalable systems"
                ]
            }
        }
