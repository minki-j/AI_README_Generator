from fasthtml.common import *

def return_confirmation_box(feedback_question, answer, retrieved_chunks):
    return Div(
        Div(
            Titled("Let's write a README together!"),
            P(feedback_question),
            Form(
                Div(
                    Textarea(answer, name="answer", rows="15"),
                    *[Code(chunk) for chunk in retrieved_chunks],
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
                hx_post="/middle_steps",
                hx_swap="outerHTML",
                target_id="middle_step",
            ),
            cls="container bordered-container",
        ),
        id="middle_step",
    )
