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
    "personal_info": {{
        "name": "string or null",
        "email": "string or null",
        "phone": "string or null",
        "location": "string or null",
        "linkedin": "string or null",
        "github": "string or null",
        "portfolio": "string or null"
    }},
    "professional_summary": "string",
    "skills": {{
        "technical_skills": ["array of strings"],
        "tools": ["array of strings"],
        "soft_skills": ["array of strings"]
    }},
    "experience": [
        {{
            "company": "string",
            "role": "string",
            "duration": "string",
            "location": "string or null",
            "achievements": ["array of strings"]
        }}
    ],
    "education": [
        {{
            "degree": "string",
            "institution": "string",
            "year": "string",
            "gpa": "string or null"
        }}
    ],
    "projects": [
        {{
            "name": "string",
            "description": "string",
            "technologies": ["array of strings"],
            "link": "string or null"
        }}
    ],
    "certifications": ["array of strings"],
    "languages": ["array of strings"],
    "years_of_experience": 0
}}

Extract ALL information present in the CV. Be thorough and accurate."""

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
            "personal_info": {},
            "professional_summary": cv_text[:500],
            "skills": {"technical_skills": [], "tools": [], "soft_skills": []},
            "experience": [],
            "education": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "years_of_experience": 0
        }

def store_cv_embeddings(cv_id: str, cv_parsed: dict) -> str:
    """Generate and store embeddings for different CV sections in Qdrant"""

    # Combine all text for full CV embedding
    full_text = f"""
    Summary: {cv_parsed.get('professional_summary', '')}
    Skills: {', '.join(cv_parsed.get('skills', {}).get('technical_skills', []))}
    Experience: {' '.join([f"{exp.get('role', '')} at {exp.get('company', '')}" for exp in cv_parsed.get('experience', [])])}
    """

    # Generate embedding for full CV
    full_embedding = generate_embedding(full_text)

    # Store in Qdrant
    point_id = store_cv_embedding(
        cv_id=cv_id,
        text=full_text,
        embedding=full_embedding,
        metadata={
            "section": "full",
            "name": cv_parsed.get('personal_info', {}).get('name', 'Unknown'),
            "years_of_experience": cv_parsed.get('years_of_experience', 0)
        }
    )

    return point_id
