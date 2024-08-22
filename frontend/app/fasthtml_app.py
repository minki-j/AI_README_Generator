from fasthtml.common import *

import views.gen as gen_views
from css import loader_css, gridlink

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

app, rt = fast_app(
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
app.post("/{project_id}/init")(gen_views.step_initializer)
app.get("/{project_id}/{step}")(gen_views.step_view)
app.post("/{project_id}/{step}")(gen_views.step_handler)
