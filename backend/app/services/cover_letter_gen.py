import os
import google.generativeai as genai
import json
from app.config import get_settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_cover_letter(
    cv_data: dict,
    jd_data: dict,
    answers: dict,
    optimized_cv: dict,
    cv_id: str = None
) -> dict:
    """Generate personalized cover letter using AI with RAG context"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar successful cover letters
    rag_context = ""
    if cv_id:
        query_text = f"Cover letter for {jd_data.get('position_title', 'position')} at {jd_data.get('company_name', 'company')}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    prompt = f"""Write a compelling, professional cover letter for this job application:

OPTIMIZED CV:
{json.dumps(optimized_cv, indent=2)}

JOB DESCRIPTION:
{json.dumps(jd_data, indent=2)}

USER'S ADDITIONAL CONTEXT (from questions):
{json.dumps(answers, indent=2)}

{f"BEST PRACTICES FROM SUCCESSFUL COVER LETTERS:\n{rag_context}" if rag_context else ""}

INSTRUCTIONS:
1. Opening: Strong hook that shows enthusiasm and alignment with company mission
2. Body Paragraph 1: Highlight 2-3 most relevant experiences/achievements
3. Body Paragraph 2: Show understanding of company/role + why you're excited
4. Body Paragraph 3: Address any gaps proactively (if applicable)
5. Closing: Clear call-to-action and availability

CRITICAL RULES:
- Professional but warm tone
- Specific examples from CV
- Show genuine interest in company/role
- Address hiring manager (use "Dear Hiring Manager" if unknown)
- Keep to 3-4 paragraphs
- No generic templates - be specific and personal
- Use keywords from job description naturally

Return JSON with this structure:
{{
    "opening_paragraph": "string",
    "body_paragraph_1": "string",
    "body_paragraph_2": "string",
    "body_paragraph_3": "string or null",
    "closing_paragraph": "string",
    "signature": {{
        "name": "string",
        "email": "string",
        "phone": "string",
        "location": "string"
    }}
}}"""

    generation_config = {
        "temperature": 0.5,
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
        return {
            "error": str(e),
            "opening_paragraph": "I am writing to express my interest in this position.",
            "body_paragraph_1": "Based on my experience, I believe I would be a strong fit.",
            "body_paragraph_2": "I am excited about this opportunity.",
            "closing_paragraph": "Thank you for considering my application.",
            "signature": cv_data.get('personal_info', {})
        }

def generate_cover_letter_pdf(cover_letter: dict, cv_data: dict, jd_data: dict, output_path: str) -> str:
    """Generate professional cover letter PDF"""

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )

    # Signature info
    signature = cover_letter.get('signature', cv_data.get('personal_info', {}))

    # Your Info (top right)
    your_info = []
    if signature.get('name'):
        your_info.append(signature['name'])
    if signature.get('email'):
        your_info.append(signature['email'])
    if signature.get('phone'):
        your_info.append(signature['phone'])
    if signature.get('location'):
        your_info.append(signature['location'])

    for info in your_info:
        story.append(Paragraph(info, normal_style))

    story.append(Spacer(1, 0.3*inch))

    # Date
    from datetime import datetime
    today = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(today, normal_style))
    story.append(Spacer(1, 0.2*inch))

    # Company Info
    if jd_data.get('company_name'):
        story.append(Paragraph(f"Hiring Team", normal_style))
        story.append(Paragraph(jd_data['company_name'], normal_style))
        if jd_data.get('location'):
            story.append(Paragraph(jd_data['location'], normal_style))

    story.append(Spacer(1, 0.2*inch))

    # Position
    if jd_data.get('position_title'):
        story.append(Paragraph(f"<b>RE: {jd_data['position_title']} Position</b>", normal_style))

    story.append(Spacer(1, 0.2*inch))

    # Greeting
    story.append(Paragraph("Dear Hiring Manager,", normal_style))
    story.append(Spacer(1, 0.1*inch))

    # Opening paragraph
    if cover_letter.get('opening_paragraph'):
        story.append(Paragraph(cover_letter['opening_paragraph'], normal_style))

    # Body paragraphs
    if cover_letter.get('body_paragraph_1'):
        story.append(Paragraph(cover_letter['body_paragraph_1'], normal_style))

    if cover_letter.get('body_paragraph_2'):
        story.append(Paragraph(cover_letter['body_paragraph_2'], normal_style))

    if cover_letter.get('body_paragraph_3'):
        story.append(Paragraph(cover_letter['body_paragraph_3'], normal_style))

    # Closing paragraph
    if cover_letter.get('closing_paragraph'):
        story.append(Paragraph(cover_letter['closing_paragraph'], normal_style))

    story.append(Spacer(1, 0.2*inch))

    # Signature
    story.append(Paragraph("Best regards,", normal_style))
    story.append(Spacer(1, 0.1*inch))
    if signature.get('name'):
        story.append(Paragraph(f"<b>{signature['name']}</b>", normal_style))

    # Build PDF
    doc.build(story)
    return output_path
