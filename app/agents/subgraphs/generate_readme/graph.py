import os
from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.utils.converters import to_path_map
from app.agents.state_schema import State

from .generate_readme import generate_readme

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(generate_readme))

g.add_node(n(generate_readme), generate_readme)
g.add_edge(n(generate_readme), END)

generate_readme_graph = g.compile()


os.makedirs("./app/agents/graph_diagrams", exist_ok=True)
with open("./app/agents/graph_diagrams/generate_readme_graph.png", "wb") as f:
    f.write(generate_readme_graph.get_graph().draw_mermaid_png())
