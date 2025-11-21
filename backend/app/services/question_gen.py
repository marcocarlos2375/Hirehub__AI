import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from app.services.toon_serializer import to_toon_string
from app.services.cache_service import cached
from app.services.timeout_handler import with_timeout_and_retry

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

async def generate_smart_questions(cv_data: dict, jd_data: dict, gaps: list, cv_id: str = None) -> list:
    """Generate smart questions to uncover hidden experience using RAG (ASYNC)"""

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

    # Compress data - only send what's needed for question generation
    candidate_summary = {
        "name": cv_data.get('personal_info', {}).get('name', 'Candidate'),
        "years_exp": cv_data.get('years_of_experience', 0),
        "skills": list(set(
            cv_data.get('skills', {}).get('technical_skills', []) +
            cv_data.get('skills', {}).get('soft_skills', [])
        ))[:15]  # Top 15 skills only
    }

    job_requirements = {
        "position": jd_data.get('position_title', ''),
        "required_skills": [s.get('skill', '') for s in jd_data.get('hard_skills_required', [])][:10]  # Top 10
    }

    prompt = f"""Based on these gaps between the candidate and job:

CANDIDATE: {candidate_summary['name']} ({candidate_summary['years_exp']} years experience)
Skills: {', '.join(candidate_summary['skills'])}

JOB: {job_requirements['position']}
Required: {', '.join(job_requirements['required_skills'])}

IDENTIFIED GAPS:
{json.dumps(gaps, indent=2)}

{rag_section}Generate 5-8 smart questions to uncover hidden experience that could close these gaps.

For EACH question, also provide 3-4 suggested answer options that users can select from. These should:
- Be realistic and varied (from beginner to expert level)
- Cover different levels of experience (e.g., "Yes, extensively", "Some experience", "Learning/exploring", "Not yet")
- Be written in first person, ready to use
- Let users customize them further
- Contextually include negative/"not yet" options when appropriate

Return ONLY valid JSON array (no markdown):
""" + """[
    {
        "question": "string - the actual question",
        "category": "technical/domain/experience/soft_skills",
        "priority": "critical/high/medium/low",
        "potential_impact": "string (e.g., '+10% score if yes')",
        "why_asking": "string - explain what gap this addresses",
        "suggested_answers": [
            "string - first person answer option 1",
            "string - first person answer option 2",
            "string - first person answer option 3",
            "string - optional 4th answer"
        ]
    }
]

Make questions specific, actionable, and easy to answer. Suggested answers should be ready to use but editable."""

    generation_config = {
        "temperature": 0.4,
        "response_mime_type": "application/json"
    }

    try:
        response = await model.generate_content_async(prompt, generation_config=generation_config)
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
