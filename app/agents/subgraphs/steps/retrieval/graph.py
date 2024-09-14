from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.utils.converters import to_path_map
from app.agents.state_schema import State

from .retrieve_with_path import read_files, validate_user_chosen_files
from .validate_file_path import validate_file_paths_from_LLM, correct_file_paths
from .retrieve_with_colbert import retrieve_with_colbert
from .retrieve_with_faiss import retrieve_with_faiss

from app.agents.state_schema import RetrievalMethod
from app.global_vars import DEFAULT_RETRIEVAL

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node(
    "entry",
    lambda _: {
        "retrieved_chunks": "RESET",
        "valid_paths": "RESET",
    },
)
g.add_edge("entry", n(validate_user_chosen_files))
g.add_edge("entry", n(validate_file_paths_from_LLM))
g.add_edge("entry", "choose_retrieval_method")

g.add_node("choose_retrieval_method", RunnablePassthrough())


def choose_retrieval_method(state):
    retrieval_method = RetrievalMethod[state.get("retrieval_method", DEFAULT_RETRIEVAL)]
    if retrieval_method == RetrievalMethod.COLBERT:
        return n(retrieve_with_colbert)
    elif retrieval_method == RetrievalMethod.FAISS:
        return n(retrieve_with_faiss)
    else:
        raise ValueError(
            f"Invalid retrieval method: {retrieval_method} / type: {type(retrieval_method)}"
        )


g.add_conditional_edges(
    "choose_retrieval_method",
    choose_retrieval_method,
    to_path_map([n(retrieve_with_colbert), n(retrieve_with_faiss)]),
)

g.add_node(n(validate_user_chosen_files), validate_user_chosen_files)
g.add_edge(n(validate_user_chosen_files), n(read_files))

g.add_node(n(retrieve_with_colbert), retrieve_with_colbert)
g.add_node(n(retrieve_with_faiss), retrieve_with_faiss)

g.add_node(n(validate_file_paths_from_LLM), validate_file_paths_from_LLM)
g.add_conditional_edges(
    n(validate_file_paths_from_LLM),
    lambda state: (
        n(correct_file_paths)
        if len(state["invalid_paths"]) > 0 and state["validate_count"] < 3
        else n(read_files)
    ),
    to_path_map(
        [
            n(correct_file_paths),
            n(read_files),
        ]
    ),
)

g.add_node(n(correct_file_paths), correct_file_paths)
g.add_edge(n(correct_file_paths), n(validate_file_paths_from_LLM))

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

subGraph_retrieval = g.compile()

with open("./app/agents/graph_diagrams/subGraph_retrieval.png", "wb") as f:
    f.write(subGraph_retrieval.get_graph().draw_mermaid_png())
