import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv, get_rag_context_for_jd

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_interview_prep(
    cv_data: dict,
    jd_data: dict,
    optimized_cv: dict,
    answers: dict,
    cv_id: str = None
) -> dict:
    """Generate comprehensive interview preparation guide"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar successful interviews
    rag_context = ""
    if cv_id:
        query_text = f"Interview prep for {jd_data.get('position_title', 'position')}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    rag_section = ""
    if rag_context:
        rag_section = f"INSIGHTS FROM SIMILAR SUCCESSFUL INTERVIEWS:\n{rag_context}\n\n"

    prompt = f"""Create a comprehensive interview preparation guide for this candidate:

CANDIDATE PROFILE (OPTIMIZED):
{json.dumps(optimized_cv, indent=2)}

JOB DESCRIPTION:
{json.dumps(jd_data, indent=2)}

ADDITIONAL CONTEXT:
{json.dumps(answers, indent=2)}

{rag_section}Generate interview prep covering:
1. Phone Screen (30 min) - HR/Recruiter questions
2. Technical Round (60-90 min) - Engineers questions
3. Behavioral Round (45-60 min) - STAR method questions
4. Final Round (30-45 min) - Leadership/Culture fit

For each question, provide:
- The likely question
- A suggested answer based on candidate's actual experience
- Tips for delivering the answer well

Return JSON:
""" + """{
    "stages": [
        {
            "stage_name": "Phone Screen",
            "duration": "30 minutes",
            "interviewer": "HR/Recruiter",
            "focus": "Culture fit, basic qualifications",
            "questions": [
                {
                    "question": "string - the actual question",
                    "category": "motivation/experience/culture/logistics",
                    "priority": "critical/high/medium",
                    "suggested_answer": "string - answer using candidate's real experience",
                    "tips": ["array of tips for answering well"],
                    "why_they_ask": "string - what they're really evaluating"
                }
            ]
        }
    ],
    "technical_deep_dives": [
        {
            "topic": "string - e.g., 'React Performance Optimization'",
            "likely_questions": ["array of specific technical questions"],
            "preparation_tips": ["array of how to prepare"],
            "example_projects_to_mention": ["projects from CV"]
        }
    ],
    "star_method_examples": [
        {
            "situation": "string - specific example from candidate's experience",
            "task": "string - what needed to be done",
            "action": "string - what candidate did",
            "result": "string - quantified outcome",
            "applicable_to": ["array of question types this answers"]
        }
    ],
    "red_flags_to_address": [
        {
            "concern": "string - potential concern (e.g., experience gap)",
            "how_to_address": "string - proactive framing",
            "example_response": "string"
        }
    ],
    "questions_to_ask_them": [
        {
            "question": "string",
            "category": "team/tech/growth/culture",
            "why_ask": "string - shows you're interested in..."
        }
    ],
    "general_tips": ["array of overall interview tips"]
}

Base ALL answers on the candidate's ACTUAL experience from their CV. Be specific and authentic."""

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

        interview_prep = json.loads(response_text)
        return interview_prep

    except Exception as e:
        print(f"Error generating interview prep with Gemini: {e}")
        return {
            "error": str(e),
            "stages": [],
            "technical_deep_dives": [],
            "star_method_examples": [],
            "red_flags_to_address": [],
            "questions_to_ask_them": [],
            "general_tips": []
        }
