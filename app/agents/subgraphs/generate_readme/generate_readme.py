import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
)
from app.agents.state_schema import State

from app.agents.llm_models import chat_model

from langchain_core.pydantic_v1 import BaseModel, Field

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
                "Based on the collected information about the Github repository, write a README.\n{step_answers}\n{repo_info}\n Make sure it is a proper markdown format.", 
            ),
        ]
    )

    chain = prompt | chat_model.with_structured_output(Readme)

    # if os.getenv("SKIP_LLM_CALLINGS", "false").lower() == "true":
    #     print("DEBUG MODE: SKIP answer_step_question node")
    #     return {
    #         "generated_readme": "DEBUG MODE: SKIP generate_readme node",
    #         "results": {
    #             "final": [
    #                 {
    #                     "answer": "DEBUG MODE: SKIP generate_readme node",
    #                     "opened_files": [],
    #                 }
    #             ]
    #         },
    #     }

    readme = chain.invoke(
        {
            "step_answers": f"<step_answers>{', '.join(step_answers)}</step_answers>\n" if step_answers else "",
            "repo_info": f"<repo_info>{', '.join(repo_info)}</repo_info>\n" if repo_info else "",
        }
    )

    readme_content = readme.content

    return {"generated_readme": readme_content,
            "results": {
                "final": [{
                    "answer": readme_content,
                    "opened_files": [],
                }]
            }
        }
