# Overfiew

Building automation pipelines which of course is a trending buzzword in development community has taken the market by storm. Non-coders who don't know codes platforms like n8n, make have enabled them to automate their day to day
tasks as well without much of a hassle. Automation is heavily depended upon large language models or in short LLMs, over the top it may seem like just use an openai api, call a model, write something to them and get what
is wanted, that's true. This is basically how things look in a birds eye view. 

But deep inside it's much more which only an engineer would know how all these working behind the scenes, if something breaks, how to take action immediately rather finding answers online.
The automation pipeline built for this email agent doesn't only call a model and writes the answer, It does prompt engineering, it orcestrates workflow customization from the root level allows for multi-agent connection and much more. 
Not all these are touched but the track exerts promising aspects for even bigger engineering.

The system continuously polls an inbox (mock data), classifies each email using a hybrid AI approach (rule-based + Groq LLM), and surfaces only the important ones on a clean dashboard. Non-important emails are silently ignored.

# How the AI works

Classification uses a **two-stage hybrid approach:**

**Stage 1 — Rule-based pre-filter (fast, free)**
- Scans subject and body for spam keywords (e.g. "newsletter", "deal", "promo")
- Scans for important keywords (e.g. "urgent", "critical", "payment failed")
- If clearly spam → classified immediately, LLM skipped (saves API calls)
- If uncertain → passed to Stage 2

**Stage 2 — Groq LLM classifier (accurate)**
- Uses `llama-3.3-70b-versatile` via Groq API
- Reads full email context (sender, subject, body)
- Returns structured JSON decision:
  - `important` — true or false
  - `priority` — HIGH, MEDIUM, or LOW
  - `category` — PAYMENT_ISSUE, SERVER_DOWN, CLIENT_COMPLAINT, etc.
  - `reason` — one clear sentence explaining the decision
    
  **What gets flagged as important:**
- Client complaints or urgent customer requests
- Payment failures or billing issues
- Server/system down alerts
- Anything requiring immediate business action

**What gets ignored:**
- Spam, promotions, marketing emails
- Newsletters and automated digests
- Social media notifications

## How the Dashboard Works
- Polls the backend every 30 seconds for new important emails
- Displays each email with sender, subject, priority, category, reason, and timestamp
- NEW emails animate in with a glowing border and pulsing badge
- Filter by priority (ALL / HIGH / MEDIUM / LOW)
- Stats bar shows count of HIGH / MEDIUM / LOW emails at a glance
- "Run Agent" button manually triggers the classification pipeline, not necessary to click and run. Dashboard automatically works though.

## Tech Stack

| Layer            | Technology |
|---               |---|
| AI Agent         | LangGraph + LangChain |
| LLM              | Groq API (llama-3.3-70b-versatile) |
| Backend          | FastAPI + Python |
| Database         | PostgreSQL |
| Frontend         | React + Vite + Tailwind CSS |
| Containerization | Docker + Docker Compose |

ai-email-agent/

├── backend/

│   ├── agent/

│   │   ├── graph.py          # LangGraph graph definition

│   │   ├── nodes.py          # fetch, classify, store nodes

│   │   ├── classifier.py     # Groq LLM + rule-based logic

│   │   ├── mock_data.json    # mock email dataset

│   │   └── email_reader.py   # Gmail/IMAP reader [Future scope for acutal email calling]

│   ├── db/

│   │   └── database.py       # PostgreSQL connection + queries

│   ├── api/

│   │   └── main.py           # FastAPI app + polling

│   ├── Dockerfile

│   ├── docker-compose.yml    # postgres + pgadmin (dev)

│   └── requirements.txt

├── frontend/

│   ├── src/

│   │   └── App.jsx           # React dashboard

│   ├── public/

│   │   └── config.js         # runtime API config

│   └── Dockerfile

├── docker-compose.yml        # full stack (prod)

└── README.md

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop

### Steps

**1. Clone the repo:**
```bash
git clone https://github.com/yourusername/ai-email-agent.git
cd ai-email-agent
```

**2. Set up environment variables:**
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env` and add your Groq API key:
GROQ_API_KEY=your_groq_api_key_here
Get a free Groq API key at [console.groq.com](https://console.groq.com)

Why GROQ: Although it's ideal to use openai models, but nowadays nearly all of them are paid, while reviewing calling the models might expend tokens that might crash the application.
LLama based free models provide quite a good amount of free tokens that helps to test the agent or run the agent a significant number of times.


**3. Start PostgreSQL:**
```bash
cd backend
docker compose up -d
```

**4. Set up Python environment:**
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

**5. Start the backend:**
```bash
python -m uvicorn api.main:app --reload --reload-dir api --reload-dir db --port 8000
```

**6. Start the frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

**7. Access the services:**

| Service | URL |
|---|---|
| Dashboard | http://localhost:5173 |
| API | http://127.0.0.1:8000 |
| pgAdmin | http://localhost:5051 |

## How to run the full stack (all at once)
```bash
(stay at the root folder after cloning)
cp .env.example .env
# Add your GROQ_API_KEY to .env
docker compose up --build
```

## Live Demo

- Dashboard: https://frontend-email-agent-production.up.railway.app/
- API: https://backend-email-agent-production.up.railway.app

## Limitations

- Mock mode only simulates email polling — no real inbox connection for now, left for future scope
- Groq free tier has rate limits — processing large batches may be throttled
- Gmail mode requires 2-Step Verification and an App Password, handling all these were left for future scopes
- Dashboard auto-refreshes every 30 seconds — not a true real-time websocket connection
- Email body is truncated to 1000 characters for classification (so that free tokens don't get run out shortly)
- Polling should be performed automatically without any intervals so that agent and ui stay synched at the same time

