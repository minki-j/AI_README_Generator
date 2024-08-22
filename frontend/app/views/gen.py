import uuid
import os
import re
import requests

from fasthtml.common import *

from components.step import Step


def home_view(session, request: Request):

    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        add_toast(session, f"Session ID created: {session['session_id']}", "info")

    project_id = str(uuid.uuid4())
    session["project_id"] = project_id

    post_url = uri("step_initializer", project_id=project_id)
    print(f"==>> post_url: {post_url}")

    return (
        Title("AI README Generator"),
        Main(cls="container")(
            Titled("AI README Generator"),
            P(
                "Having trouble writing a killer README? No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. 🚀 Let’s get started!",
            ),
            Form(
                post=post_url,
                hx_swap="beforeend",
                hx_target="#step",
                hx_indicator="#loader",
                hx_replace_url="true",
            )(
                Group(
                    Input(
                        placeholder="Github Clone URL",
                        name="clone_url",
                        id="clone_url_input",
                        value="https://github.com/minki-j/AI_README_Generator.git",
                    ),
                    Button("Start", cls="btn-primary"),
                ),
            ),
            Div(
                id="loader",
                cls="my-indicator row center-xs",
            )(
                Div(
                    cls="col-xs-6",
                )(
                    # Img(src="/img/loading.jpeg"),
                    P(
                        "Loading...",
                        cls="",
                    ),
                ),
            ),
            Div(id="step"),
        ),
    )


def step_view(project_id: str, step: str):
    url = os.getenv("BACKEND_BASE_URL") + "/gen" + f"?id={id}" + f"&step={step}"
    print("Request url: ", url)

    r = requests.get(url)

    if r.status_code != 200:
        return Div(
            f"Error: Something went wrong. Please try again later.",
            cls="error-message",
        )

    try:
        r_data = r.json()
    except requests.exceptions.JSONDecodeError:
        r_data = {"error": "Failed to decode JSON response"}

    return Step(
        r_data["feedback_question"],
        r_data["answer"],
        r_data["retrieved_chunks"],
        id,
        str(int(step) + 1),
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


async def step_initializer(
    project_id: str,
    request: Request,
):

    form = await request.form()
    clone_url = form.get("clone_url")

    # Check if the URL is a valid GitHub clone URL
    github_url_pattern = r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+\.git$"
    if not re.match(github_url_pattern, clone_url):
        return Div(
            f"Error: Invalid GitHub clone URL:{clone_url} /  Please provide a valid URL.",
            cls="error-message",
        )
    url = os.getenv("BACKEND_BASE_URL") + "/start" + f"?id={project_id}"

    r = requests.post(url, data={"clone_url": clone_url})

    if r.status_code != 200:
        return Div(
            f"Error: Something went wrong. Please try again later.",
            cls="error-message",
        )
    else:
        return RedirectResponse(url=f"/{project_id}/{"1"}", status_code=303)


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
