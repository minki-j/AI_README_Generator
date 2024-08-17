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
from app.langgraph.state_schema import State

from app.langgraph.common import chat_model

from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List


class Readme(BaseModel):
    """This is a Hypothesis of the repository. You must follow the order below when generating the properties
    1. rationale 2. hypothesis 3.queries_for_code_retrieval 4.files_to_open"""


def generate_readme(state: State):
    return {"shorterm_memory": "generate_readme node finished"}
