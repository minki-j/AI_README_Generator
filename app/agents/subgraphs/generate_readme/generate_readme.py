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


def generate_readme(state: State):
    return {"generated_readme": "placeholder for generated readme"}
