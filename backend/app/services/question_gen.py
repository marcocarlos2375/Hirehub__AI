import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_smart_questions(cv_data: dict, jd_data: dict, gaps: list, cv_id: str = None) -> list:
    """Generate smart questions to uncover hidden experience using RAG"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context
    rag_context = ""
    if cv_id:
        query_text = f"Questions about: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    rag_section = ""
    if rag_context:
        rag_section = f"SIMILAR QUESTIONS FROM PAST CASES:\n{rag_context}\n\n"

    prompt = f"""Based on these gaps between the CV and job requirements:

CV SUMMARY:
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

TOP GAPS:
{json.dumps(gaps, indent=2)}

{rag_section}Generate 5-8 smart questions to uncover hidden experience that could close these gaps.

Return ONLY valid JSON array (no markdown):
""" + """[
    {
        "question": "string - the actual question",
        "category": "technical/domain/experience/soft_skills",
        "priority": "critical/high/medium/low",
        "potential_impact": "string (e.g., '+10% score if yes')",
        "why_asking": "string - explain what gap this addresses"
    }
]

Make questions specific, actionable, and easy to answer with yes/no + details."""

    generation_config = {
        "temperature": 0.4,
        "response_mime_type": "application/json"
    }

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        questions = json.loads(response_text)
        return questions

    except Exception as e:
        print(f"Error generating questions with Gemini: {e}")
        return []
