"""
Prompt templates for CV parsing service.
"""

from langchain.prompts import PromptTemplate

CV_PARSER_PROMPT = PromptTemplate(
    input_variables=["cv_text", "format_instructions"],
    template="""Extract structured information from this CV/Resume:

{cv_text}

{format_instructions}

INSTRUCTIONS:
- Extract ALL information present in the CV
- For dates, use YYYY-MM format when available, otherwise YYYY
- Categorize skills appropriately (technical vs soft skills)
- Set level for each skill based on context (if unclear, use "Intermediate")
- Parse employment dates into startDate/endDate format
- Set currentlyWorking=true for current positions
- Extract hobbies, awards, volunteer work if present
- If information is not present, use null or empty arrays
- Be thorough and accurate
- For skills, use categories like: Programming Languages, Frontend Frameworks, Backend Technologies, Cloud Platforms, DevOps & Tools, Soft Skills, Other
- For language proficiency, use levels: A1, A2, B1, B2, C1, C2, Native

Return the structured data following the format specified above."""
)
