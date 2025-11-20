"""
Pydantic schemas for AI service outputs.
These schemas provide type safety and automatic validation for LLM responses.
"""

from .cv_schemas import (
    CVData, PersonalInfo, Employment, Education, Project, Skill,
    SocialLink, Course, Publication, Reference, Internship, Award,
    Volunteering, CustomSections, Language, Certification
)
from .jd_schemas import JDData, HardSkillRequired, DomainExpertise
from .scorer_schemas import ScorerOutput, GapAnalysis, ScoreBreakdown, CategoryScore
from .question_schemas import QuestionsList, Question
from .cover_letter_schemas import CoverLetterData
from .learning_schemas import LearningPath, QuickWin, Course as LearningCourse, Project as LearningProject, PriorityArea
from .interview_schemas import InterviewPrep, InterviewQuestion, BehavioralQuestion

__all__ = [
    # CV schemas
    "CVData",
    "PersonalInfo",
    "Employment",
    "Education",
    "Project",
    "Skill",
    # JD schemas
    "JDData",
    "HardSkillRequired",
    "DomainExpertise",
    # Scorer schemas
    "ScorerOutput",
    "GapAnalysis",
    "ScoreBreakdown",
    "CategoryScore",
    # Question schemas
    "QuestionsList",
    "Question",
    # Cover letter schemas
    "CoverLetterData",
    # Learning schemas
    "LearningPath",
    "QuickWin",
    "LearningCourse",
    "LearningProject",
    "PriorityArea",
    # Interview schemas
    "InterviewPrep",
    "InterviewQuestion",
    "BehavioralQuestion",
]
