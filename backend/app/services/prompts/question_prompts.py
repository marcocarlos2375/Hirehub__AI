"""
Prompt templates for smart question generation service.
"""

from langchain.prompts import PromptTemplate

QUESTION_GEN_PROMPT = PromptTemplate(
    input_variables=["cv_data", "jd_data", "gaps", "rag_context", "format_instructions"],
    template="""Based on these gaps between the CV and job requirements:

CV SUMMARY (with personalInfo, employmentHistory, skills array with levels):
{cv_data}

JOB REQUIREMENTS:
{jd_data}

TOP GAPS:
{gaps}

{rag_context}

{format_instructions}

INSTRUCTIONS:
- CV uses new structure with employmentHistory, skills array, courses, publications
- Consider all CV sections including languages, hobbies, customSections when formulating questions
- Ask about experience that might be in hobbies, volunteering, or side projects
- Generate 5-8 smart questions to uncover hidden experience that could close these gaps

IMPORTANT - For suggested_answers array (provide 3-4 options):
- Generate multiple answer OPTIONS with varying experience levels
- Option 1: Strong/extensive experience - "Yes, I developed X using Y for [mention specific project]. Achieved Z results with A impact."
- Option 2: Moderate experience - "I've used X in [company/project]. Built Y features and learned Z."
- Option 3: Basic/learning - "I have some experience with X through [courses/personal projects]. Familiar with Y concepts."
- Option 4: Alternative angle - Different approach or related experience
- Include helpful placeholders: [mention specific project], [company name], [add metrics], [describe impact]
- Base on ACTUAL CV data where possible - reference their real skills, projects, companies
- Each answer should be 2-3 sentences, professional and detailed
- Vary the confidence level across options (confident → learning)
- Make answers realistic and honest

For answer_tips:
- Provide 2-3 actionable tips for answering the question
- Focus on what makes a strong answer (specifics, metrics, impact)
- Guide without putting words in their mouth

Make questions specific, actionable, and easy to answer with multiple-choice format."""
)
