"""
Scorer Service - Refactored with LangChain
Calculates compatibility scores using vector similarity + AI qualitative analysis.
"""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

from app.config import get_settings
from app.schemas.scorer_schemas import ScorerAnalysis
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from app.services.vector_scorer import calculate_vector_similarity_score
from app.services.prompts.scorer_prompts import SCORER_PROMPT

settings = get_settings()


def calculate_compatibility_score(cv_data: dict, jd_data: dict, cv_id: str = None) -> dict:
    """
    Calculate detailed compatibility score using:
    1. Vector similarity for OBJECTIVE numerical scoring (deterministic)
    2. AI analysis for QUALITATIVE insights (gaps, strengths, recommendations)

    Args:
        cv_data: Parsed CV data
        jd_data: Parsed job description data
        cv_id: Optional CV ID for RAG context

    Returns:
        Combined score dictionary with vector scores and AI insights
    """

    # STEP 1: Calculate objective score using vector similarity (UNCHANGED)
    vector_score_data = calculate_vector_similarity_score(cv_data, jd_data)

    # STEP 2: Use AI only for qualitative analysis (REFACTORED WITH LANGCHAIN)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.1,  # Low temperature for consistent analysis
        max_retries=3,
        request_timeout=60,
        google_api_key=settings.GEMINI_API_KEY
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=ScorerAnalysis)

    # Generate query embedding for RAG
    query_text = f"Skills needed: {', '.join([s.get('skill', '') for s in jd_data.get('hard_skills_required', [])])}"
    query_embedding = generate_embedding(query_text)

    # Get RAG context from similar CVs/JDs
    rag_context = ""
    if cv_id:
        rag_ctx = get_rag_context_for_cv(cv_id, query_text, query_embedding)
        if rag_ctx:
            rag_context = f"ADDITIONAL CONTEXT FROM SIMILAR CASES:\n{rag_ctx}"

    # Format vector score data for prompt
    vector_score_summary = f"""- Overall Score: {vector_score_data['overall_score']}%
- Hard Skills: {vector_score_data['breakdown']['hard_skills']['score']}%
  - Matched: {vector_score_data['breakdown']['hard_skills']['matched']}
  - Missing: {vector_score_data['breakdown']['hard_skills']['missing']}"""

    # Format the prompt
    formatted_prompt = SCORER_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2),
        jd_data=json.dumps(jd_data, indent=2),
        vector_score_data=vector_score_summary,
        rag_context=rag_context,
        format_instructions=parser.get_format_instructions()
    )

    try:
        # Call Gemini with automatic retry logic
        response = llm.invoke(formatted_prompt)

        # Parse and validate response with Pydantic
        ai_analysis = parser.parse(response.content)

        # STEP 3: Combine vector scores with AI insights
        final_result = {
            "overall_score": vector_score_data['overall_score'],
            "breakdown": vector_score_data['breakdown'],
            "top_gaps": [gap.dict() for gap in ai_analysis.topGaps],
            "strengths": ai_analysis.strengths,
            "recommendations": ai_analysis.recommendations
        }

        return final_result

    except Exception as e:
        print(f"Error in AI analysis: {e}")
        # If AI fails, still return vector scores with empty insights
        return {
            "overall_score": vector_score_data['overall_score'],
            "breakdown": vector_score_data['breakdown'],
            "top_gaps": [],
            "strengths": [],
            "recommendations": []
        }
