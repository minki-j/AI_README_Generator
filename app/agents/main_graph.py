from varname import nameof as n

import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnablePassthrough

from app.agents.state_schema import State
from app.utils.converters import to_path_map

from app.agents.subgraphs.middle_step.graph import subGraph_middle_step
from app.agents.subgraphs.generate_readme.graph import subGraph_generate_readme


g = StateGraph(State)
g.set_entry_point("entry")

g.add_node(
    "entry",
    lambda _: {
        "retrieval_count": 0,
    },
)
g.add_edge("entry", n(subGraph_middle_step))

g.add_node(n(subGraph_middle_step), subGraph_middle_step)
g.add_edge(n(subGraph_middle_step), "check if last step")

g.add_node("check if last step", RunnablePassthrough())
g.add_conditional_edges(
    "check if last step",
    lambda state: (
        n(subGraph_generate_readme)
        if state["current_step"] >= state["total_number_of_steps"]
        else "human_in_the_loop"
    ),
    to_path_map(
        [n(subGraph_generate_readme),
         "human_in_the_loop"]
    ),
)

g.add_node("human_in_the_loop", lambda state: print(f"Got feedback from the user: {state["user_feedback_list"]}"))
g.add_edge("human_in_the_loop", n(subGraph_middle_step))

g.add_node(n(subGraph_generate_readme), subGraph_generate_readme)
g.add_edge(n(subGraph_generate_readme), END)

# conn = sqlite3.connect("./cache/checkpoints.sqlite")
# memory = SqliteSaver(conn)
memory = MemorySaver()
main_graph = g.compile(
    checkpointer=memory, interrupt_before=["human_in_the_loop"]
)


with open("./app/agents/graph_diagrams/main_graph.png", "wb") as f:
    f.write(main_graph.get_graph().draw_mermaid_png())
