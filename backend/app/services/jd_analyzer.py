"""
Job Description Analyzer Service - Refactored with LangChain
Extracts requirements and details from job descriptions using Google Gemini.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

from app.config import get_settings
from app.schemas.jd_schemas import JDData
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import store_jd_embedding
from app.services.prompts.jd_analyzer_prompts import JD_ANALYZER_PROMPT

settings = get_settings()


def analyze_jd_with_gemini(jd_text: str) -> dict:
    """
    Extract requirements from job description with LangChain and Pydantic validation.

    Args:
        jd_text: Raw job description text

    Returns:
        Structured JD data as dict, validated against JDData schema
    """

    # Initialize LangChain components
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3,
        max_retries=3,  # Automatic retry on failures
        request_timeout=60,
        google_api_key=settings.GEMINI_API_KEY
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=JDData)

    # Format the prompt with actual data
    formatted_prompt = JD_ANALYZER_PROMPT.format(
        jd_text=jd_text,
        format_instructions=parser.get_format_instructions()
    )

    try:
        # Call Gemini with automatic retry logic
        response = llm.invoke(formatted_prompt)

        # Parse and validate response with Pydantic
        parsed_data = parser.parse(response.content)

        # Convert to dict for compatibility
        return parsed_data.dict(by_alias=True)

    except Exception as e:
        print(f"Error analyzing JD with Gemini: {e}")

        # Return default structure that matches JDData schema
        default_jd = JDData(
            companyName=None,
            positionTitle=None,
            location=None,
            workMode=None,
            salaryRange=None,
            experienceYearsRequired=0,
            experienceLevel="mid",
            hardSkillsRequired=[],
            softSkillsRequired=[],
            responsibilities=[],
            techStack=[],
            domainExpertise={"industry": None, "specificKnowledge": []},
            implicitRequirements=[],
            companyCultureSignals=[],
            atsKeywords=[]
        )

        return default_jd.dict(by_alias=True)


def store_jd_embeddings(jd_id: str, jd_parsed: dict) -> str:
    """
    Generate and store embeddings for JD in Qdrant.

    Args:
        jd_id: Unique identifier for the JD
        jd_parsed: Parsed JD data dictionary

    Returns:
        Qdrant point ID for the stored embedding
    """

    # Combine requirements into text
    hard_skills = jd_parsed.get('hard_skills_required', [])
    skills_text = ', '.join([skill['skill'] for skill in hard_skills]) if hard_skills else ''

    responsibilities_text = ' '.join(jd_parsed.get('responsibilities', []))

    full_text = f"""
    Position: {jd_parsed.get('position_title', '')}
    Requirements: {skills_text}
    Responsibilities: {responsibilities_text}
    """

    # Generate embedding
    embedding = generate_embedding(full_text)

    # Store in Qdrant
    point_id = store_jd_embedding(
        jd_id=jd_id,
        text=full_text,
        embedding=embedding,
        metadata={
            "requirement_type": "full",
            "position": jd_parsed.get('position_title', 'Unknown'),
            "company": jd_parsed.get('company_name', 'Unknown')
        }
    )

    return point_id
