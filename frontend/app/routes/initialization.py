import uuid
import os
import re
import requests

from fasthtml.common import *

from components.confirmatoin_box import return_confirmation_box

app, rt = fast_app()

route = "/init"

@rt("/")
def get():
    return Titled("/init route is working")

@rt("/start")
def post(clone_url: str):
    # Check if the URL is a valid GitHub clone URL
    github_url_pattern = r"^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+\.git$"
    if not re.match(github_url_pattern, clone_url):
        return Div(
            f"Error: Invalid GitHub clone URL:{clone_url} /  Please provide a valid URL.",
            cls="error-message",
        )

    id = str(uuid.uuid4())

    url = os.getenv("BACKEND_BASE_URL") + "/start"
    print("Request url: ", url)

    r = requests.post(url, json={"clone_url": clone_url, "id": id})

    if r.status_code != 200:
        return Div(
            f"Error: Something went wrong. Please try again later.",
            cls="error-message",
        )

    try:
        r_data = r.json()
    except requests.exceptions.JSONDecodeError:
        r_data = {"error": "Failed to decode JSON response"}

    print(f"==>> r_data: {r_data}")

    if r.status_code != 200:
        confirmation_box = P("Error: Something went wrong. Please try again later.")
    else:
        print("answer: ", r_data["answer"])
        confirmation_box = return_confirmation_box(
            r_data["feedback_question"], r_data["answer"]
        )

    return (
        Input(
            placeholder="Github Clone URL",
            name="clone_url",
            hx_swap_oob="true",
            id="clone_url_input",
        ),
        confirmation_box,
    )
