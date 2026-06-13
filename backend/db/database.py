import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_emails (
            id SERIAL PRIMARY KEY,
            email_id VARCHAR(255) UNIQUE NOT NULL,
            sender VARCHAR(255),
            subject TEXT,
            body TEXT,
            important BOOLEAN,
            priority VARCHAR(10),
            category VARCHAR(50),
            reason TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully.")


def is_duplicate(email_id: str) -> bool:
    """Check if email was already processed."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM processed_emails WHERE email_id = %s",
        (email_id,)
    )
    exists = cursor.fetchone() is not None

    cursor.close()
    conn.close()
    return exists


def save_email(email: dict):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO processed_emails 
            (email_id, sender, subject, body, important, priority, category, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email_id) DO NOTHING
        """, (
            email["email_id"],
            email["sender"],
            email["subject"],
            email["body"],
            email["important"],
            email["priority"],
            email["category"],
            email["reason"]
        ))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"[db] Saved email: {email['email_id']}")

    except Exception as e:
        print(f"[db] Error saving {email['email_id']}: {e}")


def get_important_emails():
    """Fetch all important emails for the dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT email_id, sender, subject, priority, category, reason, received_at
        FROM processed_emails
        WHERE important = TRUE
        ORDER BY received_at DESC
    """)

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "email_id": row[0],
            "sender": row[1],
            "subject": row[2],
            "priority": row[3],
            "category": row[4],
            "reason": row[5],
            "received_at": row[6].isoformat()
        }
        for row in rows
    ]