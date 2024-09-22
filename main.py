import time
import uuid
from fasthtml.common import *

import uvicorn
from uvicorn.config import Config

import app.views.main as main_views
import app.views.step as step_views
import app.views.history as history_views
import app.controllers.init as init_controller
import app.controllers.step as step_controller
import app.controllers.admin as admin

from app.agents.state_schema import RetrievalMethod
from app.utils.initialize_db import db


def user_auth_before(req, session):
    if "session_id" not in session:
        print("initializing session")
        session["session_id"] = str(uuid.uuid4())
        db.t.users.insert(
            id=session["session_id"],
            name="",
            email="",
            password="",
        )
    if "quota" not in session:
        print("initializing quota")
        session["quota"] = (int(os.getenv("QUOTA_LIMIT", 10)), int(time.time()))
    if "retrieval_method" not in session:
        print("initializing retrieval_method")
        session["retrieval_method"] = RetrievalMethod.FAISS.name

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
        MarkdownJS(),
        HighlightJS(langs=["python", "javascript", "html", "css"]),
        Script(
            src="https://unpkg.com/htmx-ext-response-targets@2.0.0/response-targets.js"
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
.error-modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}
.error-modal .error-content {
    padding: 20px;
    border-radius: 5px;
    width: 80%;
    height: 80%;
    overflow: auto;
    position: relative;
    background-color: var(--pico-background-color);
    border: var(--pico-primary-border);
}
.error-modal .error-content .close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    font-size: 24px;
    cursor: pointer;
    border: none;
}
    """
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
app.get("/download_db")(admin.download_db)

app.post("/init")(init_controller.step_initializer)
app.post("/step")(step_controller.step_handler)
app.post("/step/final")(step_controller.generate_readme)
app.post("/update_retrieval_method")(step_controller.update_retrieval_method)

running_on_server = os.environ.get("RAILWAY_ENVIRONMENT_NAME") == "production"
print(f">>>> running_on_server: {running_on_server}")
serve(reload=not running_on_server)
