from fasthtml.common import *

from app.components.step import Step


def StepPage(step_num, total_step_num, step_data, directory_tree_str):
    return (
        Title("AI README Generator"),
        Main(cls="container", style="")(
            A(href="/", style="text-decoration: none; color: inherit;")(H1("AI README Generator")),
            Step(
                step_data["feedback_question"],
                step_data["answer"],
                step_data["retrieved_chunks"],
                step_data["project_id"],
                step_data["next_step"],
                total_step_num,
                directory_tree_str,
                is_last_step=True if int(step_num) > total_step_num else False,
            ),
        ),
    )
