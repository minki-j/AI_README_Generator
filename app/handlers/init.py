import uuid
import os
import re
import requests

from fasthtml.common import *

from app.components.step import StepDiv

from app.utils.get_repo_info import get_repo_info
from app.utils.db_functions import initialize_db, insert_step_db, update_readme_content
from app.assets.step_list import STEP_LIST
from app.agents.main_graph import main_graph
from app.global_vars import DEBUG
from app.db import db


async def step_initializer(
    session,
    request: Request,
    project_id: str,
):
    print("==>> step_initializer")

    form = await request.form()
    clone_url = form.get("clone_url")

    github_url_pattern = r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+\.git$"
    if not re.match(github_url_pattern, clone_url):
        print("Invalid Github clone URL")
        print(f"==>> clone_url: {clone_url}")
        add_toast(
            session,
            "Please enter a valid Github clone URL",
            "error",
        ) #! toast not working
        return Div(Titled("Invalid Github clone URL"), cls="container")

    if os.path.exists(f"/vol"):
        cache_dir = f"/vol/cache"
        os.makedirs(cache_dir, exist_ok=True)
    else:
        print("using local cache instead of Modal's storage")
        cache_dir = "./cache"
        os.makedirs("./cache", exist_ok=True)

    repo_info = get_repo_info(clone_url, cache_dir)
    initial_state = {
        **repo_info,
        "middle_step": STEP_LIST[0],
        "total_number_of_steps": len(STEP_LIST),
    }

    try:
        r = main_graph.invoke(
            {
                **initial_state,
                "previous_step": 0,
                "current_step": 1
            },
            {"configurable": {"thread_id": project_id}},
        )
        answered_middle_steps = r.get("answered_middle_steps", None)
        retrieved_chunks = r.get("retrieved_chunks", None)

    except Exception as e:
        raise e

    r = initialize_db(session["session_id"], project_id, answered_middle_steps[0]["answer"], STEP_LIST[0]["feedback_question"], retrieved_chunks, repo_info["directory_tree_dict"])
    if r:
        full_route = str(request.url_for("step_view"))
        route = full_route.replace(str(request.base_url), '')
        print(f"==>> route: {route}")
        return RedirectResponse(url=f"/{route}?step_num=1&project_id={project_id}", status_code=303)
