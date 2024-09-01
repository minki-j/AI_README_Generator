from fasthtml.common import *
import json
from app.components.pages import StepPage

from app.assets.step_list import STEP_LIST
from app.db import db


def step_view(step_num: int, project_id: str):
    print("==>> step_view:", step_num, project_id)

    step_data = next(
        db.t.steps.rows_where("step = ? AND readme_id= ?", [step_num, project_id]), None
    )

    if step_data:
        retrieved_chunks = []
        for chunk in db.t.retrieved_chunks.rows_where("step_id = ?", [step_data["id"]]):
            retrieved_chunks.append(chunk["content"])
        return StepPage(
            step_num,
            len(STEP_LIST),
            {
                "feedback_question": step_data["feedback_question"],
                "answer": step_data["answer"],
                "retrieved_chunks": retrieved_chunks,
                "project_id": project_id,
                "next_step": str(int(step_num) + 1),
            },
            step_data["directory_tree_str"],
        )
    else:
        return A(href="/")(H1("AI README Generator")), Main(id="step")(
            Div(
                f"Error happended while retrieving information from the DB.",
                cls="error-message",
            ),
        )


def result_view(project_id: str):
    readme_data = db.t.readmes.get(project_id)
    print(f"==>> readme_data: {readme_data}")
    return A(href="/")(H1("AI README Generator")), Main(id="step")(
        Div(cls="container")(
            H2("Congratulations! You have completed the README generation process."),
            H3("Here is the generated README:"),
            P(readme_data.content),
        ),
    )
