from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.agents.state_schema import State

from .answer_step_question import answer_step_question
from .refine_retrieved_chunks import refine_retrieved_chunks
from .retrieval.graph import subGraph_retrieval
from app.utils.converters import to_path_map
from app.utils.get_user_picked_file_paths import get_user_picked_file_paths

def do_need_retrieval(state: State):
    print("\n>>>> EDGE: do_need_retrieval")

    user_picked_file_paths = get_user_picked_file_paths(state["directory_tree_dict"])
    print(f"==>> user_picked_file_paths: {len(user_picked_file_paths)}")
    if len(user_picked_file_paths) > 0 or state["step_question"]["retrieval_needed"]:
        return n(subGraph_retrieval)
    else:
        return n(answer_step_question)


g = StateGraph(State)
g.set_entry_point("do_need_retrieval")

g.add_node("do_need_retrieval", RunnablePassthrough())
g.add_conditional_edges(
    "do_need_retrieval",
    do_need_retrieval,
    to_path_map([n(subGraph_retrieval), n(answer_step_question)]),
)

g.add_node(n(subGraph_retrieval), subGraph_retrieval)
g.add_edge(n(subGraph_retrieval), n(refine_retrieved_chunks))

g.add_node(n(refine_retrieved_chunks), refine_retrieved_chunks)
g.add_edge(n(refine_retrieved_chunks), n(answer_step_question))

g.add_node(n(answer_step_question), answer_step_question)
g.add_edge(n(answer_step_question), END)

subGraph_steps = g.compile()


with open("./app/agents/graph_diagrams/subGraph_steps.png", "wb") as f:
    f.write(subGraph_steps.get_graph().draw_mermaid_png())
