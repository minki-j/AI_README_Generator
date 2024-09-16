import time
import uuid
from fasthtml.common import *
from app.utils.initialize_db import db
from app.global_vars import QUOTA_LIMIT
from app.agents.state_schema import RetrievalMethod


def home_view(session):
    print("\n>>>> VIEW: home_view")
    if "session_id" not in session:
        print("initializing session")
        session["session_id"] = str(uuid.uuid4())
    if "quota" not in session:
        print("initializing quota")
        session["quota"] = (QUOTA_LIMIT, int(time.time()))
    if "retrieval_method" not in session:
        print("initializing retrieval_method")
        session["retrieval_method"] = RetrievalMethod.FAISS.name
    db.t.users.insert(
        id=session["session_id"],
        name="",
        email="",
        password="",
    )

    return (
        Title("AI README Generator"),
        Main(id="step", cls="container", hx_ext="response-targets")(
            A(href="/", style="text-decoration: none; color: inherit;")(
                H1("AI README Generator")
            ),
            Form(
                hx_post="init?project_id=" + str(uuid.uuid4()),
                hx_swap="outerHTML",
                hx_target="#step",
                hx_target_429="#quota_msg",
                hx_indicator="#loader",
                hx_replace_url="true",
            )(
                P(
                    "Having trouble writing a killer README? No worries, I’ve got your back! 💪 Share your project with me, and together we’ll create a README that stands out. 🚀 Let’s get started!",
                ),
                Group(
                    Input(
                        placeholder="Github Clone URL",
                        name="clone_url",
                        id="clone_url_input",
                        value="https://github.com/minki-j/AI_README_Generator.git",
                        pattern="^https://github\.com/[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+\.git$",
                        required=True,
                    ),
                    Button("Start", id="start_button"),
                ),
                P(
                    "URL pattern: https://github.com/username/repository.git",
                    id="clone_url_guide_msg",
                    style="display: none; padding-left: 1rem;",
                ),
                Script(
                    """
                    document.addEventListener('DOMContentLoaded', function() {
                        const input = document.getElementById('clone_url_input');
                        const button = document.getElementById('start_button');
                        function validateInput() {
                            button.disabled = !input.checkValidity();
                        }
                        
                        const guideMsg = document.getElementById('clone_url_guide_msg');
                        function showGuideMsg() {
                            guideMsg.style.display = input.checkValidity() ? 'none' : 'block';
                        }
                        
                        input.addEventListener('input', validateInput);
                        input.addEventListener('input', showGuideMsg);
                        validateInput();
                    });
                    """
                ),
            ),
            Div(
                id="loader",
                cls="main-page-loader row center-xs",
            )(
                Div(
                    cls="col-xs-12",
                )(
                    P(
                        "Please wait for a moment. We are indexing your project and generating steps to help you write a README."
                    ),
                ),
            ),
        ),
        Div(id="quota_msg"),
        Style(
            """
            input:valid {
                background-color: #e8f5e9;  /* Light pastel green */
            }
            input:invalid {
                background-color: #ffebee;  /* Light pastel red */
            }
            """
        ),
    )
