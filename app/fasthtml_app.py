from fasthtml.common import *

from app.css import loader_css, input_pattern_error

import app.views.main as main_views
import app.views.step as step_views
import app.views.history as history_views
import app.controllers.init as init_handlers
import app.controllers.step as step_handlers


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

app.get("/")(main_views.home_view)
app.get("/step")(step_views.step_view)
app.get("/step/final")(step_views.result_view)
app.get("/history")(history_views.history_view)

app.post("/init")(init_handlers.step_initializer)
app.post("/step")(step_handlers.step_handler)
app.post("/step/final")(step_handlers.generate_readme)


# def user_auth_before(req, sess):
#     # The `auth` key in the request scope is automatically provided
#     # to any handler which requests it, and can not be injected
#     # by the user using query params, cookies, etc, so it should
#     # be secure to use.
#     auth = req.scope["auth"] = sess.get("auth", None)
#     # If the session key is not there, it redirects to the login page.
#     if not auth:
#         return RedirectResponse("/login", status_code=303)


# beforeware = Beforeware(
#     user_auth_before,
#     skip=[r"/favicon\.ico", r"/static/.*", r".*\.css", r".*\.js", "/login", "/"],
# )
