# ====================================================================
# routers/ask.py — Simple question-answering endpoint
# ====================================================================
# Checkpoint 1: Hosted LLMs
# POST /ask — accepts a question, calls the LLM, returns an answer.
# This is the simplest possible LLM integration pattern.
# ====================================================================

from fastapi import APIRouter
from app.models import Question, Answer
from app.services.hosted_llm import call_llm, get_model_name
from app.prompts.assistant import ASSISTANT_PROMPT

router = APIRouter(prefix="", tags=["ask"])


# Purpose: Accept a question and return an LLM-generated answer
@router.post("/ask", response_model=Answer)
def ask_question(request: Question):
    """Send a question to the LLM and get an answer back."""
    response_text = call_llm(
        user_prompt=request.question,
        system_prompt=ASSISTANT_PROMPT,
    )

    return Answer(
        answer=response_text,
        model=get_model_name(),
    )
