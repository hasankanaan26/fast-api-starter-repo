"""
Application configuration.

Centralizes environment variable loading so other modules don't each call
load_dotenv() and os.getenv() independently. Import the module-level constants
(or the `settings` object) wherever configuration is needed.

Environment variables:
    OLLAMA_BASE_URL   e.g. http://localhost:11434
    OLLAMA_MODEL      e.g. llama3.2:1b
"""

import os

from dotenv import load_dotenv

# Load variables from .env once, at import time.
load_dotenv()

OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
