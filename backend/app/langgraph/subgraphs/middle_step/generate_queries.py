import os
import json

from app.langgraph.state_schema import State

from app.langgraph.common import chat_model
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


def generate_queries(state: State):
    print("==>> generate_queries node started")
    return {"shortterm_memory": ["generate_queries node finished"]}
