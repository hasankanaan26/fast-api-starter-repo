# ====================================================================
# config.py — Centralized configuration via environment variables
# ====================================================================
# Checkpoint 2: Prompt Engineering & Structured Outputs
# Same config as checkpoint 1 — no new settings needed yet.
# ====================================================================

import os
from dotenv import load_dotenv

load_dotenv()

# --- Provider selector ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

# --- Gemini Settings ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# --- OpenAI Settings ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# --- Azure OpenAI Settings ---
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "")
