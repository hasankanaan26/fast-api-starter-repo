# ====================================================================
# routers/structured.py — Structured output endpoints
# ====================================================================
# Checkpoint 3: Building an LLM Pipeline (carried from Checkpoint 2)
# Three endpoints that demonstrate different prompt patterns:
#   POST /analyze/sentiment  — Native structured output from LLM
#   POST /analyze/summarize  — Template variables with .format()
#   POST /analyze/classify   — Few-shot prompting with examples
#
# All endpoints use call_llm_structured() which leverages provider-
# native structured output (Gemini response_schema / OpenAI
# response_format) to guarantee valid JSON matching the Pydantic model.
# ====================================================================

import logging

from fastapi import APIRouter
from app.models import (
    AnalyzeRequest,
    SentimentResult,
    SummaryRequest,
    SummaryResult,
    ClassifyRequest,
    ClassifyResult,
)
from app.llm import call_llm_structured
from app.prompts.sentiment import SENTIMENT_PROMPT
from app.prompts.summarize import SUMMARIZE_PROMPT
from app.prompts.few_shot import FEW_SHOT_CLASSIFY_PROMPT

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["analyze"])


# Purpose: Analyze sentiment of text using native structured output
@router.post("/sentiment", response_model=SentimentResult)
def analyze_sentiment(request: AnalyzeRequest):
    """Analyze the sentiment of the provided text."""
    prompt = SENTIMENT_PROMPT.format(text=request.text)
    return call_llm_structured(user_prompt=prompt, response_model=SentimentResult)


# Purpose: Summarize text with a configurable sentence limit
@router.post("/summarize", response_model=SummaryResult)
def summarize_text(request: SummaryRequest):
    """Summarize the provided text in N sentences or fewer."""
    prompt = SUMMARIZE_PROMPT.format(
        text=request.text,
        max_sentences=request.max_sentences,
    )
    return call_llm_structured(user_prompt=prompt, response_model=SummaryResult)


# Purpose: Classify a support ticket using few-shot examples
@router.post("/classify", response_model=ClassifyResult)
def classify_ticket(request: ClassifyRequest):
    """Classify a support ticket into a category using few-shot prompting."""
    prompt = FEW_SHOT_CLASSIFY_PROMPT.format(text=request.text)
    return call_llm_structured(user_prompt=prompt, response_model=ClassifyResult)

    # TODO (Lab exercise): Add a query parameter `use_few_shot=True`
    # that switches between the zero-shot CLASSIFY_PROMPT and the
    # few-shot FEW_SHOT_CLASSIFY_PROMPT. Compare the results!
