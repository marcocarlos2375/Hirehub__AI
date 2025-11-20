"""
Prompt templates for scorer service.
"""

from langchain.prompts import PromptTemplate

SCORER_PROMPT = PromptTemplate(
    input_variables=["cv_data", "jd_data", "vector_score_data", "rag_context", "format_instructions"],
    template="""Analyze the gaps, strengths, and provide recommendations for this CV and Job Description match.

CV DATA:
{cv_data}

JOB DESCRIPTION DATA:
{jd_data}

CURRENT MATCH SCORE (calculated via vector similarity):
{vector_score_data}

{rag_context}

{format_instructions}

YOUR TASK: Provide qualitative analysis ONLY (do NOT recalculate scores):

1. TOP GAPS: Identify 5-8 critical missing elements that hurt the score
   - Focus on missing hard skills with high priority
   - Include experience gaps, domain mismatches
   - Estimate impact if gap is filled (e.g., "+15% score")

2. STRENGTHS: Identify 3-5 strong points in the CV that match well
   - Highlight matched skills with high similarity
   - Note relevant experience or achievements

3. RECOMMENDATIONS: Provide 3-5 actionable suggestions to improve match

Be specific, honest, and actionable."""
)
