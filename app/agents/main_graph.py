from varname import nameof as n

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.agents.state_schema import State
from app.utils.converters import to_path_map

from app.agents.subgraphs.steps.graph import steps_graph
from app.agents.subgraphs.generate_readme.graph import generate_readme_graph

import os

def is_last_step(state):
    print("\n>>>> EDGE: is_last_step")
    if state["current_step"] is None or state["total_number_of_steps"] is None:
        raise(ValueError("current_step or total_number_of_steps is None"))
    if int(state["current_step"]) > int(state["total_number_of_steps"]):
        print("True: generate readme")
        return n(generate_readme_graph)
    print("False: move to next step")
    return n(steps_graph)

g = StateGraph(State)
g.set_entry_point("reset_variables")

g.add_node(
    "reset_variables",
    lambda state: {
        #! Always reset variables in the root level.
        "previous_step": int(state["current_step"]),
        "retrieved_chunks": "RESET", #TODO: Need to handle conditionally
        "valid_paths": "RESET",
        "corrected_paths": [],
    },
)
g.add_edge("reset_variables", "is_last_step")

g.add_node("is_last_step", RunnablePassthrough())
g.add_conditional_edges(
    "is_last_step",
    is_last_step,
    to_path_map([n(generate_readme_graph), n(steps_graph)]),
)

g.add_node(n(steps_graph), steps_graph)
g.add_edge(n(steps_graph), "human_in_the_loop")

g.add_node("human_in_the_loop", RunnablePassthrough())
g.add_edge("human_in_the_loop", "reset_variables")

g.add_node(n(generate_readme_graph), generate_readme_graph)
g.add_edge(n(generate_readme_graph), END)


os.makedirs("./data/graph_checkpoints", exist_ok=True)
db_path = os.path.join(".", "data", "graph_checkpoints", "checkpoints.sqlite")

with SqliteSaver.from_conn_string(db_path) as memory:
    main_graph = g.compile(
        checkpointer=memory, interrupt_before=["human_in_the_loop"]
    )

os.makedirs("./app/agents/graph_diagrams", exist_ok=True)
with open("./app/agents/graph_diagrams/main_graph.png", "wb") as f:
    f.write(main_graph.get_graph(xray=10).draw_mermaid_png())
