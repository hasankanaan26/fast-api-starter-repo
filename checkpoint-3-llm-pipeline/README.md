# Checkpoint 3 -- Building an LLM Pipeline

## Objective

Chain multiple LLM calls into a multi-step processing pipeline with conditional prompting and error handling.

## What's New in This Checkpoint

| File | What it does |
|------|-------------|
| `app/pipeline.py` | `run_pipeline()` -- 3-step orchestration with per-step error handling |
| `app/prompts/pipeline.py` | Classification, extraction (per-category), and summary prompts |
| `app/routers/pipeline.py` | `POST /pipeline/analyze` endpoint |
| `app/models.py` | Adds ClassificationStep, ExtractionResult, PipelineRequest, PipelineResult |

## The Pipeline

```
Input Text
    |
Step 1: CLASSIFY (structured) -- bug_report, feature_request, billing, praise, general
    |
Step 2: EXTRACT (structured) -- category-specific fields (e.g., severity for bugs, amount for billing)
    |
Step 3: GENERATE (text) -- formatted summary with suggested next action
    |
PipelineResult (all intermediate steps visible)
```

## How to Run

```bash
# From the week-2-llm-apps directory:
python run_checkpoint.py checkpoint-3-llm-pipeline
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/ask` | General question-answering (from Checkpoint 1) |
| POST | `/analyze/*` | Structured analysis endpoints (from Checkpoint 2) |
| POST | `/pipeline/analyze` | Full 3-step pipeline: classify -> extract -> generate |

## Try These

1. Pipeline a bug report: "The app crashes when I export to PDF. Error: Export module failed. Started after v3.2.1."
2. Pipeline a feature request: "Could you add dark mode? Working late with the bright UI strains my eyes."
3. Pipeline a billing issue: "I was charged $49.99 but I cancelled 3 days before renewal."
4. Pipeline a praise: "Thanks to support agent Maria for helping me migrate my data!"
5. Compare: same pipeline, five different text types, five different extraction schemas
6. Try sending text that could be ambiguous -- see how the pipeline classifies it

## What Was Live-Coded vs Pre-Built

**Live-coded (during session):**
- `app/models.py` -- pipeline Pydantic models
- `app/prompts/pipeline.py` -- all pipeline step prompts
- `app/pipeline.py` -- run_pipeline() with error handling
- `app/routers/pipeline.py` -- the endpoint
- Router mounting in `main.py`

**Pre-built (provided):**
- `app/llm.py`, `app/config.py` (from Checkpoints 1-2)
- All Checkpoint 1 and 2 code (carried forward)
