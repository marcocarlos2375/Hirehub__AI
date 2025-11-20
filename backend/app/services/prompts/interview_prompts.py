"""
Prompt templates for interview preparation service.
"""

from langchain.prompts import PromptTemplate

INTERVIEW_PREP_PROMPT = PromptTemplate(
    input_variables=["cv_data", "jd_data", "answers", "gaps", "rag_context", "format_instructions"],
    template="""Generate comprehensive interview preparation materials based on:

CV DATA (with personalInfo, employmentHistory, skills array, projects, publications):
{cv_data}

JOB DESCRIPTION:
{jd_data}

USER'S ANSWERS:
{answers}

IDENTIFIED GAPS:
{gaps}

{rag_context}

{format_instructions}

IMPORTANT - CV STRUCTURE NOTES:
- Use personalInfo.firstName/lastName for candidate name
- employmentHistory contains positions with responsibilities array
- Skills have levels and categories - use this to gauge expertise depth
- May reference courses, publications, hobbies, or customSections (awards, volunteering)
- Projects array contains detailed project information

Create interview preparation materials organized by stages:

**INTERVIEW STAGES:**

Stage 1: Phone Screen (HR/Recruiter) - 30 minutes
- Focus: Background, motivation, logistics, salary expectations
- Who: HR or recruiter

Stage 2: Technical Interview - 60-90 minutes
- Focus: Technical skills, problem-solving, domain expertise
- Who: Engineering manager or senior engineer

Stage 3: Behavioral/Cultural Fit - 45-60 minutes
- Focus: Work style, team collaboration, company values
- Who: Team lead or cross-functional partners

**FOR EACH QUESTION PROVIDE:**
1. Priority level (CRITICAL/HIGH/MEDIUM)
2. Category (gap/technical/behavioral/cultural/project)
3. Why this question matters
4. Answer framework (bullet points using STAR method where appropriate)
5. Sample answer using candidate's ACTUAL experience from CV and answers

**ADDITIONAL SECTIONS:**
1. Company Research (key facts from JD)
2. Smart Questions to Ask Interviewers (5-7 questions)
3. Common Mistakes to Avoid
4. Talking Points for Each Project/Experience

Be specific, actionable, and use the candidate's actual experience from their CV."""
)
