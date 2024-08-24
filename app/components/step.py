from fasthtml.common import *


def Step(feedback_question, answer, retrieved_chunks, project_id, next_step):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    return Div(id="step")(
        Div(cls="container bordered-container")(
            H2("Let's write a README together!"),
            P(feedback_question),
            Form(
                post=uri("step_handler", project_id=project_id, step=str(int(next_step)-1)),
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
            Button(
                "Next Step",
                type="submit",
                cls="outline",
                post=uri("step_handler", project_id=project_id, step=next_step),
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
            ),
        )
    )
