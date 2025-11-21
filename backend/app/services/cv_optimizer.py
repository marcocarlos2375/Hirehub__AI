import os
import google.generativeai as genai
import json
from app.config import get_settings
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv, get_rag_context_for_jd

settings = get_settings()
genai.configure(api_key=settings.GEMINI_API_KEY)

def optimize_cv(cv_data: dict, jd_data: dict, answers: dict, cv_id: str = None) -> dict:
    """Generate optimized CV using AI with RAG context"""

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    # Get RAG context from similar successful CVs
    rag_context = ""
    if cv_id:
        query_text = f"Optimize CV for {jd_data.get('position_title', 'position')}"
        query_embedding = generate_embedding(query_text)
        rag_context = get_rag_context_for_cv(cv_id, query_text, query_embedding)

    rag_section = ""
    if rag_context:
        rag_section = f"BEST PRACTICES FROM SIMILAR SUCCESSFUL CVS:\n{rag_context}\n\n"

    prompt = f"""Optimize this CV for the job description, incorporating user's answers:

ORIGINAL CV:
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

USER'S ADDITIONAL INFORMATION (from questions):
{json.dumps(answers, indent=2)}

{rag_section}INSTRUCTIONS:
1. Rewrite professional summary to emphasize alignment with job
2. Reorder and reframe experience bullets to highlight relevant work
3. Add skills uncovered from user answers
4. Use keywords from job description naturally
5. Quantify achievements where possible
6. Use action verbs (architected, led, optimized, delivered)

CRITICAL RULES:
- DO NOT fabricate experience
- Only use information from CV + user answers
- Reframe truthfully, don't invent
- Keep professional tone
- Maintain same JSON structure as input

Return optimized CV in same JSON structure as the original CV."""

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

        optimized = json.loads(response_text)
        return optimized

    except Exception as e:
        print(f"Error optimizing CV with Gemini: {e}")
        return cv_data

def generate_cv_pdf(cv_data: dict, output_path: str) -> str:
    """Generate PDF from CV data using ReportLab"""

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#1a1a1a',
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2563eb',
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    # Name
    name = cv_data.get('personal_info', {}).get('name', 'Your Name')
    story.append(Paragraph(name, title_style))
    story.append(Spacer(1, 0.1*inch))

    # Contact info
    contact_parts = []
    pi = cv_data.get('personal_info', {})
    if pi.get('email'):
        contact_parts.append(pi['email'])
    if pi.get('phone'):
        contact_parts.append(pi['phone'])
    if pi.get('location'):
        contact_parts.append(pi['location'])

    if contact_parts:
        contact_text = ' | '.join(contact_parts)
        story.append(Paragraph(contact_text, styles['Normal']))

    # Links
    link_parts = []
    if pi.get('linkedin'):
        link_parts.append(f"LinkedIn: {pi['linkedin']}")
    if pi.get('github'):
        link_parts.append(f"GitHub: {pi['github']}")
    if pi.get('portfolio'):
        link_parts.append(f"Portfolio: {pi['portfolio']}")

    if link_parts:
        link_text = ' | '.join(link_parts)
        story.append(Paragraph(link_text, styles['Normal']))

    story.append(Spacer(1, 0.2*inch))

    # Professional Summary
    if cv_data.get('professional_summary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(cv_data['professional_summary'], styles['Normal']))
        story.append(Spacer(1, 0.15*inch))

    # Skills
    if cv_data.get('skills'):
        story.append(Paragraph("SKILLS", heading_style))
        skills = cv_data['skills']

        if skills.get('technical_skills'):
            tech_skills = ', '.join(skills['technical_skills'])
            story.append(Paragraph(f"<b>Technical:</b> {tech_skills}", styles['Normal']))

        if skills.get('tools'):
            tools = ', '.join(skills['tools'])
            story.append(Paragraph(f"<b>Tools:</b> {tools}", styles['Normal']))

        story.append(Spacer(1, 0.15*inch))

    # Experience
    if cv_data.get('experience'):
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))

        for exp in cv_data['experience']:
            # Company and role
            title = f"<b>{exp.get('role', 'Role')}</b> — {exp.get('company', 'Company')}"
            story.append(Paragraph(title, styles['Normal']))

            # Duration and location
            duration_location = []
            if exp.get('duration'):
                duration_location.append(exp['duration'])
            if exp.get('location'):
                duration_location.append(exp['location'])

            if duration_location:
                story.append(Paragraph(' | '.join(duration_location), styles['Normal']))

            story.append(Spacer(1, 0.05*inch))

            # Achievements
            if exp.get('achievements'):
                for achievement in exp['achievements']:
                    story.append(Paragraph(f"• {achievement}", styles['Normal']))

            story.append(Spacer(1, 0.1*inch))

    # Education
    if cv_data.get('education'):
        story.append(Paragraph("EDUCATION", heading_style))

        for edu in cv_data['education']:
            degree_text = f"<b>{edu.get('degree', '')}</b> — {edu.get('institution', '')}"
            if edu.get('year'):
                degree_text += f" ({edu['year']})"
            if edu.get('gpa'):
                degree_text += f" | GPA: {edu['gpa']}"

            story.append(Paragraph(degree_text, styles['Normal']))
            story.append(Spacer(1, 0.05*inch))

    # Projects
    if cv_data.get('projects'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("PROJECTS", heading_style))

        for proj in cv_data['projects']:
            proj_title = f"<b>{proj.get('name', 'Project')}</b>"
            if proj.get('technologies'):
                tech = ', '.join(proj['technologies'])
                proj_title += f" ({tech})"

            story.append(Paragraph(proj_title, styles['Normal']))

            if proj.get('description'):
                story.append(Paragraph(proj['description'], styles['Normal']))

            if proj.get('link'):
                story.append(Paragraph(f"Link: {proj['link']}", styles['Normal']))

            story.append(Spacer(1, 0.08*inch))

    # Build PDF
    doc.build(story)
    return output_path
