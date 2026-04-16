# ====================================================================
# models.py — Pydantic models for request/response validation
# ====================================================================
# Checkpoint 3: Building an LLM Pipeline
# Adds pipeline models for multi-step LLM processing:
# ClassificationStep, ExtractionResult, PipelineRequest, PipelineResult.
# ====================================================================

from pydantic import BaseModel


# --- Checkpoint 1 models (carried forward) ---

class Question(BaseModel):
    question: str


class Answer(BaseModel):
    answer: str
    model: str


# --- Checkpoint 2 models: Structured analysis (carried forward) ---

class AnalyzeRequest(BaseModel):
    text: str


class SentimentResult(BaseModel):
    sentiment: str
    confidence: float
    reasoning: str


class SummaryRequest(BaseModel):
    text: str
    max_sentences: int = 3


class SummaryResult(BaseModel):
    summary: str
    sentence_count: int


class ClassifyRequest(BaseModel):
    text: str


class ClassifyResult(BaseModel):
    category: str
    confidence: float
    reasoning: str


# --- Checkpoint 3 models: LLM Pipeline ---

class PipelineRequest(BaseModel):
    text: str


class ClassificationStep(BaseModel):
    category: str
    confidence: float
    reasoning: str


class KeyValuePair(BaseModel):
    key: str
    value: str


class ExtractionResult(BaseModel):
    fields: list[KeyValuePair]


class PipelineResult(BaseModel):
    input_text: str
    classification: ClassificationStep | None = None
    extraction: ExtractionResult | None = None
    summary: str = ""
    steps_completed: int = 0
    error: str | None = None
