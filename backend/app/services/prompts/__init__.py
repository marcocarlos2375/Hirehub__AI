"""
LangChain prompt templates for AI services.
Centralized prompts for easier maintenance and A/B testing.
"""

from .cv_parser_prompts import CV_PARSER_PROMPT
from .jd_analyzer_prompts import JD_ANALYZER_PROMPT
from .scorer_prompts import SCORER_PROMPT
from .question_prompts import QUESTION_GEN_PROMPT
from .cover_letter_prompts import COVER_LETTER_PROMPT
from .learning_prompts import LEARNING_PATH_PROMPT
from .interview_prompts import INTERVIEW_PREP_PROMPT
from .cv_optimizer_prompts import CV_OPTIMIZER_PROMPT

__all__ = [
    "CV_PARSER_PROMPT",
    "JD_ANALYZER_PROMPT",
    "SCORER_PROMPT",
    "QUESTION_GEN_PROMPT",
    "COVER_LETTER_PROMPT",
    "LEARNING_PATH_PROMPT",
    "INTERVIEW_PREP_PROMPT",
    "CV_OPTIMIZER_PROMPT",
]
