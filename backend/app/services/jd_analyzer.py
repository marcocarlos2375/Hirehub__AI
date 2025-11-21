import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import store_jd_embedding
from app.services.cache_service import cached
from app.services.timeout_handler import with_timeout_and_retry

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

@cached("jd_analyze", ttl=3600)
@with_timeout_and_retry(timeout_seconds=30, max_retries=2)
def analyze_jd_with_gemini(jd_text: str) -> dict:
    """Extract requirements from job description"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    prompt = f"""Analyze this job description and extract requirements:

{jd_text}

Return ONLY a valid JSON object (no markdown, no backticks) with:
{{
    "company_name": "string or null",
    "position_title": "string or null",
    "location": "string or null",
    "work_mode": "remote/hybrid/onsite or null",
    "salary_range": "string or null",
    "experience_years_required": 0,
    "experience_level": "junior/mid/senior",
    "hard_skills_required": [
        {{
            "skill": "string",
            "priority": "critical/important/nice"
        }}
    ],
    "soft_skills_required": ["array of strings"],
    "responsibilities": ["array of key duties"],
    "tech_stack": ["array of technologies"],
    "domain_expertise": {{
        "industry": "string or null",
        "specific_knowledge": ["array"]
    }},
    "implicit_requirements": ["things not stated but implied"],
    "company_culture_signals": ["array"],
    "ats_keywords": ["array of important terms"]
}}

Be thorough and extract all information."""

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

        parsed_data = json.loads(response_text)
        return parsed_data

    except Exception as e:
        print(f"Error analyzing JD with Gemini: {e}")
        return {"error": str(e)}

def store_jd_embeddings(jd_id: str, jd_parsed: dict) -> str:
    """Generate and store embeddings for JD in Qdrant"""

    # Combine requirements into text
    full_text = f"""
    Position: {jd_parsed.get('position_title', '')}
    Requirements: {', '.join([skill['skill'] for skill in jd_parsed.get('hard_skills_required', [])])}
    Responsibilities: {' '.join(jd_parsed.get('responsibilities', []))}
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
