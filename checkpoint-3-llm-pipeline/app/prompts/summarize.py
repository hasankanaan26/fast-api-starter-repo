# ====================================================================
# prompts/summarize.py — Prompt template for text summarization
# ====================================================================
# Checkpoint 2: Prompt Engineering & Structured Outputs
# Uses Python's .format() for template variables. The {max_sentences}
# placeholder lets callers control output length at runtime.
# ====================================================================

SUMMARIZE_PROMPT = """Summarize the following text in at most {max_sentences} sentences.

For "sentence_count", provide the number of sentences in your summary (must be <= {max_sentences}).

Text to summarize:
{text}"""
