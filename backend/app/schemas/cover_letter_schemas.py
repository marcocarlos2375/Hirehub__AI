"""
Pydantic schemas for cover letter generation.
Based on the structure used in cover_letter_gen.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PersonalInfo(BaseModel):
    """Personal information for cover letter"""
    name: str = Field(description="Full name")
    email: str = Field(description="Email address")
    phone: str = Field(description="Phone number")
    location: str = Field(description="Location/city")


class CompanyInfo(BaseModel):
    """Company information for cover letter"""
    hiringTeam: str = Field(alias="hiring_team", description="Hiring team or specific name")
    companyName: str = Field(alias="company_name", description="Company name")
    companyLocation: str = Field(alias="company_location", description="Company location")

    class Config:
        populate_by_name = True


class CoverLetterContent(BaseModel):
    """Content sections of cover letter"""
    opening: str = Field(description="Engaging opening paragraph showing excitement")
    whyCompany: str = Field(alias="why_company", description="Specific reasons excited about THIS company")
    whatBrings: List[str] = Field(alias="what_brings", description="3-4 key strengths with evidence")
    addressingConcerns: str = Field(alias="addressing_concerns", description="Proactively address logistics/gaps")
    seeking: str = Field(description="What candidate wants in next role and why this fits")
    closing: str = Field(description="Strong closing inviting conversation")
    ps: Optional[str] = Field(None, description="Optional interesting hook or additional detail")

    class Config:
        populate_by_name = True


class CoverLetterData(BaseModel):
    """Complete cover letter structure"""
    personalInfo: PersonalInfo = Field(alias="personal_info", description="Candidate's personal info")
    date: str = Field(description="Date string (e.g., 'December 15, 2024')")
    companyInfo: CompanyInfo = Field(alias="company_info", description="Company information")
    positionTitle: str = Field(alias="position_title", description="Position being applied for")
    content: CoverLetterContent = Field(description="Cover letter content sections")
    fullText: str = Field(alias="full_text", description="Complete formatted cover letter")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "personal_info": {
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1 (555) 123-4567",
                    "location": "San Francisco, CA"
                },
                "date": "December 15, 2024",
                "company_info": {
                    "hiring_team": "Hiring Team",
                    "company_name": "TechCorp Inc",
                    "company_location": "San Francisco, CA"
                },
                "position_title": "Senior Python Developer",
                "content": {
                    "opening": "I am writing to express my strong interest...",
                    "why_company": "TechCorp's commitment to innovation...",
                    "what_brings": [
                        "8+ years of Python development experience...",
                        "Led migration to microservices architecture...",
                        "Strong background in team leadership..."
                    ],
                    "addressing_concerns": "I am available to start immediately...",
                    "seeking": "I am looking for a role where...",
                    "closing": "I would welcome the opportunity to discuss...",
                    "ps": "P.S. I noticed TechCorp recently launched..."
                },
                "full_text": "John Doe\n555-123-4567\njohn@example.com\n\nDecember 15, 2024\n\n..."
            }
        }
