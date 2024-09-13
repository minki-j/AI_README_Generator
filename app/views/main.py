import uuid
from fasthtml.common import *
from app.utils.initialize_db import db


def home_view(session):
    print("\n==>>VIEW: home_view")
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
        Main(id="step", cls="container")(
            A(href="/", style="text-decoration: none; color: inherit;")(H1("AI README Generator")),
            Form(
                hx_post="init/?project_id=" + str(uuid.uuid4()),
                hx_swap="innerHTML",
                hx_target="body",
                hx_indicator="#loader",
                hx_replace_url="true",
            )(
                P(
                    "Having trouble writing a killer README? No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. 🚀 Let’s get started!",
                ),
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
                    P(
                        "Loading...",
                        cls="",
                    ),
                ),
            ),
        ),
    )
