"""
Interview Preparation Service - Refactored with LangChain
Generates comprehensive interview preparation materials.
"""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

from app.config import get_settings
from app.schemas.interview_schemas import InterviewPrep
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from app.services.prompts.interview_prompts import INTERVIEW_PREP_PROMPT

settings = get_settings()


def generate_interview_prep(cv_data: dict, jd_data: dict, answers: dict, gaps: list, cv_id: str = None) -> dict:
    """
    Generate comprehensive interview preparation materials.

    Args:
        cv_data: Parsed CV data
        jd_data: Parsed job description data
        answers: User's answers to smart questions
        gaps: Identified gaps from scoring
        cv_id: Optional CV ID for RAG context

    Returns:
        Interview prep dictionary with questions, answers, and strategies
    """

    # Initialize LangChain components
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.3,
        max_retries=3,
        request_timeout=60,
        google_api_key=settings.GEMINI_API_KEY
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=InterviewPrep)

    # Get RAG context from similar interview scenarios
    rag_context = ""
    if cv_id:
        query_text = f"Interview questions for {jd_data.get('position_title', 'position')} with focus on: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_ctx = get_rag_context_for_cv(cv_id, query_text, query_embedding)
        if rag_ctx:
            rag_context = f"INTERVIEW INSIGHTS FROM SIMILAR ROLES:\n{rag_ctx}"

    # Format the prompt with actual data
    formatted_prompt = INTERVIEW_PREP_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2),
        jd_data=json.dumps(jd_data, indent=2),
        answers=json.dumps(answers, indent=2),
        gaps=json.dumps(gaps, indent=2),
        rag_context=rag_context,
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
        print(f"Error generating interview prep with Gemini: {e}")
        return {"error": str(e)}
