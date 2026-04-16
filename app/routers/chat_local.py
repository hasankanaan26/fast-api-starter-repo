"""
Chat router — exposes the /chat endpoint.

Thin wiring layer: accepts a list of chat messages and hands them to the
Ollama service. Models live in app/models.py; the HTTP client lives in
app/services/ollama.py.
"""

from fastapi import APIRouter

from app.models import ChatMessage, ChatResponse
from app.services.ollama import chat_completion

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(messages: list[ChatMessage]) -> ChatResponse:
    """Send a conversation to the local Ollama model and return its reply."""
    model_used, content = await chat_completion(messages=messages)
    return ChatResponse(
        model=model_used,
        message=ChatMessage(role="assistant", content=content),
    )
