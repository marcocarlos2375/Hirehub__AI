"""
CV Optimizer Service - Refactored with LangChain
Optimizes CV content for specific job descriptions using AI with RAG context.
"""

import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from app.config import get_settings
from app.schemas.cv_schemas import CVData
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv

settings = get_settings()


def optimize_cv(cv_data: dict, jd_data: dict, answers: dict, cv_id: str = None) -> dict:
    """
    Generate optimized CV using AI with RAG context.

    Args:
        cv_data: Original CV data
        jd_data: Parsed job description data
        answers: User's answers to smart questions
        cv_id: Optional CV ID for RAG context

    Returns:
        Optimized CV data dictionary
    """

    # Initialize LangChain components
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.4,  # Slightly higher for creative rewriting
        max_retries=3,
        request_timeout=60,
        google_api_key=settings.GEMINI_API_KEY
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=CVData)

    # Get RAG context from similar successful CVs
    rag_context = ""
    if cv_id:
        query_text = f"Optimize CV for {jd_data.get('position_title', 'position')}"
        query_embedding = generate_embedding(query_text)
        rag_ctx = get_rag_context_for_cv(cv_id, query_text, query_embedding)
        if rag_ctx:
            rag_context = f"BEST PRACTICES FROM SIMILAR SUCCESSFUL CVS:\n{rag_ctx}"

    # Format the prompt with actual data
    from app.services.prompts.cv_optimizer_prompts import CV_OPTIMIZER_PROMPT

    formatted_prompt = CV_OPTIMIZER_PROMPT.format(
        cv_data=json.dumps(cv_data, indent=2),
        jd_data=json.dumps(jd_data, indent=2),
        answers=json.dumps(answers, indent=2),
        rag_context=rag_context,
        format_instructions=parser.get_format_instructions()
    )

    try:
        # Call Gemini with automatic retry logic
        response = llm.invoke(formatted_prompt)

        # Parse and validate response with Pydantic
        parsed_data = parser.parse(response.content)

        # Convert to dict for compatibility
        return parsed_data.dict()

    except Exception as e:
        print(f"Error optimizing CV with Gemini: {e}")
        # Return original CV on error
        return cv_data


def generate_cv_pdf(cv_data: dict, output_path: str) -> str:
    """
    Generate PDF from optimized CV data using ReportLab.
    This function is UNCHANGED from the original - preserves all PDF generation logic.

    Args:
        cv_data: Optimized CV data dictionary
        output_path: Path to save the PDF

    Returns:
        Path to the generated PDF
    """

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor='#2563eb',
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2563eb',
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    subheader_style = ParagraphStyle(
        'SubheaderStyle',
        parent=styles['Heading3'],
        fontSize=11,
        textColor='#1a1a1a',
        spaceAfter=4,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#374151',
        spaceAfter=6,
        leading=12,
        fontName='Helvetica'
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#6b7280',
        spaceAfter=2,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    # Personal Info Header
    pi = cv_data.get('personalInfo', {})
    full_name = f"{pi.get('firstName', '')} {pi.get('lastName', '')}".strip()
    if full_name:
        story.append(Paragraph(full_name, name_style))

    if pi.get('jobTitle'):
        story.append(Paragraph(pi['jobTitle'], contact_style))

    contact_parts = []
    if pi.get('email'):
        contact_parts.append(pi['email'])
    if pi.get('phone'):
        contact_parts.append(pi['phone'])
    if pi.get('address'):
        contact_parts.append(pi['address'])

    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), contact_style))

    story.append(Spacer(1, 0.2*inch))

    # Professional Summary
    if cv_data.get('professionalSummary'):
        story.append(Paragraph("PROFESSIONAL SUMMARY", header_style))
        story.append(Paragraph(cv_data['professionalSummary'], body_style))
        story.append(Spacer(1, 0.1*inch))

    # Employment History
    employment = cv_data.get('employmentHistory', [])
    if employment:
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", header_style))

        for job in employment:
            # Job title and company
            job_title = f"<b>{job.get('position', '')}</b> | {job.get('company', '')}"
            if job.get('location'):
                job_title += f" | {job['location']}"
            story.append(Paragraph(job_title, subheader_style))

            # Dates
            dates = f"{job.get('startDate', '')} - "
            dates += "Present" if job.get('currentlyWorking') else job.get('endDate', '')
            story.append(Paragraph(f"<i>{dates}</i>", body_style))

            # Responsibilities
            for resp in job.get('responsibilities', []):
                story.append(Paragraph(f"• {resp}", body_style))

            story.append(Spacer(1, 0.1*inch))

    # Skills
    skills = cv_data.get('skills', [])
    if skills:
        story.append(Paragraph("SKILLS", header_style))

        # Group skills by category
        skills_by_category = {}
        for skill in skills:
            category = skill.get('category', 'Other')
            if category not in skills_by_category:
                skills_by_category[category] = []
            skill_text = skill.get('skill', '')
            if skill.get('level'):
                skill_text += f" ({skill['level']})"
            skills_by_category[category].append(skill_text)

        for category, skill_list in skills_by_category.items():
            story.append(Paragraph(f"<b>{category}:</b> {', '.join(skill_list)}", body_style))

        story.append(Spacer(1, 0.1*inch))

    # Education
    education = cv_data.get('education', [])
    if education:
        story.append(Paragraph("EDUCATION", header_style))

        for edu in education:
            edu_text = f"<b>{edu.get('degree', '')}</b> | {edu.get('school', '')}"
            if edu.get('location'):
                edu_text += f" | {edu['location']}"
            story.append(Paragraph(edu_text, subheader_style))

            dates = f"{edu.get('startDate', '')} - "
            dates += "Present" if edu.get('current') else edu.get('endDate', '')
            if dates.strip() != " - ":
                story.append(Paragraph(f"<i>{dates}</i>", body_style))

            if edu.get('description'):
                story.append(Paragraph(edu['description'], body_style))

            story.append(Spacer(1, 0.05*inch))

        story.append(Spacer(1, 0.1*inch))

    # Projects
    projects = cv_data.get('projects', [])
    if projects:
        story.append(Paragraph("PROJECTS", header_style))

        for project in projects:
            story.append(Paragraph(f"<b>{project.get('name', '')}</b>", subheader_style))
            if project.get('description'):
                story.append(Paragraph(project['description'], body_style))
            if project.get('technologies'):
                tech_str = project['technologies']
                if isinstance(tech_str, list):
                    tech_str = ', '.join(tech_str)
                story.append(Paragraph(f"<i>Technologies: {tech_str}</i>", body_style))
            story.append(Spacer(1, 0.05*inch))

        story.append(Spacer(1, 0.1*inch))

    # Certifications/Courses
    courses = cv_data.get('courses', [])
    if courses:
        story.append(Paragraph("CERTIFICATIONS & COURSES", header_style))

        for course in courses:
            course_text = f"<b>{course.get('title', '')}</b>"
            if course.get('institution'):
                course_text += f" - {course['institution']}"
            if course.get('completionDate'):
                course_text += f" ({course['completionDate']})"
            story.append(Paragraph(course_text, body_style))

        story.append(Spacer(1, 0.1*inch))

    # Languages
    languages = cv_data.get('languages', [])
    if languages:
        story.append(Paragraph("LANGUAGES", header_style))

        lang_list = []
        for lang in languages:
            lang_text = lang.get('language', '')
            if lang.get('level'):
                lang_text += f" ({lang['level']})"
            lang_list.append(lang_text)

        story.append(Paragraph(", ".join(lang_list), body_style))
        story.append(Spacer(1, 0.1*inch))

    # Build PDF
    doc.build(story)
    return output_path
