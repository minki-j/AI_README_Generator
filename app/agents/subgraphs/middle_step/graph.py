from varname import nameof as n

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough
from langgraph.checkpoint.memory import MemorySaver

from app.utils.converters import to_path_map
from app.agents.state_schema import State

from app.agents.subgraphs.retrieval.graph import subGraph_retrieval


from .answer_middle_step_question import answer_middle_step_question

g = StateGraph(State)
g.set_entry_point("entry")

g.add_node("entry", RunnablePassthrough())
g.add_edge("entry", n(subGraph_retrieval))

g.add_node(n(subGraph_retrieval), subGraph_retrieval)
g.add_edge(n(subGraph_retrieval), n(answer_middle_step_question))

g.add_node(n(answer_middle_step_question), answer_middle_step_question)
g.add_edge(n(answer_middle_step_question), END)

subGraph_middle_step = g.compile()


with open("./app/agents/graph_diagrams/subGraph_middle_step.png", "wb") as f:
    f.write(subGraph_middle_step.get_graph().draw_mermaid_png())
