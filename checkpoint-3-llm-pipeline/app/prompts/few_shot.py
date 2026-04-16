# ====================================================================
# prompts/few_shot.py — Few-shot prompt for ticket classification
# ====================================================================
# Checkpoint 2: Prompt Engineering & Structured Outputs
# Demonstrates few-shot prompting: giving the LLM examples of
# correct classifications to improve accuracy and consistency.
# Compare results with the zero-shot classify.py prompt.
# ====================================================================

FEW_SHOT_CLASSIFY_PROMPT = """You are a support ticket classifier. Classify the support ticket
into exactly one category. Here are examples of correct classifications:

Example 1:
Ticket: "The export button throws a 500 error every time I click it. Started yesterday."
Classification: {{"category": "bug_report", "confidence": 0.95, "reasoning": "User reports a specific error (500) with a reproducible action (clicking export button)."}}

Example 2:
Ticket: "It would be great if you could add keyboard shortcuts for the most common actions."
Classification: {{"category": "feature_request", "confidence": 0.92, "reasoning": "User is suggesting a new capability (keyboard shortcuts) that doesn't currently exist."}}

Example 3:
Ticket: "I was double-charged last month and haven't received my refund yet."
Classification: {{"category": "billing", "confidence": 0.97, "reasoning": "User reports a payment issue (double charge) and is requesting financial resolution."}}

Example 4:
Ticket: "Your support team went above and beyond to help me set up my account. Thank you!"
Classification: {{"category": "praise", "confidence": 0.93, "reasoning": "User is expressing gratitude and positive feedback about their support experience."}}

Now classify this ticket. Use exactly these categories: bug_report, feature_request,
billing, account, praise, general.

Support ticket:
{text}"""
