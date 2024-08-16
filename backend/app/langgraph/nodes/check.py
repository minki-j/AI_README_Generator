from varname import nameof as n
from difflib import SequenceMatcher

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.langgraph.common import chat_model
from app.langgraph.state_schema import State

from app.langgraph.subgraphs.retrieval.graph import subGraph_retrieval
from .hypothesis import generate_hypothesis

# We are NOT going to use LLM here because judging whether something is enough or not is a subjective and resource-dependent task. LLMs are not suitable for this type of task.
def do_we_need_more_retrieval(state: State):
    print("==> do_we_need_more_retrieval")

    # If the last hypothesis is the same as the original hypothesis, stop rerieval
    # Used SequenceMatcher to allow some flexibility
    if len(state["analysis_results"]) > 0:
        modified_hypotheses = state["analysis_results"][-1]["modified_hypothesis"]
        original_hypothesis = state["analysis_results"][-1]["original_hypothesis"]
        if SequenceMatcher(None, modified_hypotheses, original_hypothesis).ratio() > 0.8:
            return "put_candidate_as_final_hypothesis"
        
    if state["retrieval_count"] >= 1:
        return "put_candidate_as_final_hypothesis"
    else:
        return n(subGraph_retrieval)


def do_we_have_enough_hypotheses(state: State):
    hypotheses = state["final_hypotheses"]
    print(f"collected {len(hypotheses)} hypotheses so far")

    if len(hypotheses) >= 4:
        return "__end__"
    else:
        return n(generate_hypothesis)
