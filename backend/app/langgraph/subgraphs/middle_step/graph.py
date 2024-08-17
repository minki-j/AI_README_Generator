from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough
from langgraph.checkpoint.memory import MemorySaver

from app.utils.converters import to_path_map
from app.langgraph.state_schema import State

from app.langgraph.subgraphs.retrieval.graph import subGraph_retrieval

from .generate_queries import generate_queries
from .answer_middle_step_question import answer_middle_step_question

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(generate_queries))

g.add_node(n(generate_queries), generate_queries)
g.add_edge(n(generate_queries), n(subGraph_retrieval))

g.add_node(n(subGraph_retrieval), subGraph_retrieval)
g.add_edge(n(subGraph_retrieval), n(answer_middle_step_question))

g.add_node(n(answer_middle_step_question), answer_middle_step_question)
g.add_edge(n(answer_middle_step_question), END)

subGraph_middle_step = g.compile(checkpointer=MemorySaver(), interrupt_after=[n(generate_queries)])


# with open("./app/langgraph/graph_diagrams/subGraph_retrieval.png", "wb") as f:
#     f.write(subGraph_retrieval.get_graph().draw_mermaid_png())
