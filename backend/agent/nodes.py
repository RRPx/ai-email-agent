import json
import os
from agent.classifier import classify_email
from db.database import is_duplicate, save_email

MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "mock_data.json")


def fetch_emails(state: dict) -> dict:
    with open(MOCK_DATA_PATH, "r") as f:
        emails = json.load(f)
    print(f"[fetch] Fetching {len(emails)} mock emails...")
    return {"emails": emails}


def process_emails(state: dict) -> dict:
    emails = state["emails"]
    results = []

    for email in emails:
        email_id = email["email_id"]

        try:
            if is_duplicate(email_id):
                print(f"[process] Skipping duplicate: {email_id}")
                continue

            print(f"[process] Classifying: {email['subject']}")

            classification = classify_email(email)

            full_record = {
                **email,
                "important": classification["important"],
                "priority": classification["priority"],
                "category": classification["category"],
                "reason": classification["reason"],
            }

            save_email(full_record)

            if classification["important"]:
                print(f"[process] IMPORTANT ({classification['priority']}): {email['subject']}")
            else:
                print(f"[process] ignored: {email['subject']}")

            results.append(full_record)

        except Exception as e:
            print(f"[process] Error processing {email_id}: {e} — skipping")
            continue

    return {"processed": results}


def summarize(state: dict) -> dict:
    processed = state.get("processed", [])
    important = [e for e in processed if e["important"]]

    print(f"\n[summary] Processed: {len(processed)} emails")
    print(f"[summary] Important: {len(important)} emails")
    print(f"[summary] Ignored: {len(processed) - len(important)} emails")

    return {"summary": {"total": len(processed), "important": len(important)}}