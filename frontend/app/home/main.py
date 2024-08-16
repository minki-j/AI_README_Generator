from fasthtml.common import *

import uuid
import dotenv
import requests
import re

dotenv.load_dotenv()


gridlink = (
    Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
        type="text/css",
    ),
)
tailwindlink = Script(src="https://cdn.tailwindcss.com")

loader_css = Style(
    """
    .my-indicator{
        display:none;
    }
    .htmx-request .my-indicator{
        display:inline;
    }
    .htmx-request.my-indicator{
        display:inline;
    }
    .bordered-container {
        border: 1px solid #000;
        border-radius: 4px;
        padding: 16px;
    }

                   """
)

app, rt = fast_app(hdrs=(picolink, gridlink, loader_css))


@rt("/")
def get():
    return Title("AI README Generator"), Main(
        Titled("AI README Generator"),
        P(
            "Having trouble writing a killer README? 😩 No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. ✍️🚀 Let’s get started!",
            cls="",
        ),
        Form(
            Group(
                Input(
                    placeholder="Github Clone URL",
                    name="clone_url",
                    id="clone_url_input",
                    value="https://github.com/minki-j/AI_README_Generator.git",
                ),
                Button("Start", cls="btn-primary"),
            ),
            hx_post="/start",
            hx_swap="beforeend",
            target_id="middle_step",
            hx_indicator="#loader",
        ),
        Div(
            Div(
                Img(src="/img/loading.jpeg"),
                P(
                    "Loading...",
                    cls="",
                ),
                cls="col-xs-6",
            ),
            id="loader",
            cls="my-indicator row center-xs",
        ),
        Div(id="middle_step"),
        cls="container",
    )


def return_confirmation_box(next_step, llm_output):
    return Div(
        Div(
            Titled("Let's write a README together!"),
            P(next_step),
            Form(
                Div(
                    Input(name="llm_output", value=llm_output),
                    Input(name="user_feedback", placeholder="Enter your feedback here"),
                    Group(
                        Button("Send", type="submit", cls="outline col-xs-6"),
                        Button("Retry", cls="outline col-xs-6", hx_get="/retry"),
                        cls="row between-xs",
                    ),
                    cls="row around-xs",
                ),
                hx_post="/middle_steps",
                hx_swap="outerHTML",
                target_id="middle_step",
            ),
            cls="container bordered-container",
        ),
        id="middle_step",
    )


@rt("/start")
def post(clone_url: str):
    # Check if the URL is a valid GitHub clone URL
    github_url_pattern = r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+\.git$"
    if not re.match(github_url_pattern, clone_url):
        return Div(
            f"Error: Invalid GitHub clone URL:{clone_url} /  Please provide a valid URL.",
            cls="error-message",
        )

    url = os.getenv("BACKEND_BASE_URL") + "/start"
    print("Request url: ", url)

    r = requests.post(url, json={"clone_url": clone_url})
    print(f"==>> r: {r}")
    next_step = "Step 2: Analyzing the repository"
    llm_output = "Analyzing the repository..."

    if r.status_code != 200:
        confirmation_box = P("Error: Something went wrong. Please try again later.")
    else:
        confirmation_box = return_confirmation_box(next_step, llm_output)

    return (
        Input(
            placeholder="Github Clone URL",
            name="clone_url",
            hx_swap_oob="true",
            id="clone_url_input",
        ),
        confirmation_box,
    )


@rt("/middle_steps")
def post(
    llm_output: str,
    user_feedback: str,
):
    print("user_feedback: ", user_feedback)
    url = os.getenv("BACKEND_BASE_URL") + "/middleSteps"
    print("Request url: ", url)

    r = requests.post(
        url, json={"user_feedback": user_feedback, "llm_output": llm_output}
    )
    print(f"==>> r: {r}")
    next_step = "Step 2: Analyzing the repository"
    llm_output = "Analyzing the repository..."

    return return_confirmation_box(next_step, llm_output)


@rt("/retry")
def get():
    url = os.getenv("BACKEND_BASE_URL") + "/retry"
    r = requests.get(url)

    return Div(
        Div(
            Titled("Let's write a README together!"),
            P("Step 1: Cloning the repository"),
            Form(
                Div(
                    Input(name="user_feedback", placeholder="Enter your feedback here"),
                    Group(
                        Button("Send", type="submit", cls="outline col-xs-3"),
                        Button("Retry", cls="outline col-xs-3", hx_get="/retry"),
                        Button(
                            "Go Back", type="submit", cls="outline secondary col-xs-3"
                        ),
                        cls="row around-xs",
                    ),
                    cls="row around-xs",
                ),
                hx_post="/middle_steps",
                hx_swap="outerHTML",
                target_id="middle_step",
            ),
            cls="container bordered-container",
        ),
        id="middle_step",
    )
