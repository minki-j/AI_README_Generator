from fasthtml.common import *

import uuid
import dotenv
import requests
import re

from components.landing_box import return_landing_bos
from css import loader_css, gridlink

from routes.routes import mounts_for_routes

dotenv.load_dotenv()

def user_auth_before(req, sess):
    # The `auth` key in the request scope is automatically provided
    # to any handler which requests it, and can not be injected
    # by the user using query params, cookies, etc, so it should
    # be secure to use.
    auth = req.scope["auth"] = sess.get("auth", None)
    # If the session key is not there, it redirects to the login page.
    if not auth:
        return RedirectResponse("/login", status_code=303)


beforeware = Beforeware(
    user_auth_before,
    skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login", "/"],
)

app, rt = fast_app(
    hdrs=(
        picolink,
        gridlink,
        loader_css,
        HighlightJS(langs=["python"]),
    ),
    exception_handlers={
        404: lambda req, exc: Main(
            Titled("Page not found"),
            P("The page you are looking for does not exist."),
            cls="container",
        ),
    },
    before=beforeware,
    routes=mounts_for_routes,
)

setup_toasts(app)


@rt("/")
def get(session):
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
        add_toast(session, f"Session ID created: {session['session_id']}", "info")

    return Title("AI README Generator"), Main(
        Titled("AI README Generator"),
        P(
            "Having trouble writing a killer README? No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. 🚀 Let’s get started!",
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
        return_landing_bos(session),
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


@rt("/middle_steps")
def post(
    answer: str,
    user_feedback: str,
):
    url = os.getenv("BACKEND_BASE_URL") + "/middleSteps"

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

    return return_confirmation_box(r_data["feedback_question"], r_data["answer"])


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
