import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv, get_rag_context_for_jd

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def calculate_compatibility_score(cv_data: dict, jd_data: dict, cv_id: str = None) -> dict:
    """Calculate detailed compatibility score using AI with RAG context"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Generate query embedding for RAG
    query_text = f"Skills needed: {', '.join([s['skill'] for s in jd_data.get('hard_skills_required', [])])}"
    query_embedding = generate_embedding(query_text)

    # Get RAG context from similar CVs/JDs
    rag_context = ""
    if cv_id:
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    rag_section = ""
    if rag_context:
        rag_section = f"ADDITIONAL CONTEXT FROM SIMILAR CASES:\n{rag_context}\n\n"

    prompt = f"""Analyze the match between this CV and Job Description:

CV DATA:
{json.dumps(cv_data, indent=2)}

JOB DESCRIPTION DATA:
{json.dumps(jd_data, indent=2)}

{rag_section}Calculate a detailed compatibility score. Return ONLY valid JSON (no markdown):
""" + """{
    "overall_score": 0,
    "breakdown": {
        "hard_skills": {
            "score": 0,
            "weight": 35,
            "matched": ["array of matched skills"],
            "missing": ["array of missing skills"]
        },
        "soft_skills": {
            "score": 0,
            "weight": 15,
            "matched": ["array"],
            "missing": ["array"]
        },
        "experience": {
            "score": 0,
            "weight": 20,
            "candidate_years": 0,
            "required_years": 0,
            "assessment": "string"
        },
        "domain": {
            "score": 0,
            "weight": 15,
            "assessment": "string"
        },
        "portfolio": {
            "score": 0,
            "weight": 10,
            "assessment": "string"
        },
        "logistics": {
            "score": 0,
            "weight": 5,
            "assessment": "string"
        }
    },
    "top_gaps": [
        {
            "gap": "string",
            "priority": "critical/high/medium",
            "impact": "string (e.g., '+15% score if added')"
        }
    ],
    "strengths": ["array of candidate strengths"],
    "recommendations": ["array of actionable recommendations"]
}

Overall score should be 0-100. Be realistic and detailed."""

    generation_config = {
        "temperature": 0.3,
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

        score_data = json.loads(response_text)
        return score_data

    except Exception as e:
        print(f"Error calculating score with Gemini: {e}")
        return {"error": str(e), "overall_score": 0}
