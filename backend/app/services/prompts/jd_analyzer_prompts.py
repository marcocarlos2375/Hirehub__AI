"""
Prompt templates for Job Description analysis service.
"""

from langchain.prompts import PromptTemplate

JD_ANALYZER_PROMPT = PromptTemplate(
    input_variables=["jd_text", "format_instructions"],
    template="""Analyze this job description and extract all requirements:

{jd_text}

{format_instructions}

INSTRUCTIONS:
- Extract company name, position title, location if mentioned
- Identify work mode (remote/hybrid/onsite)
- Extract salary range if mentioned
- Determine experience level required (junior/mid/senior/lead)
- List all hard skills with priority (critical/important/nice)
- List soft skills required
- Extract key responsibilities
- Identify technology stack mentioned
- Note domain expertise requirements (industry, specific knowledge)
- Identify implicit requirements (things not explicitly stated but implied)
- Note company culture signals from the language used
- Extract important ATS keywords
- Be thorough and extract all available information

Return the structured data following the format specified above."""
)
