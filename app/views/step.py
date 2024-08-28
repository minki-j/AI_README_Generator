from fasthtml.common import *

from app.components.step import Step

from app.data.step_list import STEP_LIST
from app.db import db


def step_view(step_num: str, project_id: str):
    print("==>> step_view:", step_num, project_id)
    step_data = next(
        db.t.steps.rows_where("step = ? AND readme_id= ?", [step_num, project_id]), None
    )

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
                next_step=str(int(step_num) + 1),
                is_last_step=True if int(step_num) == len(STEP_LIST) - 1 else False,
            ),
        )
    else:
        return Main(id="step")(
            Titled("AI README Generator"),
            Div(
                f"Error happended while retrieving information from the DB.",
                cls="error-message",
            ),
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
