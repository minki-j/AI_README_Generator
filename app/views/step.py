from fasthtml.common import *
from app.components.pages import StepPage

from app.step_list import STEP_LIST
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
                "next_step": step_num + 1,
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
    print("==>> result_view")
    readme_data = db.t.readmes.get(project_id)
    print("==>> readme_data.content:", readme_data.content)
    return (
        Title("AI README Generator"),
        Main(cls="container", style="")(
            A(href="/", style="text-decoration: none; color: inherit;")(
                H1("AI README Generator")
            ),
            P("Congratulations! You have completed the README generation process."),
            P(B("Here is the generated README:")),
            P(readme_data.content if readme_data.content else "No content generated."),
        ),
    )
