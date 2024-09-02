from app.agents.state_schema import State

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.agents.common import chat_model

from app.global_vars import SKIP_LLM_CALLINGS


class Answer(BaseModel):
    ratoionale: str = Field(
        description="Think out loud and step by step to answer the question"
    )
    answer: str = Field(description="The answer to the question")


def answer_middle_step_question(state: State) -> State:
    print("==>> answer_middle_step_question node started")
    middle_step = state["step_question"]

    prompt = ChatPromptTemplate.from_template(
        """
Based on the retrieved code snippets, answer the following question. 
<questions>
{question}
</questions>

<code_snippets>
{retrieved_chunks}
</code_snippets>
"""
    )

    chain = prompt | chat_model.with_structured_output(Answer)

    if SKIP_LLM_CALLINGS:
        print("DEBUG MODE. SKIP answer_middle_step_question")
        return {
            "results": {
                state["current_step"]: [{
                    "answer": "DEBUG MODE",
                    "opened_files": [],
                }]
            }
        }

    response = chain.invoke(
        {
            "question": middle_step["prompt"],
            "retrieved_chunks": state["retrieved_chunks"],
        }
    )

    print("response: ", response)
    answer = response.answer
    print(f"==>> answer: {answer}")

    return {
        "results": {
            state["current_step"]: [{
                "answer": answer,
                "opened_files": [],
            }]
        }
    }
