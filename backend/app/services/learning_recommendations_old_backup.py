import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_learning_path(cv_data: dict, jd_data: dict, gaps: list, score_data: dict, cv_id: str = None) -> dict:
    """Generate personalized learning roadmap to close skill gaps"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar learning paths
    rag_context = ""
    if cv_id:
        query_text = f"Learning path for skills: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    current_score = score_data.get('overall_score', 0)
    target_score = min(100, current_score + 20)  # Aim for +20 points

    prompt = f"""Generate a comprehensive, personalized learning roadmap based on:

CV DATA (with personalInfo, employmentHistory, skills array with levels, courses, languages):
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

CURRENT SCORE: {current_score}
TARGET SCORE: {target_score}

IDENTIFIED GAPS:
{json.dumps(gaps, indent=2)}

SCORE BREAKDOWN:
{json.dumps(score_data.get('breakdown', {}), indent=2)}

{f"SUCCESSFUL LEARNING PATHS FROM SIMILAR CASES:{chr(10)}{rag_context}" if rag_context else ""}

IMPORTANT - CV STRUCTURE NOTES:
- Skills are in array format with skill name, level (Beginner/Intermediate/Advanced), and category
- Employment history shows positions with startDate/endDate
- May include existing courses the candidate has taken
- Languages show proficiency levels (A1-C2/Native)

Create a realistic, actionable learning plan with:

1. QUICK WINS (1-2 weeks, achievable immediately):
   - CV reframing techniques
   - LinkedIn profile optimization
   - One weekend project using critical missing skills
   - Estimated impact: +5-10% score

2. PRIORITY LEARNING AREAS (ranked by impact):
   For each priority area, include:
   - Specific courses (prefer FREE options: Coursera audit, YouTube, freeCodeCamp, etc.)
   - Platform, duration, cost
   - Hands-on projects with detailed feature lists
   - Expected score improvement
   - Time investment

3. WEEKLY ROADMAP (10-week timeline):
   - Week-by-week breakdown
   - Specific tasks for each week
   - Cumulative score improvement tracking
   - Realistic time estimates

4. TOTAL INVESTMENT ANALYSIS:
   - Total time required
   - Total cost (prioritize free resources)
   - Expected score improvement
   - ROI analysis (time vs career impact)

Return ONLY valid JSON (no markdown):
{{
    "current_score": {current_score},
    "target_score": {target_score},
    "quick_wins": [
        {{
            "action": "string - specific action to take",
            "time": "string - hours or days",
            "impact": "string - e.g., '+5%'",
            "details": ["array of specific steps"]
        }}
    ],
    "priority_areas": [
        {{
            "priority": 1,
            "skill": "string - skill name",
            "current_level": "string - beginner/intermediate/none",
            "target_level": "string - intermediate/advanced",
            "impact": "string - e.g., '+15%'",
            "time": "string - e.g., '40-50 hours'",
            "why_important": "string - why this matters for the role",
            "courses": [
                {{
                    "name": "string",
                    "platform": "string",
                    "duration": "string - hours",
                    "cost": "string - FREE or $amount",
                    "url": "string - course URL if available",
                    "impact": "string - '+X%'",
                    "topics": ["array of key topics covered"]
                }}
            ],
            "projects": [
                {{
                    "name": "string - project name",
                    "description": "string - what to build",
                    "time": "string - hours",
                    "impact": "string - '+X%'",
                    "features": ["array of specific features to implement"],
                    "technologies": ["array of tech stack"]
                }}
            ]
        }}
    ],
    "weekly_roadmap": [
        {{
            "week": "string - e.g., '1-2'",
            "focus": "string - main focus area",
            "tasks": ["array of specific tasks"],
            "hours": "string - estimated hours",
            "score_after": 72,
            "deliverables": ["array of what should be completed"]
        }}
    ],
    "total_investment": {{
        "time": "string - total hours",
        "cost": "string - total cost",
        "score_improvement": "string - e.g., '+20%'",
        "timeline": "string - e.g., '10 weeks'",
        "roi_analysis": "string - analysis of time vs career impact"
    }},
    "resources": {{
        "free_platforms": ["array of recommended free learning platforms"],
        "communities": ["array of relevant communities to join"],
        "certifications": ["array of valuable certifications to consider"]
    }}
}}

Be specific, realistic, and actionable. Prioritize FREE resources where possible. Focus on skills that will have the most impact on the score and job prospects."""

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

        learning_path = json.loads(response_text)
        return learning_path

    except Exception as e:
        print(f"Error generating learning path with Gemini: {e}")
        return {"error": str(e)}
