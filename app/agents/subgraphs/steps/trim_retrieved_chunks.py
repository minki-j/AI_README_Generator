import json

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.global_vars import SKIP_LLM_CALLINGS
from app.agents.state_schema import State
from app.agents.common import chat_model
from app.utils.get_user_picked_file_paths import get_user_picked_file_paths


def refine_retrieved_chunks(state: State) -> State:
    print("\n>>>> NODE: trim_retrieved_chunks")


    prompt = ChatPromptTemplate.from_template(
        """Leave only the code snippets that are most relevant to the question and replace the rest with "...".
        <question>
        {question}
        </question>
        <code_snippets>
        {retrieved_chunks}
        </code_snippets>
        """
    )

    chain = prompt | chat_model.with_structured_output()

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
    
    previous_step_answers = []
    for step_num, step_results in results.items():
        if int(step_num) < int(state["current_step"]):
            previous_step_answers.append(step_results[-1]["answer"])

    response = chain.invoke(
        {
            "question": f"<question>\n{step_question['prompt']}\n</question>\n" if step_question["prompt"] else "",
            "retrieved_chunks": f"<code_snippets>\n{json.dumps(state['retrieved_chunks'], ensure_ascii=False)}\n</code_snippets>\n" if state["retrieved_chunks"] else "",
            "user_feedback": f"<extra_instruction>\n{state.get('user_feedback', '')}\n</extra_instruction>\n" if state.get("user_feedback", "") else "",
            "repo_info": f"<repo_info>\n{repo_info_str}\n</repo_info>\n" if repo_info_str else "",
            "previous_step_answers": f"<key_information>\n{"\n".join(previous_step_answers)}\n</key_information>\n" if previous_step_answers else "",
        }
    )

    trimmed_chunks = {}

    return {
        "retrieved_chunks": {
            "replace": True,
            **trimmed_chunks,
        }
    }
