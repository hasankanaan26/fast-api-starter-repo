"""
Pydantic schemas for the chat API.

These models describe the request and response payloads for the /chat endpoint.
Keeping them in their own module separates the API contract from the routing
layer (app/routers/chat.py) and the Ollama client (app/services/ollama.py).
"""

from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single message in a chat conversation."""

    role: Literal["system", "user", "assistant"] = Field(
        ...,
        description="Who sent the message: 'system', 'user', or 'assistant'.",
    )
    content: str = Field(..., description="The text content of the message.")


class ChatRequest(BaseModel):
    """Request body for the /chat endpoint."""

    messages: list[ChatMessage] = Field(
        ...,
        description="Conversation history to send to the model. Must contain at least one message.",
        min_length=1,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "messages": [
                        {"role": "user", "content": "Hello! Tell me a fun fact about octopuses."}
                    ]
                }
            ]
        }
    }


class ChatResponse(BaseModel):
    """Response body for the /chat endpoint."""

    model: str = Field(..., description="The model that produced the reply.")
    message: ChatMessage = Field(..., description="The assistant's reply message.")
