"""
CV Parser Service - Refactored with LangChain
Extracts structured data from CV files using Google Gemini with type-safe Pydantic validation.
"""

import fitz  # PyMuPDF
from docx import Document
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from app.config import get_settings
from app.schemas.cv_schemas import CVData
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import store_cv_embedding

settings = get_settings()


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX"""
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def parse_cv_with_gemini(cv_text: str) -> dict:
    """
    Use Gemini to structure CV data with LangChain and Pydantic validation.

    Args:
        cv_text: Raw text extracted from CV

    Returns:
        Structured CV data as dict, validated against CVData schema
    """

    # Initialize LangChain components
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3,
        max_retries=3,  # Automatic retry on rate limits/failures
        request_timeout=60
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=CVData)

    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["cv_text", "format_instructions"],
        template="""Extract structured information from this CV/Resume:

{cv_text}

{format_instructions}

INSTRUCTIONS:
- Extract ALL information present in the CV
- For dates, use YYYY-MM format when available, otherwise YYYY
- Categorize skills appropriately (technical vs soft skills)
- Set level for each skill based on context (if unclear, use "Intermediate")
- For skill categories, use: Programming Languages, Frontend Frameworks, Backend Technologies, Cloud Platforms, DevOps & Tools, Soft Skills, Other
- For language proficiency, use levels: A1, A2, B1, B2, C1, C2, Native
- Parse employment dates into startDate/endDate format
- Set currentlyWorking=true for current positions
- Extract hobbies, awards, volunteer work if present
- If information is not present, use null or empty arrays
- Be thorough and accurate

Return the structured data following the format specified above."""
    )

    # Format the prompt with actual data
    formatted_prompt = prompt.format(
        cv_text=cv_text,
        format_instructions=parser.get_format_instructions()
    )

    try:
        # Call Gemini with automatic retry logic
        response = llm.invoke(formatted_prompt)

        # Parse and validate response with Pydantic
        # Parser automatically handles markdown stripping and JSON parsing
        parsed_data = parser.parse(response.content)

        # Convert to dict for compatibility with existing code
        return parsed_data.dict()

    except Exception as e:
        print(f"Error parsing CV with Gemini: {e}")

        # Return default structure that matches CVData schema
        default_cv = CVData(
            personalInfo={
                "jobTitle": None,
                "firstName": None,
                "lastName": None,
                "email": None,
                "phone": None,
                "address": None,
                "website": None,
                "birthDate": None,
                "nationality": None,
                "relationshipStatus": None,
                "availability": None,
                "socialLinks": []
            },
            professionalSummary=cv_text[:500] if cv_text else "",
            employmentHistory=[],
            education=[],
            skills=[],
            languages=[],
            courses=[],
            publications=[],
            projects=[],
            references=[],
            hobbies=[],
            internships=[],
            customSections={"awards": [], "volunteering": []}
        )

        return default_cv.dict()


def store_cv_embeddings(cv_id: str, cv_parsed: dict) -> str:
    """
    Generate and store embeddings for different CV sections in Qdrant.

    Args:
        cv_id: Unique identifier for the CV
        cv_parsed: Parsed CV data dictionary

    Returns:
        Qdrant point ID for the stored embedding
    """

    # Extract skills as text
    skills_list = [s.get('skill', '') for s in cv_parsed.get('skills', [])]
    skills_text = ', '.join(skills_list)

    # Extract employment history as text
    employment_text = ' '.join([
        f"{emp.get('position', '')} at {emp.get('company', '')}"
        for emp in cv_parsed.get('employmentHistory', [])
    ])

    # Calculate years of experience (simplified)
    employment_history = cv_parsed.get('employmentHistory', [])
    years_of_experience = len(employment_history)

    # Combine all text for full CV embedding
    full_text = f"""
    Summary: {cv_parsed.get('professionalSummary', '')}
    Skills: {skills_text}
    Experience: {employment_text}
    """

    # Generate embedding for full CV
    full_embedding = generate_embedding(full_text)

    # Store in Qdrant
    personal_info = cv_parsed.get('personalInfo', {})
    name = f"{personal_info.get('firstName', '')} {personal_info.get('lastName', '')}".strip() or "Unknown"

    point_id = store_cv_embedding(
        cv_id=cv_id,
        text=full_text,
        embedding=full_embedding,
        metadata={
            "section": "full",
            "name": name,
            "years_of_experience": years_of_experience
        }
    )

    return point_id
