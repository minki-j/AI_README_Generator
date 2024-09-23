from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.agents.state_schema import State

from .answer_step_question import answer_step_question
from .refine_retrieved_chunks import refine_retrieved_chunks
from app.agents.subgraphs.retrieval.graph import retrieval_graph
from app.utils.converters import to_path_map
from app.utils.get_user_picked_file_paths import get_user_picked_file_paths

def do_need_retrieval(state: State):
    print("\n>>>> EDGE: do_need_retrieval")
    user_picked_file_paths = get_user_picked_file_paths(state["directory_tree_dict"])
    if len(user_picked_file_paths) > 0 or state["step_question"]["retrieval_needed"]:
        print("Retrieval needed")
        return n(retrieval_graph)
    else:
        print("Retrieval not needed")
        return n(answer_step_question)


g = StateGraph(State)
g.set_entry_point("do_need_retrieval")

g.add_node("do_need_retrieval", RunnablePassthrough())
g.add_conditional_edges(
    "do_need_retrieval",
    do_need_retrieval,
    to_path_map([n(retrieval_graph), n(answer_step_question)]),
)

g.add_node(n(retrieval_graph), retrieval_graph)
g.add_edge(n(retrieval_graph), n(refine_retrieved_chunks))

g.add_node(n(refine_retrieved_chunks), refine_retrieved_chunks)
g.add_edge(n(refine_retrieved_chunks), n(answer_step_question))

g.add_node(n(answer_step_question), answer_step_question)
g.add_edge(n(answer_step_question), END)

steps_graph = g.compile()


with open("./app/agents/graph_diagrams/steps_graph.png", "wb") as f:
    f.write(steps_graph.get_graph().draw_mermaid_png())
