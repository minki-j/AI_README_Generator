from varname import nameof as n

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnablePassthrough

from app.langgraph.state_schema import State
from app.utils.converters import to_path_map

from app.langgraph.subgraphs.middle_step.graph import subGraph_middle_step
from app.langgraph.subgraphs.generate_readme.graph import subGraph_generate_readme

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(subGraph_middle_step))

g.add_node(n(subGraph_middle_step), subGraph_middle_step)
g.add_edge(n(subGraph_middle_step), n(subGraph_generate_readme))

g.add_node(n(subGraph_generate_readme), subGraph_generate_readme)
g.add_edge(n(subGraph_middle_step), END)

main_graph = g.compile(checkpointer=MemorySaver(), interrupt_after=[n(subGraph_middle_step)])


# with open("./app/langgraph/graph_diagrams/main_graph.png", "wb") as f:
#     f.write(main_graph
# .get_graph().draw_mermaid_png())
