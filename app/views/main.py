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
                hx_post="init/?project_id=" + str(uuid.uuid4()),
                hx_swap="outerHTML",
                hx_target="#step",
                hx_indicator="#loader",
                hx_replace_url="true",
            )(
                Div(cls="container row", style="gap:1rem;")(
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


def step_view(step: str, project_id: str):
    print("==>> step_view:", step, project_id)
    
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
                is_last_step= True if int(step) == len(STEP_LIST)-1 else False,
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


def result_view(project_id: str):
    readme_data = db.t.readmes.get(project_id)
    print(f"==>> readme_data: {readme_data}")
    return Main(id="step")(
        Titled("AI README Generator"),
        Div(cls="container")(
            H2("Congratulations! You have completed the README generation process."),
            H3("Here is the generated README:"),
            P(readme_data.content),
        ),
    )
