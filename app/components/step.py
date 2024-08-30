from fasthtml.common import *


def Step(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step,
    is_last_step=False,
):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    return (
        H4(f"Step {str(int(next_step)-1)}. {feedback_question}"),
        Form(
            hx_post=f"step?step_num={str(int(next_step) - 1)}&project_id={project_id}",
            hx_swap="outerHTML",
            hx_target="#step",
            cls="",
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


def StepDiv(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step,
    total_step_num,
    is_last_step=False,
):
    def make_page_list(total_step_num):
        page_list = []
        for i in range(1, total_step_num + 1):
            page_list.append(
                Li(cls="col-xs-2", style="list-style-type:none; margin-bottom:0;")(
                    A(href=f"/step?step_num={i}&project_id={project_id}")(
                        P(i, style="margin-bottom:0;"),
                    ),
                ),
            )
        return page_list

    return Div(id="step", cls="")(
        Step(
            feedback_question,
            answer,
            retrieved_chunks,
            project_id,
            next_step,
            is_last_step,
        ),
        Div(
            Ol(cls="row center-xs middle-xs", style="padding-inline-start:0;")(
                *make_page_list(total_step_num)
            )
        ),
    )
