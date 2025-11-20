"""
Pydantic schemas for Job Description analysis output.
Based on the structure used in jd_analyzer.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class HardSkillRequired(BaseModel):
    """Single hard skill requirement"""
    skill: str = Field(description="Skill name")
    priority: str = Field(description="Priority level: critical/important/nice")
    yearsRequired: Optional[int] = Field(None, description="Years of experience required for this skill")


class DomainExpertise(BaseModel):
    """Domain expertise requirements"""
    industry: Optional[str] = Field(None, description="Industry sector")
    specificKnowledge: List[str] = Field(default_factory=list, description="Specific domain knowledge areas")


class JDData(BaseModel):
    """Complete Job Description data structure matching jd_analyzer.py output"""
    companyName: Optional[str] = Field(None, description="Company name")
    positionTitle: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Job location")
    workMode: Optional[str] = Field(None, description="Work mode: remote/hybrid/onsite")
    salaryRange: Optional[str] = Field(None, description="Salary range if mentioned")
    experienceYearsRequired: int = Field(0, description="Years of experience required")
    experienceLevel: str = Field("mid", description="Experience level: junior/mid/senior/lead")

    hardSkillsRequired: List[HardSkillRequired] = Field(
        default_factory=list,
        description="Required hard skills with priority"
    )
    softSkillsRequired: List[str] = Field(
        default_factory=list,
        description="Required soft skills"
    )
    responsibilities: List[str] = Field(
        default_factory=list,
        description="Key job responsibilities"
    )
    techStack: List[str] = Field(
        default_factory=list,
        description="Technology stack mentioned"
    )
    domainExpertise: DomainExpertise = Field(
        default_factory=DomainExpertise,
        description="Domain expertise requirements"
    )
    implicitRequirements: List[str] = Field(
        default_factory=list,
        description="Requirements not explicitly stated but implied"
    )
    companyCultureSignals: List[str] = Field(
        default_factory=list,
        description="Company culture indicators from the JD"
    )
    atsKeywords: List[str] = Field(
        default_factory=list,
        description="Important keywords for ATS systems"
    )
    benefits: List[str] = Field(
        default_factory=list,
        description="Mentioned benefits and perks"
    )
    teamSize: Optional[str] = Field(None, description="Team size if mentioned")
    reportingTo: Optional[str] = Field(None, description="Reporting structure")

    class Config:
        json_schema_extra = {
            "example": {
                "companyName": "TechCorp Inc",
                "positionTitle": "Senior Python Developer",
                "location": "San Francisco, CA",
                "workMode": "hybrid",
                "experienceYearsRequired": 5,
                "experienceLevel": "senior",
                "hardSkillsRequired": [
                    {"skill": "Python", "priority": "critical", "yearsRequired": 5},
                    {"skill": "Django", "priority": "important", "yearsRequired": 3}
                ],
                "responsibilities": [
                    "Design and implement scalable backend services",
                    "Mentor junior developers"
                ],
                "atsKeywords": ["Python", "Django", "REST API", "PostgreSQL"]
            }
        }
