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

subGraph_generate_readme = g.compile()


with open("./app/agents/graph_diagrams/subGraph_generate_readme.png", "wb") as f:
    f.write(subGraph_generate_readme.get_graph().draw_mermaid_png())
