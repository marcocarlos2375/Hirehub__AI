import fitz  # PyMuPDF
from docx import Document
import os
import google.generativeai as genai
import json
from app.config import get_settings
from app.services.embeddings import generate_embedding, generate_embeddings_batch
from app.services.qdrant_service import store_cv_embedding

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX"""
    doc = Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

def parse_cv_with_gemini(cv_text: str) -> dict:
    """Use Gemini to structure CV data"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    prompt = f"""Extract structured information from this CV/Resume:

{cv_text}

Return ONLY a valid JSON object (no markdown, no backticks) with this exact structure:
{{
    "personalInfo": {{
        "jobTitle": "string or null - current/desired job title",
        "firstName": "string or null",
        "lastName": "string or null",
        "email": "string or null",
        "phone": "string or null",
        "address": "string or null - full address or city",
        "website": "string or null - personal website URL",
        "birthDate": "string or null - format: DD.MM.YYYY",
        "nationality": "string or null",
        "relationshipStatus": "string or null",
        "availability": "string or null - e.g., '2weeks', 'immediate'",
        "socialLinks": [
            {{
                "type": "string - linkedin/github/twitter/portfolio/other",
                "url": "string - full URL"
            }}
        ]
    }},
    "professionalSummary": "string - professional summary or objective",
    "employmentHistory": [
        {{
            "position": "string - job title",
            "company": "string - company name",
            "location": "string or null - city, state/country",
            "startDate": "string - YYYY-MM format or 'YYYY'",
            "endDate": "string - YYYY-MM format or 'YYYY' or empty if current",
            "currentlyWorking": true or false,
            "description": "string or null - brief job description",
            "responsibilities": ["array of strings - key achievements and responsibilities"]
        }}
    ],
    "education": [
        {{
            "school": "string - institution name",
            "degree": "string - degree type and field",
            "location": "string or null - city, state/country",
            "startDate": "string or null - YYYY-MM format",
            "endDate": "string or null - YYYY-MM format",
            "current": false,
            "description": "string or null - HTML formatted details like GPA, honors"
        }}
    ],
    "skills": [
        {{
            "skill": "string - skill name",
            "level": "string - Beginner/Intermediate/Advanced/Expert",
            "category": "string - Programming Languages/Frontend Frameworks/Backend Technologies/Cloud Platforms/DevOps & Tools/Soft Skills/Other"
        }}
    ],
    "languages": [
        {{
            "language": "string - language name",
            "level": "string - A1/A2/B1/B2/C1/C2/Native"
        }}
    ],
    "courses": [
        {{
            "title": "string - course name",
            "institution": "string - provider/platform",
            "completionDate": "string or null - YYYY-MM format",
            "credential": "string or null - certificate ID or credential"
        }}
    ],
    "publications": [
        {{
            "title": "string - publication title",
            "publisher": "string - where published",
            "publicationDate": "string or null - YYYY-MM format",
            "url": "string or null - link to publication"
        }}
    ],
    "projects": [
        {{
            "name": "string - project name",
            "description": "string - project description",
            "technologies": "string - comma-separated technologies",
            "link": "string or null - project URL"
        }}
    ],
    "references": [
        {{
            "name": "string - reference name",
            "position": "string or null - their job title",
            "company": "string or null - their company",
            "email": "string or null",
            "phone": "string or null"
        }}
    ],
    "hobbies": ["array of strings - hobbies and interests"],
    "internships": [
        {{
            "position": "string - internship title",
            "company": "string - company name",
            "location": "string or null",
            "startDate": "string or null - YYYY-MM format",
            "endDate": "string or null - YYYY-MM format",
            "description": "string or null - what they did"
        }}
    ],
    "customSections": {{
        "awards": [
            {{
                "title": "string - award name",
                "city": "string or null - where received",
                "startDate": "string or null - YYYY-MM format",
                "endDate": "string or null",
                "current": false,
                "description": "string or null - HTML formatted details"
            }}
        ],
        "volunteering": [
            {{
                "title": "string - volunteer role",
                "city": "string or null - location",
                "startDate": "string or null - YYYY-MM format",
                "endDate": "string or null",
                "current": false,
                "description": "string or null - HTML formatted details"
            }}
        ]
    }}
}}

INSTRUCTIONS:
- Extract ALL information present in the CV
- For dates, use YYYY-MM format when available, otherwise YYYY
- Categorize skills appropriately (technical vs soft skills)
- Set level for each skill based on context (if unclear, use "Intermediate")
- Parse employment dates into startDate/endDate format
- Set currentlyWorking=true for current positions
- Extract hobbies, awards, volunteer work if present
- If information is not present, use null or empty arrays
- Be thorough and accurate"""

    generation_config = {
        "temperature": 0.3,
        "response_mime_type": "application/json"
    }

    try:
        response = model.generate_content(prompt, generation_config=generation_config)
        response_text = response.text.strip()

        # Handle potential markdown code blocks
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        parsed_data = json.loads(response_text)
        return parsed_data

    except Exception as e:
        print(f"Error parsing CV with Gemini: {e}")
        return {
            "error": str(e),
            "personalInfo": {
                "jobTitle": None,
                "firstName": None,
                "lastName": None,
                "email": None,
                "phone": None,
                "address": None,
                "website": None,
                "birthDate": None,
                "nationality": None,
                "relationshipStatus": None,
                "availability": None,
                "socialLinks": []
            },
            "professionalSummary": cv_text[:500],
            "employmentHistory": [],
            "education": [],
            "skills": [],
            "languages": [],
            "courses": [],
            "publications": [],
            "projects": [],
            "references": [],
            "hobbies": [],
            "internships": [],
            "customSections": {
                "awards": [],
                "volunteering": []
            }
        }

def store_cv_embeddings(cv_id: str, cv_parsed: dict) -> str:
    """Generate and store embeddings for different CV sections in Qdrant"""

    # Extract skills as text
    skills_list = [s.get('skill', '') for s in cv_parsed.get('skills', [])]
    skills_text = ', '.join(skills_list)

    # Extract employment history as text
    employment_text = ' '.join([
        f"{emp.get('position', '')} at {emp.get('company', '')}"
        for emp in cv_parsed.get('employmentHistory', [])
    ])

    # Calculate years of experience
    employment_history = cv_parsed.get('employmentHistory', [])
    years_of_experience = len(employment_history)  # Simplified calculation

    # Combine all text for full CV embedding
    full_text = f"""
    Summary: {cv_parsed.get('professionalSummary', '')}
    Skills: {skills_text}
    Experience: {employment_text}
    """

    # Generate embedding for full CV
    full_embedding = generate_embedding(full_text)

    # Get full name
    personal_info = cv_parsed.get('personalInfo', {})
    first_name = personal_info.get('firstName', '')
    last_name = personal_info.get('lastName', '')
    full_name = f"{first_name} {last_name}".strip() or 'Unknown'

    # Store in Qdrant
    point_id = store_cv_embedding(
        cv_id=cv_id,
        text=full_text,
        embedding=full_embedding,
        metadata={
            "section": "full",
            "name": full_name,
            "years_of_experience": years_of_experience,
            "job_title": personal_info.get('jobTitle', '')
        }
    )

    return point_id
