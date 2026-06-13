from db.database import init_db
from agent.graph import email_agent

init_db()
email_agent.invoke({})