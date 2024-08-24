from fasthtml.common import *

import app.views.gen as gen_views
from app.css import loader_css, gridlink
from app.db import db

def user_auth_before(req, sess):
    # The `auth` key in the request scope is automatically provided
    # to any handler which requests it, and can not be injected
    # by the user using query params, cookies, etc, so it should
    # be secure to use.
    auth = req.scope["auth"] = sess.get("auth", None)
    # If the session key is not there, it redirects to the login page.
    if not auth:
        return RedirectResponse("/login", status_code=303)

beforeware = Beforeware(
    user_auth_before,
    skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login", "/"],
)

app, _ = fast_app(
    live=True,
    hdrs=(
        picolink,
        gridlink,
        loader_css,
        HighlightJS(langs=["python"]),
    ),
    exception_handlers={
        404: lambda req, exc: Main(
            Titled("Page not found"),
            P("The page you are looking for does not exist."),
            cls="container",
        ),
    },
    # before=beforeware,
)

setup_toasts(app)

app.get("/")(gen_views.home_view)
app.post("/init/{project_id}")(gen_views.step_initializer)
app.get("/step/{step}/{project_id}")(gen_views.step_view)
app.post("/step/{step}/{project_id}")(gen_views.step_handler)
