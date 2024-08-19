import os
import json

from app.langgraph.state_schema import State

from app.langgraph.common import chat_model
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


def answer_middle_step_question(state: State) -> State:
    middle_step = state["middle_step"]
    return {
        "answered_middle_steps": [
            {
                **middle_step,
                "answer": "Placeholder",
            }
        ]
    }
