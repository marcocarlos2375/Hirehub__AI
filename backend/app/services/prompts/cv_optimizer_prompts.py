"""
Prompt templates for CV optimization service.
"""

from langchain.prompts import PromptTemplate

CV_OPTIMIZER_PROMPT = PromptTemplate(
    input_variables=["cv_data", "jd_data", "answers", "rag_context", "format_instructions"],
    template="""Optimize this CV for the job description, incorporating user's answers:

ORIGINAL CV:
{cv_data}

JOB REQUIREMENTS:
{jd_data}

USER'S ADDITIONAL INFORMATION (from questions):
{answers}

{rag_context}

{format_instructions}

INSTRUCTIONS:
1. Rewrite professional summary to emphasize alignment with job
2. Reorder and reframe experience bullets to highlight relevant work
3. Add skills uncovered from user answers
4. Use keywords from job description naturally
5. Quantify achievements where possible
6. Use action verbs (architected, led, optimized, delivered)

CRITICAL RULES:
- DO NOT fabricate experience
- Only use information from ORIGINAL CV and USER ANSWERS
- Reframe existing experiences to emphasize relevance
- Add context to vague bullets using user answers
- Keep all dates, companies, positions accurate
- Use personalInfo.firstName/lastName from original CV
- Maintain array format for skills, employmentHistory, education
- Include ALL sections from original (courses, publications, languages, etc.)

OPTIMIZATION STRATEGIES:
- Mirror job description language where truthful
- Move most relevant experience to top of bullets
- Add metrics and impact where user provided them
- Highlight transferable skills
- Address gaps proactively by reframing related experience
- Use strong action verbs consistently

Return a fully optimized CV with the same structure as the input, but with enhanced content."""
)
