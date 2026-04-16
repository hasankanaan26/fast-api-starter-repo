# ====================================================================
# main.py — FastAPI application entry point
# ====================================================================
# Checkpoint 3: Building an LLM Pipeline
# Endpoints: GET /health, POST /ask, POST /analyze/*, POST /pipeline/analyze
# Chains multiple LLM calls into a multi-step processing pipeline.
# ====================================================================

from fastapi import FastAPI
from app.routers import ask, structured, pipeline

app = FastAPI(
    title="AI Assistant",
    version="0.3.0",
    description="Week 2 — Checkpoint 3: Building an LLM Pipeline",
)


# Purpose: Health check with checkpoint indicator
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "checkpoint": 3,
        "version": app.version,
    }


app.include_router(ask.router)
app.include_router(structured.router)
app.include_router(pipeline.router)
