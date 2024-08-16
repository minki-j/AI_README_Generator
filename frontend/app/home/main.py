from fasthtml.common import *

import uuid
import dotenv
import requests

dotenv.load_dotenv()


# Flexbox CSS (http://flexboxgrid.com/)
gridlink = Link(
    rel="stylesheet",
    href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
    type="text/css",
)

app, rt = fast_app(hdrs=(picolink, gridlink))


@rt("/")
def get():
    return Title("AI README Generator"), Main(
        Titled("AI README Generator"),
        P(
            "Having trouble writing a killer README? 😩 No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. ✍️🚀 Let’s get started!",
            cls="",
        ),
        Form(
            Group(
                Input(
                    placeholder="Github Clone URL",
                    name="clone_url",
                    id="clone_url_input",
                ),
                Button("Start", hx_indicator="loader"),
            ),
            hx_post="/start",
            hx_swap="beforeend",
            target_id="middle_step",
        ),
        Div(
            Div(
                Img(id="loader", cls="box loader", src="/img/loading.jpeg"),
                P(
                    "Loading...", cls="",
                ),
                cls="col-xs-6",
            ),
            cls="row center-xs",
        ),
        Div(id="middle_step"),
        cls="container",
    )


@rt("/start")
def post(clone_url: str):
    # add os.getenv("BACKEND_BASE_URL_DEV") with the endpoint "start"
    url = os.getenv("BACKEND_BASE_URL_DEV") + "/start"
    print("Request url: ", url)

    start_project(clone_url)

    return (
        Input(
            placeholder="Github Clone URL",
            name="clone_url",
            hx_swap_oob="true",
            id="clone_url_input",
        ),
        Div("Loading..."),
    )


@threaded
def start_project(clone_url: str):
    url = os.getenv("BACKEND_BASE_URL_DEV") + "/start"
    print("Request url: ", url)

    r = requests.post(url, json={"clone_url": clone_url})

    return r.json()


@rt("/loading")
def get():
    return (Div("Loading..."),)
