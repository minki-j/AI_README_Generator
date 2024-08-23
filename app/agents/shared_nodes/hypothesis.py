from varname import nameof as n
from enum import Enum
import pendulum
import json

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    SystemMessage,
    HumanMessage,
)
from app.agents.state_schema import State

from app.agents.common import chat_model

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class Hypothesis(BaseModel):
    """This is a Hypothesis of the repository. You must follow the order below when generating the properties
    1. rationale 2. hypothesis 3.queries_for_code_retrieval 4.files_to_open"""

    rationale: str = Field(
        description="The reason for the hypothesis and the queries to retreive codes for confirmation"
    )
    hypothesis: str
    queries: List[str] = Field(
        description="A list of search queries used to retrieve relevant code snippets. These snippets will be used to verify the hypothesis. The retrieval process combines BM25 and embedding vector search techniques for improved accuracy. Order the queries from most imporant to least important. You can choose up to 3 queries."
    )
    files_to_open: List[str] = Field(
        description="The list of file pathes from the directory tree that you need to open to confirm the hypothesis. You can choose up to 3 files."
    )


def generate_hypothesis(state: State):
    print("==>> generate_hypothesis node started")
    hypothesis_count = state["hypothesis_count"]

    hypothesis_level_map = {
        0: [0],
        1: [1, 2, 3],
        2: [4, 5, 6, 7, 8, 9],
    }

    if hypothesis_count in hypothesis_level_map[0]:
        system_message = SystemMessage(
            content="""
            You are a sesoned software engineer tasked to understand the provided repository. It includes meta data such as title, description, directory tree, and packages used. 
            Based on the information, make 1) a hypothesis about the project, 2) file pathes that you want to open to confirm the hypothesis based on the directory tree, and 3) queries that could be used to retrieve relevant code snippets to validate your hypothesis.
            The queries are english sentences that describe functionality or patterns in the code that you need to look at to confirm the hypothesis. For example, if your hypothsis includes "this repo contains third party authentications, then queries could be "code for third party authentication", "login with google" etc.
            """
        )
    elif hypothesis_count in hypothesis_level_map[1]:
        system_message = SystemMessage(
            content=f"""
            You are a seasoned software engineer tasked to understand the provided repository. 
            In the previous step, you have created a highest level analysis of the repository. 
            Now, you need to create a hypothesis for more specific functionalities or patterns in the code. 

            Make sure that your hypothesis is more narrower and specific compared to those in the previous level.
            Don't include the same phrases or patterns that are already in the previous level hypothesis. For example, you could just say "It includes" instead of "This repositories is about ... that includes ..."
            Make sure that your hypothesis is not overlapping with other hypothesis that are in the same level.


            Previous level hypothesis: 
            {"\n".join([h["hypothesis"] for h in state["final_hypotheses"] if h["hypothesis_count"] in hypothesis_level_map[0]])}     


            Same level other hypothesis: 
            {"\n".join([h["hypothesis"] for h in state["final_hypotheses"] if h["hypothesis_count"] in hypothesis_level_map[1]])}
            """
        )
    else:
        raise ValueError(f"Invalid hypothesis count: {hypothesis_count}")

    human_message = HumanMessage(
        content=f"""
        Here are the meta data of the repository:
        Title: {state["title"]}
        Description: {state["repo_description_by_user"]}
        Packages used: {", ".join(state["packages_used"])}
        Directory Tree: {state["directory_tree"]}

        Make sure that your hypothesis is more narrower and specific compared to those in the previous level.
        Don't include the same phrases or patterns that are already in the previous level hypothesis. For example, you could just say "It includes" instead of "This repositories is about ... that includes ..."
        Make sure that your hypothesis is not overlapping with other hypothesis that are in the same level.
        """
    )

    prompt = ChatPromptTemplate.from_messages([system_message, human_message])

    chain = prompt | chat_model.with_structured_output(Hypothesis)

    response = chain.invoke({})
    response_dict = response.dict()

    return {"candidate_hypothesis": response_dict}


def evaluate_hypothesis(state: State):
    print("==>> evaluate_hypothesis node started")

    hypothesis_dict = state["candidate_hypothesis"]

    class Evaluation(BaseModel):
        """This is a result of the evaluation. You need to first provide the rationale of the result and then the modified_hypothesis."""

        rationale: str = Field(
            description="Think out loud how you examined the hypothesis with the opened files. You must provide this BEFORE modified_hypothesis to ensure a better and thoughful examiniation process.",
        )
        modified_hypothesis: str = Field(
            description="This is the modified hypothesis based on the evaluation results.",
        )
        queries: List[str] = Field(
            description="The list of files that you need to open to confirm the modified hypothesis."
        )

    prompt = ChatPromptTemplate.from_template(
        """
        You are a seasoned software engineer tasked to understand the provided repository. In the previous step, you've already proposed a hypothesis about this repo and chosen files to look into to confirm your hypothesis. 
        Now all the files are opened and collected for you. Examine if your hypothesis is coherent with the actual content of the files. 
        If the opened files doesn't contain the information you need, you can request to open more files.

        Hypothesis: {hypothesis}

        Files to refer(total: {number_of_retrieved_code}):
        {retrieved_code_snippets}
        """
    )

    chain = prompt | chat_model.with_structured_output(Evaluation)

    response = chain.invoke(
        {
            "hypothesis": hypothesis_dict["hypothesis"],
            "number_of_retrieved_code" : len(state["retrieved_code_snippets"]),
            "retrieved_code_snippets": state["retrieved_code_snippets"],
        }
    )

    result = response.dict()
    result["original_hypothesis"] = hypothesis_dict["hypothesis"]
    result["queries"] = hypothesis_dict["queries"]
    result["opened_files"] = state["opened_files"]
    result["hypothesis_count"] = state["hypothesis_count"]

    candidate_hypothesis = {
        "rationale": result["rationale"],
        "hypothesis": result["modified_hypothesis"],
        "queries": result["queries"],
        "files_to_open": [],
        "hypothesis_count": state["hypothesis_count"],
    }

    return {"analysis_results": [result], "candidate_hypothesis": candidate_hypothesis}
