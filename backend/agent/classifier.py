import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

## ****
# Logic uses rule based + LLM checks [Hybrid approach]
# LLM is used only at the time of sketchy emails if rule based classification is uncertain to take decision to save cost on LLM api calls
## ****


SPAM_KEYWORDS = [
    "unsubscribe", "newsletter", "deal", "offer", "promo",
    "discount", "free trial", "limited time", "top stories",
    "connection request", "you have", "curated for you"
]

IMPORTANT_KEYWORDS = [
    "urgent", "critical", "failed", "failure", "down", "error",
    "complaint", "broken", "action required", "terminate", "escalate",
    "declined", "invoice", "payment", "production", "costing"
]


def rule_based_check(subject: str, body: str) -> str | None:
    """
    Returns 'spam' or 'important' if rules are confident.
    Returns None if rules are not sure — let LLM decide.
    """
    text = (subject + " " + body).lower()

    spam_hits = sum(1 for kw in SPAM_KEYWORDS if kw in text)
    important_hits = sum(1 for kw in IMPORTANT_KEYWORDS if kw in text)

    if important_hits >= 2:
        return "important"
    if spam_hits >= 2 and important_hits == 0:
        return "spam"

    return None  # uncertain — pass to LLM


# ─── LLM Classifier ──────────────────────────────────────────────────────────

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

SYSTEM_PROMPT = """
You are an AI email classifier for a business inbox.

Your job is to analyze each email and return a JSON decision.

Classify as important if the email is:
- A client complaint or urgent customer request
- A payment failure or billing issue
- A server/system down alert
- Anything that requires immediate business action

Classify as NOT important if the email is:
- Spam, promotions, or marketing
- Newsletters or automated digests
- Social media notifications
- Anything that does not require immediate attention

You MUST respond with ONLY a valid JSON object, no extra text:
{
    "important": true or false,
    "priority": "HIGH" or "MEDIUM" or "LOW",
    "category": "PAYMENT_ISSUE" or "SERVER_DOWN" or "CLIENT_COMPLAINT" or "BILLING_ISSUE" or "SPAM" or "NEWSLETTER" or "PROMOTION" or "OTHER",
    "reason": "one clear sentence explaining your decision"
}
"""


def classify_with_llm(sender: str, subject: str, body: str) -> dict:
    """Call Groq LLM to classify the email."""
    user_message = f"""
                    From: {sender}
                    Subject: {subject}
                    Body: {body}
                    """
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_message)
    ])

    raw = response.content.strip()

    # strip markdown code fences if LLM wraps in ```json
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())


# ─── Main classify function ───────────────────────────────────────────────────

def classify_email(email: dict) -> dict:
    """
    Hybrid classifier:
    1. Run rule-based check first
    2. If uncertain, call LLM for final decision
    """
    sender = email["sender"]
    subject = email["subject"]
    body = email["body"]

    rule_result = rule_based_check(subject, body)

    if rule_result == "spam":
        # confident it's spam, skip LLM
        return {
            "important": False,
            "priority": "LOW",
            "category": "SPAM",
            "reason": "Rule-based: email matched multiple spam keywords.",
            "classified_by": "rules"
        }

    # either confirmed important by rules OR uncertain — use LLM
    result = classify_with_llm(sender, subject, body)
    result["classified_by"] = "llm"
    return result