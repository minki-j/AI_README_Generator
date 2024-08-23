import uuid
import os
import re
import requests

from fasthtml.common import *

from app.components.step import Step

from app.utils.get_repo_info import get_repo_info
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

    return (
        Title("AI README Generator"),
        Main(cls="container")(
            Titled("AI README Generator"),
            Form(
                post=uri("step_initializer", project_id=str(uuid.uuid4())),
                hx_swap="beforeend",
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
            Div(id="step"),
        ),
    )


async def step_initializer(
    session,
    project_id: str,
    request: Request,
):
    if DEBUG:
        print("DEBUG MODE SKIP GRAPH")  

        db.t.readmes.insert(
            id=project_id,
            user_id=session["session_id"],
            content="",
        )

        step_id = str(uuid.uuid4())
        db.t.steps.insert(
            id=step_id,
            readme_id=project_id,
            step=1,
            feedback_question="TEST QUESTION",
            answer="TEST ANSWER",
        )

        db.t.retrieved_chunks.insert(
            id=str(uuid.uuid4()),
            step_id=step_id,
            content="TEST CHUNK",
        )

        return RedirectResponse(url=f"/{project_id}/{"1"}", status_code=303)

    form = await request.form()
    clone_url = form.get("clone_url")

    github_url_pattern = r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+\.git$"
    if not re.match(github_url_pattern, clone_url):
        return Div(
            f"Error: Invalid GitHub clone URL:{clone_url} /  Please provide a valid URL.",
            cls="error-message",
        )
    

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
            initial_state,
            {"configurable": {"thread_id": project_id}},
        )
        answered_middle_steps = r.get("answered_middle_steps", None)
        retrieved_chunks = r.get("retrieved_chunks", None)
        return RedirectResponse(url=f"/{project_id}/{"1"}", status_code=303)
    except Exception as e:
        return Div(
            f"Error: Something went wrong. Please try again later. ERROR_MESSAGE: {e}",
            cls="error-message",
        )


def step_view(project_id: str, step: str):
    step_data = next(db.t.steps.rows_where(
        "step = 1 AND readme_id= ?", [project_id]
    ), None)

    if step_data:
        retrieved_chunks = next(db.t.retrieved_chunks.rows_where("step_id = ?", [step_data["id"]]), None)
        if retrieved_chunks:
            return Step(
                step_data["feedback_question"],
                step_data["answer"],
                retrieved_chunks["content"],
                id,
                next_step=str(int(step) + 1),
            )
    else:
        return Div(
            f"Error happended while retrieving information from the DB.",
            cls="error-message",
        )



async def step_handler(
    project_id: str,
    step: str,
    request: Request,
    response: Response,
):
    form = await request.form()
    print(f"==>> form: {form}")
    return


def post(
    project_id: str,
    step: str,
    answer: str,
    user_feedback: str,
):
    url = os.getenv("BACKEND_BASE_URL") + "/middleSteps" + f"?/id={id}"

    data = {
        "user_feedback": user_feedback,
    }

    r = requests.post(url, data=data)

    if r.status_code != 200:
        return Div(
            f"Error: Something went wrong. Please try again later.",
            cls="error-message",
        )

    try:
        r_data = r.json()
    except requests.exceptions.JSONDecodeError:
        r_data = {"error": "Failed to decode JSON response"}

    return return_confirmation_box(
        r_data["feedback_question"],
        r_data["answer"],
        r_data["retrieved_chunks"],
        id,
        str(int(step) + 1),
    )


def get():
    url = os.getenv("BACKEND_BASE_URL") + "/middleSteps"

    data = {
        "user_feedback": "retry generating the answer",
    }

    r = requests.post(url, data=data)

    if r.status_code != 200:
        return Div(
            f"Error: Something went wrong. Please try again later.",
            cls="error-message",
        )

    try:
        r_data = r.json()
    except requests.exceptions.JSONDecodeError:
        r_data = {"error": "Failed to decode JSON response"}

    return return_confirmation_box(
        r_data["feedback_question"], r_data["answer"], r_data["retrieved_chunks"], id
    )
