from fasthtml.common import *
from app.components.pages import StepPage

from app.step_list import STEP_LIST
from app.utils.initialize_db import db


def step_view(session, step_num: int, project_id: str):
    print("\n>>>> VIEW: step_view")

    step_data = next(
        db.t.steps.rows_where("step = ? AND readme_id= ?", [step_num, project_id]), None
    )
    if not step_data:
        raise Exception(
            f"Step data not found for step_num: {step_num} and project_id: {project_id}"
        )
    
    readme_data = db.t.readmes.get(project_id)
    if not readme_data:
        raise Exception(
            f"README data not found for project_id: {project_id}"
        )
    
    print(f"Repo title: {readme_data.title}")
    print(f"Project ID: {project_id}")

    retrieved_chunks = {}
    for chunk in db.t.retrieved_chunks.rows_where("step_id = ?", [step_data["id"]]):
        retrieved_chunks[chunk["path"]] = chunk["content"]
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
        retrieval_method=session["retrieval_method"],
        quota=session.get("quota", (0, 0)),
    )


def result_view(project_id: str):
    print("\n>>>> VIEW: result_view")

    readme_data = db.t.readmes.get(project_id)
    if not readme_data:
        raise Exception(
            f"README data not found for project_id: {project_id}"
        )

    print(f"Repo title: {readme_data.title}")
    print(f"Project ID: {project_id}")

    return (
        Title("AI README Generator"),
        Main(cls="container", style="")(
            Div(
                cls="header-container",
                style="display: flex; justify-content: space-between; align-items: center;",
            )(
                A(href="/", style="text-decoration: none; color: inherit;")(
                    H1("AI README Generator")
                ),
                Button(
                    id="themeToggle",
                    style="background: none; border: none; cursor: pointer;",
                    onclick="toggleTheme()",
                )("🌓"),
            ),
            P(
                "Congratulations! You have completed the README generation process. ",
                B("Here is the generated README:"),
            ),
            Div(
                cls="marked",  #! Not working on Railway (works fine locally)
                style="border: 1px solid #a0a0a0; border-radius: 5px; padding: 10px;",
            )(readme_data.content if readme_data.content else "No content generated."),
            Script(
                """
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
            }

            document.addEventListener('DOMContentLoaded', function() {
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme) {
                    document.documentElement.setAttribute('data-theme', savedTheme);
                }
            });
        """
            ),
        ),
    )
