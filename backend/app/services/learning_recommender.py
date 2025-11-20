import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_learning_recommendations(
    cv_data: dict,
    jd_data: dict,
    gaps: list,
    score_data: dict,
    cv_id: str = None
) -> dict:
    """Generate personalized learning path with courses and timeline"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar successful learning paths
    rag_context = ""
    if cv_id:
        query_text = f"Learning path for: {', '.join([g.get('gap', '') for g in gaps[:5]])}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    prompt = f"""Create a personalized learning path to improve this candidate's profile:

CURRENT PROFILE:
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

IDENTIFIED GAPS:
{json.dumps(gaps, indent=2)}

CURRENT SCORE: {score_data.get('overall_score', 0)}%
TARGET SCORE: 85%+

{f"SUCCESSFUL LEARNING PATHS FROM SIMILAR CASES:\n{rag_context}" if rag_context else ""}

Generate a comprehensive learning plan with:
1. Quick wins (things they can learn/do this week)
2. Priority courses (3-5 most impactful courses)
3. 10-week roadmap (weekly breakdown)
4. Estimated time investment and cost
5. Expected score improvement

Return JSON:
{{
    "current_score": 0,
    "target_score": 85,
    "estimated_weeks": 10,
    "quick_wins": [
        {{
            "action": "string - what to do",
            "time": "string - e.g., '2 hours'",
            "impact": "string - e.g., '+3% score'",
            "description": "string - why this helps"
        }}
    ],
    "priority_courses": [
        {{
            "title": "string - course name",
            "platform": "Udemy/Coursera/DeepLearning.AI/etc",
            "url": "string or null",
            "duration": "string - e.g., '24 hours'",
            "cost": "string - e.g., '$19.99' or 'Free'",
            "impact": "string - e.g., '+10% score'",
            "priority": "critical/high/medium",
            "skills_covered": ["array of skills"],
            "why_recommended": "string"
        }}
    ],
    "roadmap": [
        {{
            "week": 1,
            "focus": "string - main goal",
            "tasks": ["array of specific tasks"],
            "hours_per_week": 10,
            "milestone": "string - what you'll achieve"
        }}
    ],
    "total_investment": {{
        "time_hours": 100,
        "cost_usd": 50,
        "expected_score_improvement": "+20%"
    }},
    "recommendations": ["array of general advice"]
}}

Be specific with real courses, realistic timelines, and accurate costs."""

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

        learning_path = json.loads(response_text)
        return learning_path

    except Exception as e:
        print(f"Error generating learning recommendations with Gemini: {e}")
        return {
            "error": str(e),
            "current_score": score_data.get('overall_score', 0),
            "target_score": 85,
            "estimated_weeks": 10,
            "quick_wins": [],
            "priority_courses": [],
            "roadmap": [],
            "total_investment": {
                "time_hours": 0,
                "cost_usd": 0,
                "expected_score_improvement": "+0%"
            },
            "recommendations": []
        }
