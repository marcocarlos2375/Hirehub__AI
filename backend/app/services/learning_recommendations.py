"""
Learning Recommendations Service - Refactored with LangChain
Generates personalized learning roadmap to close skill gaps.
"""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

from app.config import get_settings
from app.schemas.learning_schemas import LearningPath
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from app.services.prompts.learning_prompts import LEARNING_PATH_PROMPT

settings = get_settings()


def generate_learning_path(cv_data: dict, jd_data: dict, gaps: list, score_data: dict, cv_id: str = None) -> dict:
    """
    Generate personalized learning roadmap to close skill gaps.

    Args:
        cv_data: Parsed CV data
        jd_data: Parsed job description data
        gaps: Identified gaps from scoring
        score_data: Score breakdown data
        cv_id: Optional CV ID for RAG context

    Returns:
        Learning path dictionary with roadmap, resources, timeline
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
    parser = PydanticOutputParser(pydantic_object=LearningPath)

    # Get RAG context from similar learning paths
    rag_context = ""
    if cv_id:
        query_text = f"Learning path for skills: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_ctx = get_rag_context_for_cv(cv_id, query_text, query_embedding)
        if rag_ctx:
            rag_context = f"SUCCESSFUL LEARNING PATHS FROM SIMILAR CASES:\n{rag_ctx}"

    # Calculate scores
    current_score = score_data.get('overall_score', 0)
    target_score = min(100, current_score + 20)  # Aim for +20 points

    # Format the prompt with actual data
    formatted_prompt = LEARNING_PATH_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2),
        jd_data=json.dumps(jd_data, indent=2),
        current_score=current_score,
        target_score=target_score,
        gaps=json.dumps(gaps, indent=2),
        score_breakdown=json.dumps(score_data.get('breakdown', {}), indent=2),
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
        print(f"Error generating learning path with Gemini: {e}")
        return {"error": str(e)}
