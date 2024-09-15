from varname import nameof as n

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.agents.state_schema import State
from app.utils.converters import to_path_map

from app.agents.subgraphs.steps.graph import subGraph_steps
from app.agents.subgraphs.generate_readme.graph import subGraph_generate_readme

import os

def check_if_last_step(state):
    print("\n>>>> EDGE: check_if_last_step")
    if state["current_step"] is None or state["total_number_of_steps"] is None:
        raise(ValueError("current_step or total_number_of_steps is None"))
    if int(state["current_step"]) > int(state["total_number_of_steps"]):
        return n(subGraph_generate_readme)
    return n(check_if_regenerate_with_feedback)

def check_if_regenerate_with_feedback(state):
    print("\n>>>> EDGE: check_if_regenerate_with_feedback")
    if int(state["current_step"]) == int(state["previous_step"]):
        return {
            "retrieved_chunks": "RESET",
        }
    else:
        return{
            "previous_step": int(state["current_step"]),
        }

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", "check_if_last_step")

g.add_node("check_if_last_step", RunnablePassthrough())
g.add_conditional_edges(
    "check_if_last_step",
    check_if_last_step,
    to_path_map(
        [n(subGraph_generate_readme),
         n(check_if_regenerate_with_feedback)]
    ),
)

g.add_node(n(check_if_regenerate_with_feedback), check_if_regenerate_with_feedback)
g.add_edge(n(check_if_regenerate_with_feedback), n(subGraph_steps))


g.add_node(n(subGraph_steps), subGraph_steps)
g.add_edge(n(subGraph_steps), "human_in_the_loop")

g.add_node("human_in_the_loop", RunnablePassthrough())
g.add_edge("human_in_the_loop", "check_if_last_step")

g.add_node(n(subGraph_generate_readme), subGraph_generate_readme)
g.add_edge(n(subGraph_generate_readme), END)

if os.path.exists(f"/vol"):
    os.makedirs("/vol/data/graph_checkpoints", exist_ok=True)
    db_path = os.path.join("/vol", "data", "graph_checkpoints", "checkpoints.sqlite")
else:
    os.makedirs("./data/graph_checkpoints", exist_ok=True)
    db_path = os.path.join(".", "data", "graph_checkpoints", "checkpoints.sqlite")

with SqliteSaver.from_conn_string(db_path) as memory:
    main_graph = g.compile(
        checkpointer=memory, interrupt_before=["human_in_the_loop"]
    )

with open("./app/agents/graph_diagrams/main_graph.png", "wb") as f:
    f.write(main_graph.get_graph().draw_mermaid_png())
