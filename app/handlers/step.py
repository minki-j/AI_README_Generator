import uuid
import os
import re
import requests
import json
from fasthtml.common import *

from app.components.step import StepDiv

from app.utils.get_repo_info import get_repo_info
from app.utils.db_functions import initialize_db, insert_step_db, update_readme_content
from app.assets.step_list import STEP_LIST
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

    form = await request.form()
    if len(form) == 0: # when "next step" button is clicked
        user_feedback = None
        directory_tree_str = db.t.readmes.get(project_id).directory_tree_str
        directory_tree_dict = None
    else: # when "apply feedback" button is clicked
        print("==>> form: ", form)
        user_feedback = form.get("user_feedback")
        directory_tree_str = form.get("directory_tree_str")
        directory_tree_dict = json.loads(directory_tree_str)

    try:
        config = {"configurable": {"thread_id": project_id}}
        main_graph.update_state(
            config,
            values={
                # **(last_state.values if last_state is not None else {}),
                "user_feedback_list": [user_feedback],
                "directory_tree_dict": directory_tree_dict,
                "current_step": step_num,
                "middle_step": STEP_LIST[int(step_num)],
            },
        )
        r = main_graph.invoke(None, config)
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
        directory_tree_str,
    )

    if r:
        # full_route = str(request.url_for("step_view"))
        # route = full_route.replace(str(request.base_url), '')
        # return RedirectResponse(url=f"/{route}?step_num={step_num}&project_id={project_id}", status_code=303)
        return StepDiv(
            STEP_LIST[int(step_num)]["feedback_question"],
            answered_middle_steps[-1]["answer"],
            retrieved_chunks,
            project_id,
            str(int(step_num) + 1),
            len(STEP_LIST),
            directory_tree_str,
            is_last_step=True if int(step_num) == len(STEP_LIST) - 1 else False,
        )
    else:
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )


async def generate_readme(project_id: str, request: Request):
    print("==>> generate_readme")
    if DEBUG:
        print("DEBUG MODE. SKIP GRAPH")
        r = update_readme_content(project_id, "DEBUG MODE. README GENERATED")
        if r:
            full_route = str(request.url_for("generate_readme"))
            route = full_route.replace(str(request.base_url), "")
            return RedirectResponse(
                url=f"/{route}?project_id={project_id}", status_code=303
            )
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
        full_route = str(request.url_for("generate_readme"))
        route = full_route.replace(str(request.base_url), "")
        return RedirectResponse(
            url=f"/{route}?project_id={project_id}", status_code=303
        )
    else:
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )
