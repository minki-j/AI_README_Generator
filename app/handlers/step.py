import uuid
import os
import re
import requests

from fasthtml.common import *

from app.components.step import Step

from app.utils.get_repo_info import get_repo_info
from app.utils.db_functions import initialize_db, insert_step_db, update_readme_content
from app.data.step_list import STEP_LIST
from app.agents.main_graph import main_graph
from app.global_vars import DEBUG
from app.db import db


async def step_handler(
    session,
    request: Request,
    project_id: str,
    step_num: int,
):
    print("==>> step_handler for step: ", step_num)
    if DEBUG:
        print("DEBUG MODE. SKIP GRAPH")
        r = insert_step_db(
            step_num,
            project_id,
            "test_feedback_question",
            "test_answer",
            ["test_retrieved_chunks"],
        )
        if r:
            RedirectResponse(
                url=f"step?step_num={step_num}&project_id={project_id}", status_code=303
            )
        else:
            return Div(
                "Error: Something went wrong. Please try again later.",
                cls="error-message",
            )

    form = await request.form()
    answer = form.get("answer")
    user_feedback = form.get("user_feedback")

    if os.path.exists(f"/vol"):
        cache_dir = f"/vol/cache"
        os.makedirs(cache_dir, exist_ok=True)
    else:
        print("using cache in local machine instead of the one in Modal's storage")
        cache_dir = "./cache"
        os.makedirs("./cache", exist_ok=True)

    try:
        config = {"configurable": {"thread_id": project_id}}
        # last_state = None
        # for state in main_graph.get_state_history(config):
        #     last_state = state
        #     break
        # print("==>> last_state: ", last_state)
        # if last_state is None:
        #     raise Exception("No state found in the graph")
        print(f"update state with curent_step: ", int(step_num))
        main_graph.update_state(
            config,
            values={
                # **(last_state.values if last_state is not None else {}),
                "user_feedback_list": [user_feedback],
                "current_step": int(step_num),
                "middle_step": STEP_LIST[int(step_num)],
            },
        )
        r = main_graph.invoke(
            None,
            config,
        )
        answered_middle_steps = r.get("answered_middle_steps", None)
        retrieved_chunks = r.get("retrieved_chunks", None)

    except Exception as e:
        raise e

    r = insert_step_db(
        step_num,
        project_id,
        STEP_LIST[int(step_num)]["feedback_question"],
        answered_middle_steps[-1]["answer"],
        retrieved_chunks,
    )

    if r:
        return RedirectResponse(
            url=f"step?step_num={step_num}&project_id={project_id}", status_code=303
        )
    else:
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )


async def generate_readme(project_id: str):
    print("==>> generate_readme")
    if DEBUG:
        print("DEBUG MODE. SKIP GRAPH")
        r = update_readme_content(project_id, "DEBUG MODE. README GENERATED")
        if r:
            return RedirectResponse(url=f"/step/final?project_id={project_id}", status_code=303)
        else:
            return Div(
                "Error: Something went wrong. Please try again later.",
                cls="error-message",
            )

    config = {"configurable": {"thread_id": project_id}}
    r = main_graph.update_state(
        config,
        values={
            "current_step": len(STEP_LIST),
        },
    )
    r = main_graph.invoke(
        None,
        config,
    )
    generated_readme = r.get("generated_readme", None)
    print(f"==>> generated_readme: {generated_readme}")
    r = update_readme_content(project_id, generated_readme)
    if r:
        return RedirectResponse(
            url=f"/step/final?project_id={project_id}", status_code=303
        )
    else:
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )
