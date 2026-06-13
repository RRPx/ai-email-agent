from langgraph.graph import StateGraph, END
from agent.nodes import fetch_emails, process_emails, summarize
from typing import TypedDict, List


class AgentState(TypedDict):
    emails: List[dict]
    processed: List[dict]
    summary: dict


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("fetch", fetch_emails)
    graph.add_node("process", process_emails)
    graph.add_node("summarize", summarize)

    graph.set_entry_point("fetch")
    graph.add_edge("fetch", "process")
    graph.add_edge("process", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


email_agent = build_graph()