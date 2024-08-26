import uuid
import os
import re
import requests

from fasthtml.common import *

from app.components.step import Step

from app.utils.get_repo_info import get_repo_info
from app.utils.db_functions import initialize_db, insert_step_db
from app.data.step_list import step_list
from app.agents.main_graph import main_graph
from app.global_vars import DEBUG
from app.db import db


def home_view(session):
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        db.t.users.insert(
            id=session["session_id"],
            name="",
            email="",
            password="",
        )
        add_toast(session, f"Session ID created: {session['session_id']}", "info")

    return Div(cls="container")(
        Title("AI README Generator"),
        Main(id="step")(
            Titled("AI README Generator"),
            Form(
                post=uri("step_initializer", project_id=str(uuid.uuid4())),
                hx_swap="outerHTML",
                hx_target="#step",
                hx_indicator="#loader",
                hx_replace_url="true",
            )(
                Div(cls="container row", style="gap:1rem;")(
                    P(
                        "Having trouble writing a killer README? No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. 🚀 Let’s get started!",
                    ),
                    Group(Input(
                        placeholder="Github Clone URL",
                        name="clone_url",
                        id="clone_url_input",
                        value="https://github.com/minki-j/AI_README_Generator.git",
                    ),
                    Button("Start", cls="btn-primary"),)
                ),
            ),
            Div(
                id="loader",
                cls="my-indicator row center-xs",
            )(
                Div(
                    cls="col-xs-6",
                )(
                    P(
                        "Loading...",
                        cls="",
                    ),
                ),
            ),
        ),
    )


async def step_initializer(
    session,
    project_id: str,
    request: Request,
):
    print("==>> step_initializer")
    if DEBUG:
        print("DEBUG MODE. SKIP GRAPH")  
        r = initialize_db(session["session_id"], project_id, "test_answer", "test_feedback_question", ["test_retrieved_chunks"])
        if r:
            return RedirectResponse(url=f"/{project_id}/{"0"}", status_code=303)
        else:
            return Div(
                "Error: Something went wrong. Please try again later.",
                cls="error-message",
            )

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
        "middle_step": step_list[0],
        "total_number_of_steps": len(step_list),
    }

    try:
        r = main_graph.invoke(
            {
                **initial_state,
                "current_step": 0
            },
            {"configurable": {"thread_id": project_id}},
        )
        answered_middle_steps = r.get("answered_middle_steps", None)
        retrieved_chunks = r.get("retrieved_chunks", None)

    except Exception as e:
        raise e
    
    r = initialize_db(session["session_id"], project_id, answered_middle_steps[0]["answer"], step_list[0]["feedback_question"], retrieved_chunks)
    if r:
        return RedirectResponse(url=f"/step/{"0"}/{project_id}", status_code=303) #TODO: need to be able to use uri instead of hardcoding


def step_view(step: str, project_id: str):
    print("==>> step_view")
    step_data = next(db.t.steps.rows_where(
        "step = ? AND readme_id= ?", [step, project_id]
    ), None)

    if step_data:
        retrieved_chunks = []
        for chunk in db.t.retrieved_chunks.rows_where("step_id = ?", [step_data["id"]]):
            retrieved_chunks.append(chunk["content"])
        return Main(id="step")(
            Titled("AI README Generator"),
            Step(
                step_data["feedback_question"],
                step_data["answer"],
                retrieved_chunks,
                project_id,
                next_step=str(int(step) + 1),
            )
        )
    else:
        return Main(id="step")(
            Titled("AI README Generator"),
            Div(
            f"Error happended while retrieving information from the DB.",
            cls="error-message",
            )
        )


async def step_handler(
    session,
    project_id: str,
    step: str,
    request: Request,
):
    if int(step) > len(step_list) - 1:
        return Main(id="step")(
            Titled("AI README Generator"),
            Div()(
                P("Congratulations! You have completed the README generation process."),
            )
        )
    print("==>> step_handler for step: ", step)
    if DEBUG:
        print("DEBUG MODE. SKIP GRAPH")  
        r = insert_step_db(step, project_id,  "test_feedback_question", "test_answer",["test_retrieved_chunks"])
        if r:
            return Main(id="step")(
                Titled("AI README Generator"),
                Step(
                    "DEBUG MODE",
                    "DEBUG MODE",
                    ["DEBUG MODE"],
                    project_id,
                    next_step=str(int(step) + 1),
                )
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
        last_state = None
        for state in main_graph.get_state_history(config):
            last_state = state
            break
        print("==>> last_state: ", last_state)
        if last_state is None:
            raise Exception("No state found in the graph")
        main_graph.update_state(
            config,
            values={
                "user_feedback_list": [user_feedback],
                "current_step": int(step),
                "middle_step": step_list[int(step)],
                **(last_state.values if last_state is not None else {})
            }
        )
        r = main_graph.invoke(
            None,
            config,
        )
        answered_middle_steps = r.get("answered_middle_steps", None)
        retrieved_chunks = r.get("retrieved_chunks", None)
        generated_readme = r.get("generated_readme", None)
 
    except Exception as e:
        raise e
    
    r = insert_step_db(
        step, 
        project_id,
        step_list[int(step)]["feedback_question"], 
        answered_middle_steps[-1]["answer"],
        retrieved_chunks,
    )
    
    if r:
        return Main(id="step")(
            Titled("AI README Generator"),
            Step(
                step_list[int(step)]["feedback_question"],
                answered_middle_steps[-1]["answer"],
                retrieved_chunks,
                project_id,
                next_step=str(int(step) + 1),
            )
        )
    else:
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )
