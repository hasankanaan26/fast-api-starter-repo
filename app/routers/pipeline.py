# ====================================================================
# routers/pipeline.py — Multi-step LLM pipeline endpoint
# ====================================================================
# Checkpoint 3: Building an LLM Pipeline
# Exposes the document analysis pipeline as a single endpoint.
# The response includes every intermediate step for transparency.
# ====================================================================

import logging

from fastapi import APIRouter
from app.models import PipelineRequest, PipelineResult
from app.pipeline import run_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


# Purpose: Run text through the full classify -> extract -> generate pipeline
@router.post("/analyze", response_model=PipelineResult)
def analyze_document(request: PipelineRequest):
    """
    Process text through a 3-step LLM pipeline:
    1. Classify the document type
    2. Extract category-specific fields
    3. Generate a summary with suggested actions

    Returns all intermediate steps so you can see exactly what happened.
    """
    logger.info("Starting pipeline analysis for %d characters of text", len(request.text))
    return run_pipeline(request.text)
