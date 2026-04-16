# ====================================================================
# prompts/pipeline.py — Prompts for the multi-step LLM pipeline
# ====================================================================
# Checkpoint 3: Building an LLM Pipeline
# Each step in the pipeline has its own prompt. Step 2 (extraction)
# uses a different prompt depending on the category from Step 1.
# ====================================================================


# --- Step 1: Classification ---

CLASSIFY_STEP_PROMPT = """Classify the following text into exactly one category.

Categories:
- bug_report: Something is broken or not working as expected
- feature_request: User wants a new feature or enhancement
- billing: Payment, subscription, or pricing issues
- praise: Positive feedback or compliment
- general: Anything that doesn't fit the above categories

For "confidence", use a float between 0.0 and 1.0.
For "reasoning", briefly explain your classification.

Text to classify:
{text}"""


# --- Step 2: Category-specific extraction prompts ---

EXTRACT_BUG_PROMPT = """Extract key details from this bug report.

For "fields", return a JSON object with these keys:
- "severity": how critical the bug is (critical, high, medium, low)
- "component": which part of the product is affected
- "steps_to_reproduce": brief description of how to trigger the bug

Bug report:
{text}"""

EXTRACT_FEATURE_PROMPT = """Extract key details from this feature request.

For "fields", return a JSON object with these keys:
- "feature_name": a short name for the requested feature
- "business_value": why this feature matters to the user
- "priority": suggested priority (high, medium, low)

Feature request:
{text}"""

EXTRACT_BILLING_PROMPT = """Extract key details from this billing issue.

For "fields", return a JSON object with these keys:
- "amount": the monetary amount involved (or "unknown")
- "date": when the issue occurred (or "unknown")
- "issue_type": type of billing issue (overcharge, refund, cancellation, other)

Billing issue:
{text}"""

EXTRACT_PRAISE_PROMPT = """Extract key details from this positive feedback.

For "fields", return a JSON object with these keys:
- "who": the person or team being praised (or "general")
- "what_helped": what specifically was helpful

Feedback:
{text}"""

EXTRACT_GENERAL_PROMPT = """Extract key details from this text.

For "fields", return a JSON object with these keys:
- "topic": the main topic or subject
- "key_points": the most important points, comma-separated

Text:
{text}"""


# --- Step 3: Summary generation ---

SUMMARIZE_STEP_PROMPT = """You are processing a {category} document. Here are the extracted details:

{fields}

Original text:
{text}

Write a concise, professional summary (2-3 sentences) that:
1. States the document type and key finding
2. Highlights the most important extracted detail
3. Suggests a clear next action"""
