"""
Cover Letter Generation Service - Refactored with LangChain
Generates personalized cover letters using AI with RAG context.
"""

import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from app.config import get_settings
from app.schemas.cover_letter_schemas import CoverLetterData
from app.services.embeddings import generate_embedding
from app.services.qdrant_service import get_rag_context_for_cv
from app.services.prompts.cover_letter_prompts import COVER_LETTER_PROMPT

settings = get_settings()


def generate_cover_letter(cv_data: dict, jd_data: dict, answers: dict, optimized_cv: dict, cv_id: str = None) -> dict:
    """
    Generate personalized cover letter using AI with RAG context.

    Args:
        cv_data: Original CV data
        jd_data: Parsed job description data
        answers: User's answers to smart questions
        optimized_cv: Optimized CV data
        cv_id: Optional CV ID for RAG context retrieval

    Returns:
        Cover letter data dictionary
    """

    # Initialize LangChain components
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.4,  # Slightly higher for creative writing
        max_retries=3,
        request_timeout=60,
        google_api_key=settings.GEMINI_API_KEY
    )

    # Create Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=CoverLetterData)

    # Get RAG context from similar successful cover letters
    rag_context = ""
    if cv_id:
        query_text = f"Cover letter for {jd_data.get('position_title', 'position')} at {jd_data.get('company_name', 'company')}"
        query_embedding = generate_embedding(query_text)
        rag_ctx = get_rag_context_for_cv(cv_id, query_text, query_embedding)
        if rag_ctx:
            rag_context = f"BEST PRACTICES FROM SUCCESSFUL COVER LETTERS:\n{rag_ctx}"

    # Format the prompt with actual data
    formatted_prompt = COVER_LETTER_PROMPT.format(
        optimized_cv=json.dumps(optimized_cv, indent=2),
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
        return parsed_data.dict(by_alias=True)

    except Exception as e:
        print(f"Error generating cover letter with Gemini: {e}")
        return {"error": str(e)}


def generate_cover_letter_pdf(cover_letter: dict, output_path: str) -> str:
    """
    Generate PDF from cover letter data using ReportLab.

    Args:
        cover_letter: Cover letter data dictionary
        output_path: Path to save the PDF

    Returns:
        Path to the generated PDF
    """

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
