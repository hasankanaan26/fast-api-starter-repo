# ====================================================================
# llm.py — Thin wrapper around the LLM client
# ====================================================================
# Checkpoint 1: Hosted LLMs — call_llm() for text responses.
# Checkpoint 3: Structured outputs — call_llm_structured() returns
#   validated Pydantic models via provider-native JSON schemas.
#   Gemini, OpenAI, and Azure OpenAI can all guarantee valid JSON
#   matching a Pydantic schema — no manual parsing needed.
# ====================================================================

from functools import lru_cache

from pydantic import BaseModel

from app.config import (
    LLM_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT,
)


# Purpose: Cached client factories — reuse HTTP connections across calls.
@lru_cache(maxsize=1)
def _get_gemini_client():
    from google import genai
    return genai.Client(api_key=GEMINI_API_KEY)


@lru_cache(maxsize=1)
def _get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY)


@lru_cache(maxsize=1)
def _get_azure_client():
    from openai import AzureOpenAI
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )


# Purpose: Returns the model name string for the active LLM provider.
def get_model_name() -> str:
    """Return the model name for the active provider."""
    if LLM_PROVIDER == "gemini":
        return GEMINI_MODEL
    if LLM_PROVIDER == "openai":
        return OPENAI_MODEL
    return AZURE_OPENAI_DEPLOYMENT


# Purpose: Sends a prompt to the configured LLM and returns the response text.
# This is the only function you need to call the LLM throughout the app.
def call_llm(user_prompt: str, system_prompt: str = "") -> str:
    """
    Send a prompt to the LLM and return the response text.

    Uses Gemini, OpenAI, or Azure OpenAI based on the LLM_PROVIDER setting.

    Args:
        user_prompt: The user's question or instruction.
        system_prompt: Optional system-level instructions for the LLM.

    Returns:
        The LLM's response as a string.
    """
    if LLM_PROVIDER == "gemini":
        return _call_gemini(user_prompt, system_prompt)
    if LLM_PROVIDER == "openai":
        return _call_openai(user_prompt, system_prompt)
    return _call_azure(user_prompt, system_prompt)


# Purpose: Sends a prompt to the LLM and returns a validated Pydantic model instance.
# Uses native structured output — the provider guarantees valid JSON matching the schema.
def call_llm_structured(user_prompt: str, response_model: type[BaseModel], system_prompt: str = "") -> BaseModel:
    """
    Send a prompt to the LLM and return a validated Pydantic model.

    Uses provider-native structured output to guarantee the response
    conforms to the schema. No manual JSON parsing needed.
    """
    if LLM_PROVIDER == "gemini":
        return _call_gemini_structured(user_prompt, response_model, system_prompt)
    if LLM_PROVIDER == "openai":
        return _call_openai_structured(user_prompt, response_model, system_prompt)
    return _call_azure_structured(user_prompt, response_model, system_prompt)


def _call_gemini(user_prompt: str, system_prompt: str) -> str:
    """Call Google Gemini API with proper system instruction support."""
    from google.genai import types

    client = _get_gemini_client()

    config = types.GenerateContentConfig(temperature=0.3)
    if system_prompt:
        config.system_instruction = system_prompt

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=config,
    )

    return response.text


def _call_gemini_structured(user_prompt: str, response_model: type[BaseModel], system_prompt: str) -> BaseModel:
    """Call Gemini with native structured output via response_schema."""
    from google.genai import types

    client = _get_gemini_client()

    config = types.GenerateContentConfig(
        temperature=0.3,
        response_mime_type="application/json",
        response_schema=response_model,
    )
    if system_prompt:
        config.system_instruction = system_prompt

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=user_prompt,
        config=config,
    )

    return response_model.model_validate_json(response.text)


def _call_openai(user_prompt: str, system_prompt: str) -> str:
    """Call OpenAI API."""
    client = _get_openai_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content


def _call_openai_structured(user_prompt: str, response_model: type[BaseModel], system_prompt: str) -> BaseModel:
    """Call OpenAI with native structured output via response_format."""
    client = _get_openai_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.beta.chat.completions.parse(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.3,
        response_format=response_model,
    )

    return response.choices[0].message.parsed


def _call_azure(user_prompt: str, system_prompt: str) -> str:
    """Call Azure OpenAI API."""
    client = _get_azure_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        temperature=0.3,
    )

    return response.choices[0].message.content


def _call_azure_structured(user_prompt: str, response_model: type[BaseModel], system_prompt: str) -> BaseModel:
    """Call Azure OpenAI with native structured output via response_format."""
    client = _get_azure_client()

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.beta.chat.completions.parse(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        temperature=0.3,
        response_format=response_model,
    )

    return response.choices[0].message.parsed
