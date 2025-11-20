import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_interview_prep(cv_data: dict, jd_data: dict, answers: dict, gaps: list, cv_id: str = None) -> dict:
    """Generate comprehensive interview preparation materials"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar interview scenarios
    rag_context = ""
    if cv_id:
        query_text = f"Interview questions for {jd_data.get('position_title', 'position')} with focus on: {', '.join([g.get('gap', '') for g in gaps])}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    prompt = f"""Generate comprehensive interview preparation materials based on:

CV DATA (with personalInfo, employmentHistory, skills array, projects, publications):
{json.dumps(cv_data, indent=2)}

JOB DESCRIPTION:
{json.dumps(jd_data, indent=2)}

USER'S ANSWERS:
{json.dumps(answers, indent=2)}

IDENTIFIED GAPS:
{json.dumps(gaps, indent=2)}

{f"INTERVIEW INSIGHTS FROM SIMILAR ROLES:{chr(10)}{rag_context}" if rag_context else ""}

IMPORTANT - CV STRUCTURE NOTES:
- Use personalInfo.firstName/lastName for candidate name
- employmentHistory contains positions with responsibilities array
- Skills have levels and categories - use this to gauge expertise depth
- May reference courses, publications, hobbies, or customSections (awards, volunteering)
- Projects array contains detailed project information

Create interview preparation materials organized by stages:

**INTERVIEW STAGES:**

Stage 1: Phone Screen (HR/Recruiter) - 30 minutes
- Focus: Background, motivation, logistics, salary expectations
- Who: HR or recruiter

Stage 2: Technical Interview - 60-90 minutes
- Focus: Technical skills, problem-solving, domain expertise
- Who: Engineering manager or senior engineer

Stage 3: Behavioral/Cultural Fit - 45-60 minutes
- Focus: Work style, team collaboration, company values
- Who: Team lead or cross-functional partners

**FOR EACH QUESTION PROVIDE:**
1. Priority level (CRITICAL/HIGH/MEDIUM)
2. Category (gap/technical/behavioral/cultural/project)
3. Why this question matters
4. Answer framework (bullet points using STAR method where appropriate)
5. Sample answer using candidate's ACTUAL experience from CV and answers

**ADDITIONAL SECTIONS:**
1. Company Research (key facts from JD)
2. Smart Questions to Ask Interviewers (5-7 questions)
3. Common Mistakes to Avoid
4. Talking Points for Each Project/Experience

Return ONLY valid JSON (no markdown):
{{
    "interview_stages": [
        {{
            "stage": 1,
            "name": "string - stage name",
            "duration": "string - duration",
            "interviewer": "string - who conducts",
            "focus": "string - what they're evaluating",
            "questions": [
                {{
                    "question": "string - the actual question",
                    "priority": "critical/high/medium",
                    "category": "gap/technical/behavioral/cultural/project",
                    "why_important": "string - why they're asking this",
                    "answer_framework": [
                        "string - bullet point 1",
                        "string - bullet point 2",
                        "string - bullet point 3"
                    ],
                    "sample_answer": "string - full sample answer using candidate's experience",
                    "follow_up_questions": ["array of likely follow-up questions"]
                }}
            ]
        }}
    ],
    "company_research": {{
        "key_facts": ["array of important facts about the company from JD"],
        "values": ["array of company values mentioned or implied"],
        "technical_stack": ["array of technologies they use"],
        "business_model": "string - what the company does",
        "recent_news": "string - mention if anything notable from JD"
    }},
    "questions_to_ask": [
        {{
            "question": "string - question to ask interviewer",
            "when_to_ask": "string - which interview stage",
            "why_ask": "string - what you learn from this"
        }}
    ],
    "common_mistakes": [
        {{
            "mistake": "string - common mistake",
            "why_bad": "string - why this hurts",
            "instead_do": "string - what to do instead"
        }}
    ],
    "project_talking_points": [
        {{
            "project": "string - project name from CV",
            "key_points": ["array of important points to mention"],
            "technical_details": "string - technical depth to prepare",
            "business_impact": "string - how to frame the business value",
            "challenges_overcome": ["array of interesting challenges"]
        }}
    ],
    "gap_mitigation_strategies": [
        {{
            "gap": "string - identified gap",
            "how_to_address": "string - strategy to address in interview",
            "positive_framing": "string - how to frame it positively"
        }}
    ]
}}

Be specific and use the candidate's actual experience. Provide realistic questions they're likely to face. Focus on gaps and how to address them strategically."""

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

        interview_prep = json.loads(response_text)
        return interview_prep

    except Exception as e:
        print(f"Error generating interview prep with Gemini: {e}")
        return {"error": str(e)}
