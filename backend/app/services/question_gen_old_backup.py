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

    prompt = f"""Based on these gaps between the CV and job requirements:

CV SUMMARY (with personalInfo, employmentHistory, skills array with levels):
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

TOP GAPS:
{json.dumps(gaps, indent=2)}

{f"SIMILAR QUESTIONS FROM PAST CASES:{chr(10)}{rag_context}" if rag_context else ""}

INSTRUCTIONS:
- CV uses new structure with employmentHistory, skills array, courses, publications
- Consider all CV sections including languages, hobbies, customSections when formulating questions
- Ask about experience that might be in hobbies, volunteering, or side projects

Generate 5-8 smart questions to uncover hidden experience that could close these gaps.

Return ONLY valid JSON array (no markdown):
[
    {{
        "question": "string - the actual question",
        "category": "technical/domain/experience/soft_skills",
        "priority": "critical/high/medium/low",
        "potential_impact": "string (e.g., '+10% score if yes')",
        "why_asking": "string - explain what gap this addresses",
        "suggested_answers": [
            "string - answer option 1 (strongest experience level)",
            "string - answer option 2 (moderate experience)",
            "string - answer option 3 (learning/basic level)",
            "string - answer option 4 (alternative perspective)"
        ],
        "answer_tips": ["string - tip 1", "string - tip 2"]
    }}
]

IMPORTANT - For suggested_answers array (provide 3-4 options):
- Generate multiple answer OPTIONS with varying experience levels
- Option 1: Strong/extensive experience - "Yes, I developed X using Y for [mention specific project]. Achieved Z results with A impact."
- Option 2: Moderate experience - "I've used X in [company/project]. Built Y features and learned Z."
- Option 3: Basic/learning - "I have some experience with X through [courses/personal projects]. Familiar with Y concepts."
- Option 4: Alternative angle - Different approach or related experience
- Include helpful placeholders: [mention specific project], [company name], [add metrics], [describe impact]
- Base on ACTUAL CV data where possible - reference their real skills, projects, companies
- Each answer should be 2-3 sentences, professional and detailed
- Vary the confidence level across options (confident → learning)
- Make answers realistic and honest

For answer_tips:
- Provide 2-3 actionable tips for answering the question
- Focus on what makes a strong answer (specifics, metrics, impact)
- Guide without putting words in their mouth

Make questions specific, actionable, and easy to answer with multiple-choice format."""

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
