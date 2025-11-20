"""
Question Generation Service - Refactored with LangChain
Generates smart questions to uncover hidden experience using RAG context.
"""

import json
from typing import List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

from app.config import get_settings
from app.schemas.question_schemas import QuestionsList
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from app.services.prompts.question_prompts import QUESTION_GEN_PROMPT

settings = get_settings()


def generate_smart_questions(cv_data: dict, jd_data: dict, gaps: list, cv_id: str = None) -> list:
    """
    Generate smart questions to uncover hidden experience using RAG.

    Args:
        cv_data: Parsed CV data dictionary
        jd_data: Parsed job description data dictionary
        gaps: List of identified gaps from scoring
        cv_id: Optional CV ID for RAG context retrieval

    Returns:
        List of smart questions with suggested answers
    """

    # Initialize LangChain components
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.4,  # Slightly higher for creative question generation
        max_retries=3,
        request_timeout=60,
        google_api_key=settings.GEMINI_API_KEY
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=QuestionsList)

    # Get RAG context if cv_id provided
    rag_context = ""
    if cv_id:
        query_text = f"Questions about: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_ctx = get_rag_context_for_cv(cv_id, query_text, query_embedding)
        if rag_ctx:
            rag_context = f"SIMILAR QUESTIONS FROM PAST CASES:\n{rag_ctx}"

    # Format the prompt with actual data
    formatted_prompt = QUESTION_GEN_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2),
        jd_data=json.dumps(jd_data, indent=2),
        gaps=json.dumps(gaps, indent=2),
        rag_context=rag_context,
        format_instructions=parser.get_format_instructions()
    )

    try:
        # Call Gemini with automatic retry logic
        response = llm.invoke(formatted_prompt)

        # Parse and validate response with Pydantic
        parsed_data = parser.parse(response.content)

        # Convert to list of dicts for compatibility
        questions_list = [q.dict(by_alias=True) for q in parsed_data.questions]

        return questions_list

    except Exception as e:
        print(f"Error generating questions with Gemini: {e}")
        return []
