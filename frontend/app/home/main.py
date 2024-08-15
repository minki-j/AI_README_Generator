from fasthtml.common import *

app = FastHTML()


@app.get("/")
def home():
    input = Input(id="clone_url", name="clone_url", placeholder="Github Clone URL")

    add = Form(
        Group(input, Button("Start")),
        hx_post="/clone_repo",
        target_id="status",
        hx_swap="outerHTML",
    )

    return Title("AI README Generator"), Main(
        H1("Welcome to AI README Generator"),
        add,
        Div(id="status"),
        cls="container",
    )


@app.post("/clone_repo")
def add_message(clone_url: str):
    return P(f"Cloning {clone_url}..."), Input(
        id="clone_url",
        name="clone_url",
        placeholder="Github Clone URL",
        hx_swap_oob="true",
    )
