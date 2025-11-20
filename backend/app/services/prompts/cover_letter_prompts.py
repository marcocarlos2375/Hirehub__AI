"""
Prompt templates for cover letter generation service.
"""

from langchain.prompts import PromptTemplate

COVER_LETTER_PROMPT = PromptTemplate(
    input_variables=["optimized_cv", "jd_data", "answers", "rag_context", "format_instructions"],
    template="""Generate a professional, compelling cover letter based on:

OPTIMIZED CV DATA (with personalInfo.firstName/lastName, employmentHistory, skills array):
{optimized_cv}

JOB DESCRIPTION:
{jd_data}

USER'S ADDITIONAL ANSWERS:
{answers}

{rag_context}

{format_instructions}

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

Make it specific to the actual job and candidate details."""
)
