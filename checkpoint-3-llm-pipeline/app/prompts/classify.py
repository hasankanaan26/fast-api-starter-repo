# ====================================================================
# prompts/classify.py — Prompt for support ticket classification
# ====================================================================
# Checkpoint 2: Prompt Engineering & Structured Outputs
# Zero-shot classification prompt. Compare with few_shot.py to
# see how examples improve classification accuracy.
# ====================================================================

CLASSIFY_PROMPT = """You are a support ticket classifier. Classify the following support ticket
into exactly one of these categories:

- bug_report: Something is broken or not working as expected
- feature_request: User wants a new feature or enhancement
- billing: Payment, subscription, or pricing issues
- account: Login, access, or account management issues
- praise: Positive feedback or compliment
- general: Anything that doesn't fit the above categories

For "confidence", use a float between 0.0 and 1.0.
For "reasoning", briefly explain your classification.

Support ticket:
{text}"""
