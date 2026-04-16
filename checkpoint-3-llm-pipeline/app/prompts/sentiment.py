# ====================================================================
# prompts/sentiment.py — Prompt for sentiment analysis
# ====================================================================
# Checkpoint 2: Prompt Engineering & Structured Outputs
# Asks the LLM to return structured JSON with sentiment,
# confidence score, and reasoning. The key teaching point:
# you can control LLM output format through clear instructions.
# ====================================================================

SENTIMENT_PROMPT = """Analyze the sentiment of the following text.

For "sentiment", use one of: "positive", "negative", "neutral", or "mixed".
For "confidence", use a float between 0.0 and 1.0.
For "reasoning", briefly explain why you chose this sentiment.

Text to analyze:
{text}"""
