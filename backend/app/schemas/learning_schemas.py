"""
Pydantic schemas for learning recommendations.
Based on the structure used in learning_recommendations.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class QuickWin(BaseModel):
    """Quick action for immediate impact"""
    action: str = Field(description="Specific action to take")
    time: str = Field(description="Hours or days required")
    impact: str = Field(description="Score impact (e.g., '+5%')")
    details: List[str] = Field(description="Specific steps")


class Course(BaseModel):
    """Learning course recommendation"""
    name: str = Field(description="Course name")
    platform: str = Field(description="Platform (Coursera, Udemy, etc.)")
    duration: str = Field(description="Duration in hours")
    cost: str = Field(description="Cost (FREE or $amount)")
    url: Optional[str] = Field(None, description="Course URL if available")
    impact: str = Field(description="Score impact (e.g., '+X%')")
    topics: List[str] = Field(description="Key topics covered")


class Project(BaseModel):
    """Hands-on project recommendation"""
    name: str = Field(description="Project name")
    description: str = Field(description="What to build")
    time: str = Field(description="Time required in hours")
    impact: str = Field(description="Score impact (e.g., '+X%')")
    features: List[str] = Field(description="Specific features to implement")
    technologies: List[str] = Field(description="Tech stack to use")


class PriorityArea(BaseModel):
    """Priority learning area"""
    priority: int = Field(description="Priority rank (1, 2, 3...)")
    skill: str = Field(description="Skill name")
    currentLevel: str = Field(alias="current_level", description="Current level")
    targetLevel: str = Field(alias="target_level", description="Target level")
    impact: str = Field(description="Score impact (e.g., '+15%')")
    time: str = Field(description="Time required (e.g., '40-50 hours')")
    whyImportant: str = Field(alias="why_important", description="Why this matters for the role")
    courses: List[Course] = Field(description="Recommended courses")
    projects: List[Project] = Field(description="Hands-on projects")

    class Config:
        populate_by_name = True


class WeeklyPlan(BaseModel):
    """Weekly roadmap entry"""
    week: str = Field(description="Week range (e.g., '1-2')")
    focus: str = Field(description="Main focus area")
    tasks: List[str] = Field(description="Specific tasks")
    hours: str = Field(description="Estimated hours")
    scoreAfter: int = Field(alias="score_after", description="Expected score after this week")
    deliverables: List[str] = Field(description="What should be completed")

    class Config:
        populate_by_name = True


class TotalInvestment(BaseModel):
    """Total investment analysis"""
    time: str = Field(description="Total hours required")
    cost: str = Field(description="Total cost")
    scoreImprovement: str = Field(alias="score_improvement", description="Score improvement (e.g., '+20%')")
    timeline: str = Field(description="Timeline (e.g., '10 weeks')")
    roiAnalysis: str = Field(alias="roi_analysis", description="Time vs career impact analysis")

    class Config:
        populate_by_name = True


class Resources(BaseModel):
    """Additional resources"""
    freePlatforms: List[str] = Field(alias="free_platforms", description="Free learning platforms")
    communities: List[str] = Field(description="Relevant communities to join")
    certifications: List[str] = Field(description="Valuable certifications")

    class Config:
        populate_by_name = True


class LearningPath(BaseModel):
    """Complete learning path for bridging skill gaps"""
    currentScore: int = Field(alias="current_score", description="Current compatibility score")
    targetScore: int = Field(alias="target_score", description="Target score after learning")
    quickWins: List[QuickWin] = Field(alias="quick_wins", description="Quick wins (1-2 weeks)")
    priorityAreas: List[PriorityArea] = Field(alias="priority_areas", description="Priority learning areas")
    weeklyRoadmap: List[WeeklyPlan] = Field(alias="weekly_roadmap", description="10-week roadmap")
    totalInvestment: TotalInvestment = Field(alias="total_investment", description="Total investment analysis")
    resources: Resources = Field(description="Additional resources")

    class Config:
        populate_by_name = True
