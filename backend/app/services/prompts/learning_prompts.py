"""
Prompt templates for learning recommendations service.
"""

from langchain.prompts import PromptTemplate

LEARNING_PATH_PROMPT = PromptTemplate(
    input_variables=["cv_data", "jd_data", "current_score", "target_score", "gaps", "score_breakdown", "rag_context", "format_instructions"],
    template="""Generate a comprehensive, personalized learning roadmap based on:

CV DATA (with personalInfo, employmentHistory, skills array with levels, courses, languages):
{cv_data}

JOB REQUIREMENTS:
{jd_data}

CURRENT SCORE: {current_score}
TARGET SCORE: {target_score}

IDENTIFIED GAPS:
{gaps}

SCORE BREAKDOWN:
{score_breakdown}

{rag_context}

{format_instructions}

IMPORTANT - CV STRUCTURE NOTES:
- Skills are in array format with skill name, level (Beginner/Intermediate/Advanced), and category
- Employment history shows positions with startDate/endDate
- May include existing courses the candidate has taken
- Languages show proficiency levels (A1-C2/Native)

Create a realistic, actionable learning plan with:

1. QUICK WINS (1-2 weeks, achievable immediately):
   - CV reframing techniques
   - LinkedIn profile optimization
   - One weekend project using critical missing skills
   - Estimated impact: +5-10% score

2. PRIORITY LEARNING AREAS (ranked by impact):
   For each priority area, include:
   - Specific courses (prefer FREE options: Coursera audit, YouTube, freeCodeCamp, etc.)
   - Platform, duration, cost
   - Hands-on projects with detailed feature lists
   - Expected score improvement
   - Time investment

3. WEEKLY ROADMAP (10-week timeline):
   - Week-by-week breakdown
   - Specific tasks for each week
   - Cumulative score improvement tracking
   - Realistic time estimates

4. TOTAL INVESTMENT ANALYSIS:
   - Total time required
   - Total cost (prioritize free resources)
   - Expected score improvement
   - ROI analysis (time vs career impact)

Be specific, realistic, and actionable. Prioritize FREE resources where possible. Focus on skills that will have the most impact on the score and job prospects."""
)
