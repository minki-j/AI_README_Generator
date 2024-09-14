import time
from fasthtml.common import *

from app.css import loader_css, input_pattern_error

import app.views.main as main_views
import app.views.step as step_views
import app.views.history as history_views
import app.controllers.init as init_handlers
import app.controllers.step as step_handlers

from app.global_vars import QUOTA_LIMIT


def user_auth_before(req, session):
    quota = session.get("quota", None)
    if quota is None:
        print("Initializing quota")
        session["quota"] = (QUOTA_LIMIT, int(time.time()))

beforeware = Beforeware(
    user_auth_before,
    skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login", "/"],
)

app, _ = fast_app(
    live=True,
    debug=True,
    hdrs=(
        picolink,
        Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
            type="text/css",
        ),
        loader_css,
        input_pattern_error,
        HighlightJS(langs=["python"]),
        Script(
            src="https://unpkg.com/htmx-ext-response-targets@2.0.0/response-targets.js"
        ),
    ),
    exception_handlers={
        404: lambda req, exc: Main(
            Titled("Page not found"),
            P("The page you are looking for does not exist."),
            cls="container",
        ),
    },
    before=beforeware,
)

setup_toasts(app)

app.get("/")(main_views.home_view)
app.get("/step")(step_views.step_view)
app.get("/step/final")(step_views.result_view)
app.get("/history")(history_views.history_view)

app.post("/init")(init_handlers.step_initializer)
app.post("/step")(step_handlers.step_handler)
app.post("/step/final")(step_handlers.generate_readme)
