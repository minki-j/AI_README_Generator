from fasthtml.common import *
from app.components.pages import StepPage

from app.global_vars import STEP_LIST
from app.utils.initialize_db import db
from app.agents.state_schema import RetrievalMethod

def step_view(session, step_num: int, project_id: str):
    print("\n>>>> VIEW: step_view")

    step_data = next(
        db.t.steps.rows_where("step = ? AND readme_id= ?", [step_num, project_id]), None
    )
    if not step_data:
        raise Exception(f"Step data not found for step_num: {step_num} and project_id: {project_id}")

    retrieved_chunks = []
    for chunk in db.t.retrieved_chunks.rows_where("step_id = ?", [step_data["id"]]):
        retrieved_chunks.append(chunk["content"])
    return StepPage(
        step_num=step_num,
        total_step_num=len(STEP_LIST),
        step_data={
            "feedback_question": step_data["feedback_question"],
            "answer": step_data["answer"],
            "retrieved_chunks": retrieved_chunks,
            "project_id": project_id,
            "next_step": step_num + 1,
        },
        directory_tree_str=step_data["directory_tree_str"],
        retrieval_method=(
            session["retrieval_method"]
            if STEP_LIST[step_num - 1]["retrieval_needed"]
            else RetrievalMethod.NONE.name
        ),
        quota=session.get("quota", (0, 0)),
    )


def result_view(project_id: str):
    print("\n>>>> VIEW: result_view")
    readme_data = db.t.readmes.get(project_id)
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
