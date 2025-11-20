import os
import google.generativeai as genai
import json
from datetime import datetime
from app.config import get_settings
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_cover_letter(cv_data: dict, jd_data: dict, answers: dict, optimized_cv: dict, cv_id: str = None) -> dict:
    """Generate personalized cover letter using AI with RAG context"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar successful cover letters
    rag_context = ""
    if cv_id:
        query_text = f"Cover letter for {jd_data.get('position_title', 'position')} at {jd_data.get('company_name', 'company')}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    prompt = f"""Generate a professional, compelling cover letter based on:

OPTIMIZED CV DATA (with personalInfo.firstName/lastName, employmentHistory, skills array):
{json.dumps(optimized_cv, indent=2)}

JOB DESCRIPTION:
{json.dumps(jd_data, indent=2)}

USER'S ADDITIONAL ANSWERS:
{json.dumps(answers, indent=2)}

{f"BEST PRACTICES FROM SUCCESSFUL COVER LETTERS:{chr(10)}{rag_context}" if rag_context else ""}

IMPORTANT - CV STRUCTURE NOTES:
- Use personalInfo.firstName and personalInfo.lastName for the candidate's name
- Reference employmentHistory for work experience (position, company, startDate, endDate)
- Skills are in array format with skill, level, and category
- May include courses, publications, hobbies that can be mentioned

INSTRUCTIONS:
1. Create a personalized cover letter that demonstrates genuine enthusiasm for the role and company
2. Address why the candidate is excited about THIS specific company (use details from JD)
3. Highlight 3-4 key areas where candidate brings value, with specific evidence from their experience
4. Address any logistics or concerns (relocation, work mode, experience gaps) proactively and positively
5. Show what the candidate is seeking in their next role and why this position aligns
6. Include a strong closing that invites further conversation
7. Optional: Add a P.S. with an interesting hook or additional detail

STYLE GUIDELINES:
- Professional but conversational tone
- Specific examples over generic claims
- Show enthusiasm without being over-the-top
- Address gaps strategically (frame positively)
- Use product-minded language and business impact focus
- 1-2 pages maximum
- Avoid clichés and generic phrases

Return ONLY valid JSON (no markdown):
{{
    "personal_info": {{
        "name": "string",
        "email": "string",
        "phone": "string",
        "location": "string"
    }},
    "date": "string (e.g., 'December 15, 2024')",
    "company_info": {{
        "hiring_team": "string (e.g., 'Hiring Team' or specific name)",
        "company_name": "string",
        "company_location": "string"
    }},
    "position_title": "string",
    "content": {{
        "opening": "string - engaging opening paragraph showing excitement",
        "why_company": "string - specific reasons excited about THIS company",
        "what_brings": [
            "string - first key strength with evidence",
            "string - second key strength with evidence",
            "string - third key strength with evidence"
        ],
        "addressing_concerns": "string - proactively address logistics/gaps",
        "seeking": "string - what candidate wants in next role and why this fits",
        "closing": "string - strong closing inviting conversation",
        "ps": "string or null - optional interesting hook"
    }},
    "full_text": "string - complete formatted cover letter ready for copy/paste"
}}

Make it specific to the actual job and candidate details."""

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

        cover_letter = json.loads(response_text)
        return cover_letter

    except Exception as e:
        print(f"Error generating cover letter with Gemini: {e}")
        return {"error": str(e)}

def generate_cover_letter_pdf(cover_letter: dict, output_path: str) -> str:
    """Generate PDF from cover letter data using ReportLab"""

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=1*inch, rightMargin=1*inch)

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#1a1a1a',
        spaceAfter=4,
        fontName='Helvetica'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#1a1a1a',
        spaceAfter=10,
        leading=14,
        fontName='Helvetica'
    )

    # Personal Info
    pi = cover_letter.get('personal_info', {})
    story.append(Paragraph(pi.get('name', ''), header_style))
    story.append(Paragraph(pi.get('email', ''), header_style))
    story.append(Paragraph(pi.get('phone', ''), header_style))
    story.append(Paragraph(pi.get('location', ''), header_style))
    story.append(Spacer(1, 0.2*inch))

    # Date
    story.append(Paragraph(cover_letter.get('date', datetime.now().strftime('%B %d, %Y')), header_style))
    story.append(Spacer(1, 0.2*inch))

    # Company Info
    ci = cover_letter.get('company_info', {})
    story.append(Paragraph(ci.get('hiring_team', 'Hiring Team'), header_style))
    story.append(Paragraph(ci.get('company_name', ''), header_style))
    story.append(Paragraph(ci.get('company_location', ''), header_style))
    story.append(Spacer(1, 0.2*inch))

    # RE: Position
    story.append(Paragraph(f"<b>RE: {cover_letter.get('position_title', '')}</b>", header_style))
    story.append(Spacer(1, 0.2*inch))

    # Salutation
    story.append(Paragraph(f"Dear {ci.get('hiring_team', 'Hiring Team')},", body_style))
    story.append(Spacer(1, 0.1*inch))

    # Use full_text if available, otherwise construct from parts
    if cover_letter.get('full_text'):
        # Split by paragraphs and add each
        paragraphs = cover_letter['full_text'].split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
    else:
        # Construct from content parts
        content = cover_letter.get('content', {})

        if content.get('opening'):
            story.append(Paragraph(content['opening'], body_style))

        if content.get('why_company'):
            story.append(Paragraph(content['why_company'], body_style))

        if content.get('what_brings'):
            for item in content['what_brings']:
                story.append(Paragraph(item, body_style))

        if content.get('addressing_concerns'):
            story.append(Paragraph(content['addressing_concerns'], body_style))

        if content.get('seeking'):
            story.append(Paragraph(content['seeking'], body_style))

        if content.get('closing'):
            story.append(Paragraph(content['closing'], body_style))

        if content.get('ps'):
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<i>P.S. {content['ps']}</i>", body_style))

    # Signature
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Sincerely,", body_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(pi.get('name', ''), body_style))

    # Build PDF
    doc.build(story)
    return output_path
