from varname import nameof as n
from enum import Enum
import pendulum
import json

from langchain_core.prompts import ChatPromptTemplate
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

class Readme(BaseModel):
    content: str = Field(description="The generated README in markdown format")

def generate_readme(state: State):
    print("\n>>>> NODE: generate_readme")

    repo_info = []
    repo_info.append(f"Directory Tree: {state['directory_tree']}")
    repo_info.append(f"Packages Used: {state['packages_used']}")


    step_answers = []
    for step_num, results in state["results"].items():
        step_answers.append(results[-1]["answer"])

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "Based on the collected information about the Github repository, write a README.\n{step_answers}\n{repo_info}\n",
            ),
        ]
    )

    chain = prompt | chat_model.with_structured_output(Readme)

    readme = chain.invoke(
        {
            "step_answers": f"<step_answers>\n{"\n".join(step_answers)}\n</step_answers>\n" if step_answers else "",
            "repo_info": f"<repo_info>\n{"\n".join(repo_info)}\n</repo_info>\n" if repo_info else "",
        }
    )

    return {"generated_readme": readme.content,
            "results": {
                "final": [{
                    "answer": readme.content,
                    "opened_files": [],
                }]
            }
        }
