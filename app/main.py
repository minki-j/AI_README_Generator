import time
from fasthtml.common import *

import app.views.main as main_views
import app.views.step as step_views
import app.views.history as history_views
import app.controllers.init as init_controller
import app.controllers.step as step_controller


from app.global_vars import QUOTA_LIMIT


def user_auth_before(req, session):
    quota = session.get("quota", None)
    if quota is None:
        print("Initializing quota")
        session["quota"] = (QUOTA_LIMIT, int(time.time()))


beforeware = Beforeware(
    user_auth_before,
    skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login"],
)

app, _ = fast_app(
    live=True,
    hdrs=(
        picolink,
        Link(
            rel="stylesheet",
            href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
            type="text/css",
        ),
        Style(
            """
.main-page-loader{
    display:none;
}
.htmx-request.main-page-loader{
    display:inline;
    transform: translate(-50%, -50%);
    animation: pulse 2s ease-in-out infinite !important;
}
.btn-loader {
    position: relative;
    color: inherit;
    pointer-events: auto;
    opacity: 1;
}
.htmx-request.btn-loader {
    color: transparent;
    pointer-events: none;
}
.htmx-request.btn-loader::after {
    content: "Loading...";
    position: absolute;
    width: auto;
    height: auto;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #000000;
    font-size: 14px;
    animation: pulse 2s ease-in-out infinite !important;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.2; }
    100% { opacity: 1; }
}

    """
        ),
        MarkdownJS(),
        HighlightJS(langs=["python", "javascript", "html", "css"]),
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

app.post("/init")(init_controller.step_initializer)
app.post("/step")(step_controller.step_handler)
app.post("/step/final")(step_controller.generate_readme)
app.post("/update_retrieval_method")(step_controller.update_retrieval_method)
