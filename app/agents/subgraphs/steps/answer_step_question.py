import json
import os
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.state_schema import State
from app.agents.common import chat_model
from app.utils.get_user_picked_file_paths import get_user_picked_file_paths

class Answer(BaseModel):
    ratoionale: str = Field(
        description="Think out loud and step by step to answer the question"
    )
    answer: str = Field(description="The answer to the question")


def answer_step_question(state: State) -> State:
    print("\n>>>> NODE: answer_step_question")

    directory_tree_dict = state["directory_tree_dict"]
    selected_file_paths = get_user_picked_file_paths(directory_tree_dict)

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
        if previous_answers_and_feedbacks and previous_answers_and_feedbacks[-1] != ("ai", answer):
            previous_answers_and_feedbacks.append(("ai", answer)) # TODO: This is a temporary fix to avoid the issue where AI and human messages are not alternating. This cause an erorr for Anthropic API. We need a better way to prevent this. 
    if previous_answers_and_feedbacks:
        first_message = ("human", step_question["prompt"])
        previous_answers_and_feedbacks.insert(0, first_message)

    prompt = ChatPromptTemplate.from_messages(
        [
            *previous_answers_and_feedbacks,
            (
                "human",
                "Answer the question.\n{question}{user_feedback}{retrieved_chunks}{repo_info}{previous_step_answers}",
            ),
        ]
    )

    chain = prompt | chat_model.with_structured_output(Answer)

    if os.getenv("SKIP_LLM_CALLINGS", "false").lower() == "true":
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

    previous_step_answers = []
    for step_num, step_results in results.items():
        if int(step_num) < int(state["current_step"]):
            previous_step_answers.append(step_results[-1]["answer"])

    response = chain.invoke(
        {
            "question": f"<question>{step_question['prompt']}</question>\n" if step_question["prompt"] else "",
            "retrieved_chunks": f"<code_snippets>{json.dumps(state['retrieved_chunks'], ensure_ascii=False)}</code_snippets>\n" if state["retrieved_chunks"] else "",
            "user_feedback": f"<extra_instruction>{state.get('user_feedback', '')}</extra_instruction>\n" if state.get("user_feedback", "") else "",
            "repo_info": f"<repo_info>{repo_info_str}</repo_info>\n" if repo_info_str else "",
            "previous_step_answers": f"<key_information>{', '.join(previous_step_answers)}\n</key_information>\n" if previous_step_answers else "",
        }
    )

    return {
        "results": {
            state["current_step"]: [
                {
                    "answer": response.answer,
                    "opened_files": [],
                    "user_feedback": state.get("user_feedback", ""),
                    "user_selected_files": selected_file_paths,
                }
            ]
        }
    }
