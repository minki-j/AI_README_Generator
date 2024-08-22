from fasthtml.common import *


def Step(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step
):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    return Div(
        Div(
            Titled("Let's write a README together!"),
            P(feedback_question),
            Form(
                Div(
                    Textarea(answer, name="answer", rows="15"),
                    Div(
                        *[Code(chunk) for chunk in retrieved_chunks],
                        cls="container",
                    ),
                    Textarea(
                        name="user_feedback", placeholder="Enter your feedback here"
                    ),
                    Group(
                        Button("Send", type="submit", cls="outline col-xs-6"),
                        Button("Retry", cls="outline col-xs-6", hx_get="/retry"),
                        cls="row between-xs",
                    ),
                    cls="row around-xs",
                ),
                post=uri("step_handler", project_id=project_id, step=next_step),
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
            ),
            cls="container bordered-container",
        ),
        id="middle_step",
    )
