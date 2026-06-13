import os
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from db.database import get_connection, init_db, get_important_emails
from agent.graph import email_agent

load_dotenv()

print("main.py loaded")

app = FastAPI(title="AI Email Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def poll_emails():
    interval = int(os.getenv("POLL_INTERVAL", 120))
    while True:
        print(f"\n[poller] Running email agent...")
        try:
            email_agent.invoke({})
        except Exception as e:
            print(f"[poller] Error: {e}")
        print(f"[poller] Sleeping for {interval} seconds...")
        time.sleep(interval)


@app.on_event("startup")
def startup():
    init_db()
    thread = threading.Thread(target=poll_emails, daemon=True)
    thread.start()
    print("[startup] Email polling started.")


@app.get("/")
def root():
    return {"status": "AI Email Agent is running"}


@app.get("/emails")
def get_emails():
    emails = get_important_emails()
    return {"emails": emails, "count": len(emails)}

## Development purpose only - reset the database
# @app.delete("/dev/reset")
# def reset_emails():
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute("DELETE FROM processed_emails;")
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return {"status": "Database cleared"}


@app.post("/run")
def run_agent():
    try:
        email_agent.invoke({})
        return {"status": "Agent ran successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}