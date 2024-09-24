from varname import nameof as n
from typing import Annotated, TypedDict, Dict, List

from langgraph.graph import END, StateGraph
from langchain_core.runnables import RunnablePassthrough

from app.utils.converters import to_path_map

from .characters import have_a_chat_time


class DecisionMakerState(TypedDict):
    def append_list(original: List[str], new_lines: List[str]) -> List[str]:
        if new_lines == "RESET":
            return []
        return original.append(new_lines)

    problem_statement: str
    context: Dict[str, str]
    lines: Annotated[List[str], append_list]
    vote: Dict[str, int]  # character_name: vote_index
    vote_history: Annotated[
        List[(str, Dict[int, str], Dict[str, int])], append_list
    ]  # (agenda, candidates, results)
    is_discussion_finished: bool
    is_round_finished: bool
    round_loop_count: int


g = StateGraph(DecisionMakerState)
g.set_entry_point("is_discussion_finished")

g.add_node("is_discussion_finished", RunnablePassthrough())
g.add_conditional_edges(
    "is_discussion_finished",
    lambda state: END if state["is_discussion_finished"] else "next_round",
    to_path_map(["next_round", END]),
)

g.add_node("next_round", RunnablePassthrough())
g.add_edge("next_round", n(have_a_chat_time))

g.add_node(n(have_a_chat_time), have_a_chat_time)
g.add_edge(n(have_a_chat_time), "is_round_finished")

g.add_node("is_round_finished", RunnablePassthrough())
g.add_conditional_edges(
    "is_round_finished",
    lambda state: (
        "is_discussion_finished" if state["is_round_finished"] else n(have_a_chat_time)
    ),
    to_path_map(["is_discussion_finished", n(have_a_chat_time)]),
)

decision_maker_graph = g.compile()

with open("./app/agents/graph_diagrams/decision_maker_graph.png", "wb") as f:
    f.write(decision_maker_graph.get_graph().draw_mermaid_png())
