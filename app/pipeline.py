# ====================================================================
# pipeline.py — Multi-step LLM pipeline
# ====================================================================
# Checkpoint 3: Building an LLM Pipeline
# Chains three LLM calls together:
#   Step 1: Classify the text (structured)
#   Step 2: Extract key fields based on category (structured)
#   Step 3: Generate a summary from category + fields (text)
#
# Each step is wrapped in try/except so the pipeline returns partial
# results if a step fails, rather than crashing entirely.
# ====================================================================

import logging

from app.services.hosted_llm import call_llm, call_llm_structured
from app.models import ClassificationStep, ExtractionResult, PipelineResult
from app.prompts.pipeline import (
    CLASSIFY_STEP_PROMPT,
    EXTRACT_BILLING_PROMPT,
    EXTRACT_BUG_PROMPT,
    EXTRACT_FEATURE_PROMPT,
    EXTRACT_GENERAL_PROMPT,
    EXTRACT_PRAISE_PROMPT,
    SUMMARIZE_STEP_PROMPT,
)

logger = logging.getLogger(__name__)

# Purpose: Maps a category to its extraction prompt.
EXTRACTION_PROMPTS = {
    "bug_report": EXTRACT_BUG_PROMPT,
    "feature_request": EXTRACT_FEATURE_PROMPT,
    "billing": EXTRACT_BILLING_PROMPT,
    "praise": EXTRACT_PRAISE_PROMPT,
    "general": EXTRACT_GENERAL_PROMPT,
}


# Purpose: Returns the extraction prompt for a given category.
def get_extraction_prompt(category: str) -> str:
    """Look up the extraction prompt for a category, defaulting to general."""
    return EXTRACTION_PROMPTS.get(category, EXTRACT_GENERAL_PROMPT)


# Purpose: Runs the full 3-step pipeline with per-step error handling.
def run_pipeline(text: str) -> PipelineResult:
    """
    Process text through a 3-step LLM pipeline:
      1. Classify — what kind of text is this?
      2. Extract — pull out category-specific fields
      3. Generate — produce a summary with next actions

    Returns a PipelineResult with all intermediate steps visible.
    If a step fails, returns a partial result with the error message.
    """

    # Step 1: Classify
    logger.info("Pipeline step 1: classifying text")
    try:
        classification = call_llm_structured(
            user_prompt=CLASSIFY_STEP_PROMPT.format(text=text),
            response_model=ClassificationStep,
        )
    except Exception as e:
        logger.error("Pipeline step 1 failed: %s", e)
        return PipelineResult(
            input_text=text,
            steps_completed=0,
            error=f"Classification failed: {e}",
        )

    # Step 2: Extract (prompt depends on classification)
    logger.info(
        "Pipeline step 2: extracting fields for category '%s'", classification.category
    )
    try:
        extract_prompt = get_extraction_prompt(classification.category)
        extraction = call_llm_structured(
            user_prompt=extract_prompt.format(text=text),
            response_model=ExtractionResult,
        )
    except Exception as e:
        logger.error("Pipeline step 2 failed: %s", e)
        return PipelineResult(
            input_text=text,
            classification=classification,
            steps_completed=1,
            error=f"Extraction failed: {e}",
        )

    # Step 3: Generate summary
    logger.info("Pipeline step 3: generating summary")
    try:
        fields_text = "\n".join(f"- {f.key}: {f.value}" for f in extraction.fields)
        summary = call_llm(
            user_prompt=SUMMARIZE_STEP_PROMPT.format(
                category=classification.category,
                fields=fields_text,
                text=text,
            ),
        )
    except Exception as e:
        logger.error("Pipeline step 3 failed: %s", e)
        return PipelineResult(
            input_text=text,
            classification=classification,
            extraction=extraction,
            steps_completed=2,
            error=f"Summary generation failed: {e}",
        )

    logger.info("Pipeline completed successfully")
    return PipelineResult(
        input_text=text,
        classification=classification,
        extraction=extraction,
        summary=summary,
        steps_completed=3,
    )
