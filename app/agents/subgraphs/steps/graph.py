from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.agents.state_schema import State

from .answer_step_question import answer_step_question
from .retrieval.graph import subGraph_retrieval
from app.utils.converters import to_path_map


def do_need_to_retrieve(state: State):
    if state["step_question"]["retrieval_needed"]:
        return n(subGraph_retrieval)
    else:
        return n(answer_step_question)


g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_conditional_edges(
    "entry",
    do_need_to_retrieve,
    to_path_map([n(subGraph_retrieval), n(answer_step_question)]),
)

g.add_node(n(subGraph_retrieval), subGraph_retrieval)
g.add_edge(n(subGraph_retrieval), n(answer_step_question))

g.add_node(n(answer_step_question), answer_step_question)
g.add_edge(n(answer_step_question), END)

subGraph_steps = g.compile()


with open("./app/agents/graph_diagrams/subGraph_steps.png", "wb") as f:
    f.write(subGraph_steps.get_graph().draw_mermaid_png())
