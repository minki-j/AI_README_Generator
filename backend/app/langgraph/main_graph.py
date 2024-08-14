from varname import nameof as n

from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnablePassthrough

from app.langgraph.state_schema import State
from app.utils.converters import to_path_map

from app.langgraph.subgraphs.retrieval.graph import subGraph_retrieval

from app.langgraph.nodes.hypothesis import generate_hypothesis, evaluate_hypothesis
from app.langgraph.nodes.check import (
    do_we_need_more_retrieval,
    do_we_have_enough_hypotheses,
)
from app.langgraph.nodes.clone_repo import clone_repo

g = StateGraph(State)
g.add_node("entry", RunnablePassthrough())
g.set_entry_point("entry")
g.add_edge("entry", n(clone_repo))

g.add_node(n(clone_repo), clone_repo)
g.add_edge(n(clone_repo), n(generate_hypothesis))

g.add_node(n(generate_hypothesis), generate_hypothesis)
g.add_edge(n(generate_hypothesis), n(subGraph_retrieval))

g.add_node(n(subGraph_retrieval), subGraph_retrieval)
g.add_edge(n(subGraph_retrieval), n(evaluate_hypothesis))

g.add_node(n(evaluate_hypothesis), evaluate_hypothesis)
g.add_conditional_edges(
    n(evaluate_hypothesis),
    do_we_need_more_retrieval,
    to_path_map(
        [
            "put_candidate_as_final_hypothesis",
            n(subGraph_retrieval),
        ]
    ),
)

g.add_node(
    "put_candidate_as_final_hypothesis",
    lambda state: {"final_hypotheses": [state["candidate_hypothesis"]], "hypothesis_count": state["hypothesis_count"] + 1},
)
g.add_edge("put_candidate_as_final_hypothesis", n(do_we_have_enough_hypotheses))

g.add_node(n(do_we_have_enough_hypotheses), RunnablePassthrough())
g.add_conditional_edges(
    n(do_we_have_enough_hypotheses),
    do_we_have_enough_hypotheses,
    to_path_map(
        [
            n(generate_hypothesis),
            "__end__",
        ]
    ),
)

main_graph = g.compile(
    checkpointer=MemorySaver(), interrupt_before=[n(clone_repo), n(generate_hypothesis)]
)


# with open("./app/langgraph/graph_diagrams/main_graph.png", "wb") as f:
#     f.write(main_graph
# .get_graph().draw_mermaid_png())
