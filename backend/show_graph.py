from agent.graph import email_agent

png_bytes = email_agent.get_graph().draw_mermaid_png()

with open("graph.png", "wb") as f:
    f.write(png_bytes)

print("Graph saved to graph.png")