from fasthtml.common import *


def return_landing_bos(session):
    print("session", session)
    return Div(
        Div(
            Titled("Welcome"),
            P(session.get("session_id", "No session ID found")),
        ),
        id="landing_box",
    )
