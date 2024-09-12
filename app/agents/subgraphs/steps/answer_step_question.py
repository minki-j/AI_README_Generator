from app.agents.state_schema import State

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.common import chat_model

from app.global_vars import SKIP_LLM_CALLINGS

import json


class Answer(BaseModel):
    ratoionale: str = Field(
        description="Think out loud and step by step to answer the question"
    )
    answer: str = Field(description="The answer to the question")


def answer_step_question(state: State) -> State:
    print("==>> answer_step_question node started")
    step_question = state["step_question"]

    repo_info_to_look_up = step_question["repo_info_to_look_up"]

    if repo_info_to_look_up:
        repo_info = {key: state[key] for key in repo_info_to_look_up}
        repo_info_str = json.dumps(repo_info, ensure_ascii=False)
    else:
        repo_info_str = ""

    # Add previous answers and feedbacks to the chat history
    results = state.get("results", {})
    current_step_results = results.get(str(state["current_step"]), [])
    previous_answers_and_feedbacks = []
    for previous_result in current_step_results:
        user_feedback = previous_result.get("user_feedback", "")
        answer = previous_result.get("answer", "")
        if user_feedback:
            previous_answers_and_feedbacks.append(("human", user_feedback))
        previous_answers_and_feedbacks.append(("ai", answer))
    if previous_answers_and_feedbacks:
        first_message = ("human", step_question["prompt"])
        previous_answers_and_feedbacks.insert(0, first_message)

    prompt = ChatPromptTemplate.from_messages(
        [
            *previous_answers_and_feedbacks,
            (
                "human",
                "Based on the provided information, answer the following question.\n{question}\n{user_feedback}\n{retrieved_chunks}\n{repo_info}",
            ),
        ]
    )

    chain = prompt | chat_model.with_structured_output(Answer)

    if SKIP_LLM_CALLINGS:
        print("DEBUG MODE: SKIP answer_step_question node")
        return {
            "results": {
                state["current_step"]: [
                    {
                        "answer": "This is a placeholder answer for debugging mode. "
                        * 20,
                        "opened_files": [],
                    }
                ]
            }
        }

    response = chain.invoke(
        {
            "question": f"<question>\n{step_question['prompt']}\n</question>\n",
            "retrieved_chunks": f"<code_snippets>\n{state['retrieved_chunks']}\n</code_snippets>\n",
            "user_feedback": f"<user_feedback>\n{state.get('user_feedback', '')}\n</user_feedback>\n",
            "repo_info": f"<repo_info>\n{repo_info_str}\n</repo_info>\n",
        }
    )

    return {
        "results": {
            state["current_step"]: [
                {
                    "answer": response.answer,
                    "opened_files": [],
                    "user_feedback": state.get("user_feedback", ""),
                    "user_selected_files": [],  # TODO
                }
            ]
        }
    }
