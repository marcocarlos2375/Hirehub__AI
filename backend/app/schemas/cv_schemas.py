"""
Pydantic schemas for CV parsing output.
Based on the structure used in cv_parser.py
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class SocialLink(BaseModel):
    """Social media or portfolio link"""
    type: str = Field(description="Type: linkedin/github/twitter/portfolio/other")
    url: str = Field(description="Full URL")


class PersonalInfo(BaseModel):
    """Personal information section of CV"""
    jobTitle: Optional[str] = Field(None, description="Current or desired job title")
    firstName: Optional[str] = Field(None, description="First name")
    lastName: Optional[str] = Field(None, description="Last name")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    address: Optional[str] = Field(None, description="Physical address")
    website: Optional[str] = Field(None, description="Personal website URL")
    birthDate: Optional[str] = Field(None, description="Date of birth (DD.MM.YYYY)")
    nationality: Optional[str] = Field(None, description="Nationality")
    relationshipStatus: Optional[str] = Field(None, description="Relationship status")
    availability: Optional[str] = Field(None, description="Availability (e.g., '2weeks', 'immediate')")
    socialLinks: List[SocialLink] = Field(default_factory=list, description="Social media and portfolio links")


class Employment(BaseModel):
    """Single employment history entry"""
    position: str = Field(description="Job title/position")
    company: str = Field(description="Company name")
    location: Optional[str] = Field(None, description="Work location")
    startDate: str = Field(description="Start date (YYYY-MM format preferred)")
    endDate: Optional[str] = Field(None, description="End date or empty if current")
    currentlyWorking: bool = Field(False, description="Whether this is current position")
    description: Optional[str] = Field(None, description="Brief job description")
    responsibilities: Optional[List[str]] = Field(default_factory=list, description="Key responsibilities and achievements")


class Education(BaseModel):
    """Single education entry"""
    school: str = Field(description="Institution name")
    degree: str = Field(description="Degree type and field")
    location: Optional[str] = Field(None, description="Institution location")
    startDate: Optional[str] = Field(None, description="Start date (YYYY-MM format)")
    endDate: Optional[str] = Field(None, description="End date (YYYY-MM format)")
    current: bool = Field(False, description="Whether currently enrolled")
    description: Optional[str] = Field(None, description="Additional details (GPA, honors)")


class Project(BaseModel):
    """Project entry"""
    name: str = Field(description="Project name")
    description: str = Field(description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    link: Optional[str] = Field(None, description="Project URL or repository link")
    startDate: Optional[str] = Field(None, description="Start date")
    endDate: Optional[str] = Field(None, description="End date")


class Skill(BaseModel):
    """Individual skill entry"""
    skill: str = Field(description="Skill name")
    level: Optional[str] = Field(None, description="Proficiency level (beginner/intermediate/advanced/expert)")
    category: Optional[str] = Field(None, description="Skill category (technical/soft/language/tool)")


class Language(BaseModel):
    """Language proficiency entry"""
    language: str = Field(description="Language name")
    proficiency: Optional[str] = Field(None, description="Proficiency level")


class Certification(BaseModel):
    """Certification entry"""
    name: str = Field(description="Certification name")
    issuer: Optional[str] = Field(None, description="Issuing organization")
    date: Optional[str] = Field(None, description="Date obtained")
    expiryDate: Optional[str] = Field(None, description="Expiry date if applicable")


class Course(BaseModel):
    """Course or training entry"""
    title: str = Field(description="Course name")
    institution: str = Field(description="Provider/platform")
    completionDate: Optional[str] = Field(None, description="Completion date (YYYY-MM format)")
    credential: Optional[str] = Field(None, description="Certificate ID or credential")


class Publication(BaseModel):
    """Publication entry"""
    title: str = Field(description="Publication title")
    publisher: str = Field(description="Where published")
    publicationDate: Optional[str] = Field(None, description="Publication date (YYYY-MM format)")
    url: Optional[str] = Field(None, description="Link to publication")


class Reference(BaseModel):
    """Professional reference"""
    name: str = Field(description="Reference name")
    position: Optional[str] = Field(None, description="Their job title")
    company: Optional[str] = Field(None, description="Their company")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")


class Internship(BaseModel):
    """Internship entry"""
    position: str = Field(description="Internship title")
    company: str = Field(description="Company name")
    location: Optional[str] = Field(None, description="Location")
    startDate: Optional[str] = Field(None, description="Start date (YYYY-MM format)")
    endDate: Optional[str] = Field(None, description="End date (YYYY-MM format)")
    description: Optional[str] = Field(None, description="What they did")


class Award(BaseModel):
    """Award or honor entry"""
    title: str = Field(description="Award name")
    city: Optional[str] = Field(None, description="Where received")
    startDate: Optional[str] = Field(None, description="Date received (YYYY-MM format)")
    endDate: Optional[str] = Field(None, description="End date if applicable")
    current: bool = Field(False, description="Whether currently held")
    description: Optional[str] = Field(None, description="Details about the award")


class Volunteering(BaseModel):
    """Volunteer work entry"""
    title: str = Field(description="Volunteer role")
    city: Optional[str] = Field(None, description="Location")
    startDate: Optional[str] = Field(None, description="Start date (YYYY-MM format)")
    endDate: Optional[str] = Field(None, description="End date (YYYY-MM format)")
    current: bool = Field(False, description="Whether currently volunteering")
    description: Optional[str] = Field(None, description="Details about the role")


class CustomSections(BaseModel):
    """Custom additional sections"""
    awards: List[Award] = Field(default_factory=list, description="Awards and honors")
    volunteering: List[Volunteering] = Field(default_factory=list, description="Volunteer work")


class CVData(BaseModel):
    """Complete CV data structure matching cv_parser.py output"""
    personalInfo: PersonalInfo = Field(description="Personal information")
    professionalSummary: str = Field(default="", description="Professional summary or objective")
    employmentHistory: List[Employment] = Field(default_factory=list, description="Work experience")
    education: List[Education] = Field(default_factory=list, description="Educational background")
    skills: List[Skill] = Field(default_factory=list, description="Skills list")
    languages: List[Language] = Field(default_factory=list, description="Language proficiencies")
    courses: List[Course] = Field(default_factory=list, description="Courses and certifications")
    publications: List[Publication] = Field(default_factory=list, description="Publications and papers")
    projects: List[Project] = Field(default_factory=list, description="Projects portfolio")
    references: List[Reference] = Field(default_factory=list, description="Professional references")
    hobbies: List[str] = Field(default_factory=list, description="Hobbies and interests")
    internships: List[Internship] = Field(default_factory=list, description="Internship experience")
    customSections: CustomSections = Field(default_factory=CustomSections, description="Additional custom sections")

    class Config:
        json_schema_extra = {
            "example": {
                "personalInfo": {
                    "firstName": "John",
                    "lastName": "Doe",
                    "email": "john.doe@example.com",
                    "jobTitle": "Senior Software Engineer"
                },
                "professionalSummary": "Experienced software engineer with 8+ years...",
                "employmentHistory": [
                    {
                        "position": "Senior Software Engineer",
                        "company": "Tech Corp",
                        "startDate": "2020-01",
                        "currentlyWorking": True,
                        "responsibilities": ["Led team of 5 developers", "Architected microservices"]
                    }
                ],
                "skills": [
                    {"skill": "Python", "level": "expert", "category": "technical"},
                    {"skill": "Docker", "level": "advanced", "category": "tool"}
                ],
                "yearsOfExperience": 8
            }
        }
