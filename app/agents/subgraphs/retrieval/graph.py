import os
from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.utils.converters import to_path_map
from app.agents.state_schema import State

from .retrieve_with_path import read_files, add_user_chosen_files
from .validate_file_path import validate_file_paths_from_LLM
from .retrieve_with_colbert import retrieve_with_colbert
from .retrieve_with_faiss import retrieve_with_faiss

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(add_user_chosen_files))
g.add_edge("entry", n(validate_file_paths_from_LLM))
g.add_edge("entry", "choose_retrieval_method")

g.add_node("choose_retrieval_method", RunnablePassthrough())


def choose_retrieval_method(state):
    print("\n>>>> EDGE: choose_retrieval_method")
    retrieval_method = state.get("retrieval_method", os.getenv("DEFAULT_RETRIEVAL"))

    method_mapping = {
        "COLBERT": n(retrieve_with_colbert),
        "FAISS": n(retrieve_with_faiss),
    }

    if retrieval_method in method_mapping:
        print(f"{retrieval_method} is chosen")
        return method_mapping[retrieval_method]
    else:
        raise ValueError(f"Invalid retrieval method: {retrieval_method}")


g.add_conditional_edges(
    "choose_retrieval_method",
    choose_retrieval_method,
    to_path_map([n(retrieve_with_colbert), n(retrieve_with_faiss)]),
)

g.add_node(n(add_user_chosen_files), add_user_chosen_files)
g.add_edge(n(add_user_chosen_files), n(read_files))

g.add_node(n(retrieve_with_colbert), retrieve_with_colbert)
g.add_node(n(retrieve_with_faiss), retrieve_with_faiss)

g.add_node(n(validate_file_paths_from_LLM), validate_file_paths_from_LLM)
g.add_edge(n(validate_file_paths_from_LLM), n(read_files))

g.add_node(n(read_files), read_files)

g.add_node("rendezvous", RunnablePassthrough())
g.add_edge(
    [
        n(read_files),
        n(retrieve_with_colbert),
        n(retrieve_with_faiss),
    ],
    "rendezvous",
)  # To merge two parallel nodes, must use this single edge with list of nodes instead of mutiple edges for each nodes

g.add_edge("rendezvous", END)

retrieval_graph = g.compile()

with open("./app/agents/graph_diagrams/retrieval_graph.png", "wb") as f:
    f.write(retrieval_graph.get_graph().draw_mermaid_png())
