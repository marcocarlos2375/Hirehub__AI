import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv, get_rag_context_for_jd
from app.services.vector_scorer import calculate_vector_similarity_score

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def calculate_compatibility_score(cv_data: dict, jd_data: dict, cv_id: str = None) -> dict:
    """
    Calculate detailed compatibility score using:
    1. Vector similarity for OBJECTIVE numerical scoring (deterministic)
    2. AI analysis for QUALITATIVE insights (gaps, strengths, recommendations)
    """

    # STEP 1: Calculate objective score using vector similarity
    vector_score_data = calculate_vector_similarity_score(cv_data, jd_data)

    # STEP 2: Use AI only for qualitative analysis (gaps, strengths, recommendations)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Generate query embedding for RAG
    query_text = f"Skills needed: {', '.join([s['skill'] for s in jd_data.get('hard_skills_required', [])])}"
    query_embedding = generate_embedding(query_text)

    # Get RAG context from similar CVs/JDs
    rag_context = ""
    if cv_id:
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    prompt = f"""Analyze the gaps, strengths, and provide recommendations for this CV and Job Description match.

CV DATA:
{json.dumps(cv_data, indent=2)}

JOB DESCRIPTION DATA:
{json.dumps(jd_data, indent=2)}

CURRENT MATCH SCORE (calculated via vector similarity):
- Overall Score: {vector_score_data['overall_score']}%
- Hard Skills: {vector_score_data['breakdown']['hard_skills']['score']}%
  - Matched: {vector_score_data['breakdown']['hard_skills']['matched']}
  - Missing: {vector_score_data['breakdown']['hard_skills']['missing']}

{f"ADDITIONAL CONTEXT FROM SIMILAR CASES:{chr(10)}{rag_context}" if rag_context else ""}

YOUR TASK: Provide qualitative analysis ONLY (do NOT recalculate scores):

1. TOP GAPS: Identify 5-8 critical missing elements that hurt the score
   - Focus on missing hard skills with high priority
   - Include experience gaps, domain mismatches
   - Estimate impact if gap is filled (e.g., "+15% score")

2. STRENGTHS: Identify 3-5 strong points in the CV that match well
   - Highlight matched skills with high similarity
   - Note relevant experience or achievements

3. RECOMMENDATIONS: Provide 3-5 actionable suggestions to improve match

Return ONLY valid JSON (no markdown):
{{
    "top_gaps": [
        {{
            "gap": "string - what's missing",
            "priority": "critical/high/medium",
            "impact": "string (e.g., '+15% score if addressed')"
        }}
    ],
    "strengths": ["array of 3-5 candidate strengths that match JD"],
    "recommendations": ["array of 3-5 actionable recommendations"]
}}

Be specific, honest, and actionable."""

    generation_config = {
        "temperature": 0.1,
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

        ai_analysis = json.loads(response_text)

        # STEP 3: Combine vector scores with AI insights
        final_result = {
            "overall_score": vector_score_data['overall_score'],
            "breakdown": vector_score_data['breakdown'],
            "top_gaps": ai_analysis.get('top_gaps', []),
            "strengths": ai_analysis.get('strengths', []),
            "recommendations": ai_analysis.get('recommendations', [])
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
