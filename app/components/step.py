from fasthtml.common import *


def Step(feedback_question, answer, retrieved_chunks, project_id, next_step, is_last_step=False):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    return Div(cls="container bordered-container")(
        H4(f"Step {str(int(next_step)-1)}. {feedback_question}"),
        Form(
            hx_post=f"step?step_num={str(int(next_step) - 1)}&project_id={project_id}",
            hx_swap="outerHTML",
            hx_target="#step",
        )(
            Textarea(answer, name="answer", rows="15"),
            Div(cls="container")(
                *[Code(chunk) for chunk in retrieved_chunks],
            ),
            Textarea(name="user_feedback", placeholder="Enter your feedback here"),
            Button("Apply Feedback", type="submit", cls="outline"),
        ),
        (
            Button(
                "Next Step",
                type="submit",
                cls="outline",
                hx_post=f"step?step_num={next_step}&project_id={project_id}",
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
            )
            if not is_last_step
            else Button(
                "Finish",
                type="submit",
                cls="outline",
                hx_post=f"step/final?project_id={project_id}",
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
            )
        ),
    )
