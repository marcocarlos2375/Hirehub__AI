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

    prompt = f"""Optimize this CV for the job description, incorporating user's answers:

ORIGINAL CV:
{json.dumps(cv_data, indent=2)}

JOB REQUIREMENTS:
{json.dumps(jd_data, indent=2)}

USER'S ADDITIONAL INFORMATION (from questions):
{json.dumps(answers, indent=2)}

{f"BEST PRACTICES FROM SIMILAR SUCCESSFUL CVS:{chr(10)}{rag_context}" if rag_context else ""}

INSTRUCTIONS:
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

    # Name and Job Title
    pi = cv_data.get('personalInfo', {})
    first_name = pi.get('firstName', '')
    last_name = pi.get('lastName', '')
    name = f"{first_name} {last_name}".strip() or 'Your Name'
    story.append(Paragraph(name, title_style))

    # Job Title
    if pi.get('jobTitle'):
        job_title_style = ParagraphStyle(
            'JobTitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor='#4b5563',
            alignment=TA_CENTER,
            spaceAfter=6
        )
        story.append(Paragraph(pi['jobTitle'], job_title_style))

    story.append(Spacer(1, 0.1*inch))

    # Contact info
    contact_parts = []
    if pi.get('email'):
        contact_parts.append(pi['email'])
    if pi.get('phone'):
        contact_parts.append(pi['phone'])
    if pi.get('address'):
        contact_parts.append(pi['address'])

    if contact_parts:
        contact_text = ' | '.join(contact_parts)
        story.append(Paragraph(contact_text, styles['Normal']))

    # Social Links
    link_parts = []
    for link in pi.get('socialLinks', []):
        link_type = link.get('type', '').capitalize()
        link_url = link.get('url', '')
        if link_url:
            link_parts.append(f"{link_type}: {link_url}")

    if link_parts:
        link_text = ' | '.join(link_parts)
        story.append(Paragraph(link_text, styles['Normal']))

    story.append(Spacer(1, 0.2*inch))

    # Professional Summary
    if cv_data.get('professionalSummary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
        story.append(Paragraph(cv_data['professionalSummary'], styles['Normal']))
        story.append(Spacer(1, 0.15*inch))

    # Skills
    if cv_data.get('skills'):
        story.append(Paragraph("SKILLS", heading_style))
        skills_by_category = {}

        # Group skills by category
        for skill in cv_data['skills']:
            category = skill.get('category', 'Other')
            if category not in skills_by_category:
                skills_by_category[category] = []
            skill_name = skill.get('skill', '')
            skill_level = skill.get('level', '')
            # Optionally show level: {skill_name} ({skill_level})
            skills_by_category[category].append(skill_name)

        # Display skills by category
        for category, skill_list in skills_by_category.items():
            if skill_list:
                skills_text = ', '.join(skill_list)
                story.append(Paragraph(f"<b>{category}:</b> {skills_text}", styles['Normal']))

        story.append(Spacer(1, 0.15*inch))

    # Employment History
    if cv_data.get('employmentHistory'):
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", heading_style))

        for emp in cv_data['employmentHistory']:
            # Position and company
            title = f"<b>{emp.get('position', 'Position')}</b> — {emp.get('company', 'Company')}"
            story.append(Paragraph(title, styles['Normal']))

            # Duration and location
            duration_location = []
            start_date = emp.get('startDate', '')
            end_date = emp.get('endDate', '')
            currently_working = emp.get('currentlyWorking', False)

            if start_date:
                if currently_working or not end_date:
                    duration_location.append(f"{start_date} - Present")
                else:
                    duration_location.append(f"{start_date} - {end_date}")

            if emp.get('location'):
                duration_location.append(emp['location'])

            if duration_location:
                story.append(Paragraph(' | '.join(duration_location), styles['Normal']))

            story.append(Spacer(1, 0.05*inch))

            # Responsibilities
            if emp.get('responsibilities'):
                for responsibility in emp['responsibilities']:
                    story.append(Paragraph(f"• {responsibility}", styles['Normal']))

            story.append(Spacer(1, 0.1*inch))

    # Education
    if cv_data.get('education'):
        story.append(Paragraph("EDUCATION", heading_style))

        for edu in cv_data['education']:
            degree_text = f"<b>{edu.get('degree', '')}</b> — {edu.get('school', '')}"

            # Add dates if available
            start_date = edu.get('startDate', '')
            end_date = edu.get('endDate', '')
            if start_date or end_date:
                if edu.get('current'):
                    degree_text += f" ({start_date} - Present)"
                elif end_date:
                    degree_text += f" ({end_date})"

            story.append(Paragraph(degree_text, styles['Normal']))

            # Add description (GPA, honors, etc.)
            if edu.get('description'):
                story.append(Paragraph(edu['description'], styles['Normal']))

            story.append(Spacer(1, 0.05*inch))

    # Languages
    if cv_data.get('languages'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("LANGUAGES", heading_style))

        lang_list = [f"{lang.get('language', '')} ({lang.get('level', '')})"
                     for lang in cv_data['languages']]
        if lang_list:
            story.append(Paragraph(', '.join(lang_list), styles['Normal']))

        story.append(Spacer(1, 0.1*inch))

    # Projects
    if cv_data.get('projects'):
        story.append(Paragraph("PROJECTS", heading_style))

        for proj in cv_data['projects']:
            proj_title = f"<b>{proj.get('name', 'Project')}</b>"
            if proj.get('technologies'):
                proj_title += f" ({proj['technologies']})"

            story.append(Paragraph(proj_title, styles['Normal']))

            if proj.get('description'):
                story.append(Paragraph(proj['description'], styles['Normal']))

            if proj.get('link'):
                story.append(Paragraph(f"Link: {proj['link']}", styles['Normal']))

            story.append(Spacer(1, 0.08*inch))

    # Courses/Certifications
    if cv_data.get('courses'):
        story.append(Paragraph("CERTIFICATIONS & COURSES", heading_style))

        for course in cv_data['courses']:
            course_text = f"<b>{course.get('title', '')}</b> — {course.get('institution', '')}"
            if course.get('completionDate'):
                course_text += f" ({course['completionDate']})"

            story.append(Paragraph(course_text, styles['Normal']))

            if course.get('credential'):
                story.append(Paragraph(f"Credential: {course['credential']}", styles['Normal']))

            story.append(Spacer(1, 0.05*inch))

    # Publications
    if cv_data.get('publications'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("PUBLICATIONS", heading_style))

        for pub in cv_data['publications']:
            pub_text = f"<b>{pub.get('title', '')}</b>"
            if pub.get('publisher'):
                pub_text += f" — {pub['publisher']}"
            if pub.get('publicationDate'):
                pub_text += f" ({pub['publicationDate']})"

            story.append(Paragraph(pub_text, styles['Normal']))

            if pub.get('url'):
                story.append(Paragraph(f"URL: {pub['url']}", styles['Normal']))

            story.append(Spacer(1, 0.05*inch))

    # Hobbies
    if cv_data.get('hobbies'):
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph("INTERESTS & HOBBIES", heading_style))
        hobbies_text = ', '.join(cv_data['hobbies'])
        story.append(Paragraph(hobbies_text, styles['Normal']))

    # Build PDF
    doc.build(story)
    return output_path
