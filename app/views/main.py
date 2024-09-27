import uuid
from fasthtml.common import *

from app.views.components.subtitle_selector import subtitle_selector

def home_view(session):
    print("\n>>>> VIEW: home_view")
    return (
        Title("AI README Generator"),
        Main(id="step", cls="container", hx_ext="response-targets")(
            Div(
                cls="header-container",
                style="display: flex; justify-content: space-between; align-items: center;",
            )(
                A(href="/", style="text-decoration: none; color: inherit;")(
                    H1("AI README Generator")
                ),
                Button(
                    id="themeToggle",
                    style="background: none; border: none; cursor: pointer;",
                    onclick="toggleTheme()",
                )("🌓"),
            ),
            Form(
                hx_post="init?project_id=" + str(uuid.uuid4()),
                hx_swap="outerHTML",
                hx_target="main",
                hx_target_429="#quota_msg",
                hx_target_500="#error_msg",
                hx_indicator="#loader",
                hx_replace_url="true",
            )(
                P(
                    "Having trouble writing a README? No worries, I’ve got your back! Share your project with me, and together we’ll create a README that stands out. 🚀 Let’s get started!",
                ),
                P(
                    "🐍 Python projects only for now! We're cooking up support for other languages. Stay tuned! 🔮",
                ),
                Group(
                    Input(
                        placeholder="Github Clone URL",
                        name="clone_url",
                        id="clone_url_input",
                        value="https://github.com/minki-j/AI_README_Generator.git",
                        pattern="^https://github\.com/[a-zA-Z0-9\-_]+/[a-zA-Z0-9\-_]+\.git$",
                        required=True,
                        style="",
                    ),
                    Button("Start", id="start_button"),
                ),
                P(
                    "🚨Must follow the URL pattern: https://github.com/username/repository.git",
                    id="clone_url_guide_msg",
                    style="display: none; padding-left: 1rem;",
                ),
                subtitle_selector(),
                Script(
                    """
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOMContentLoaded addEventlisteners")
    const input = document.getElementById('clone_url_input');
    const button = document.getElementById('start_button');
    const guideMsg = document.getElementById('clone_url_guide_msg');
    
    function validateInput() {
        console.log("validateInput")
        button.disabled = !input.checkValidity();
        console.log("button.disabled", button.disabled)
        input.classList.toggle('invalid', !input.checkValidity());
        console.log("input.classList.toggle('invalid', !input.checkValidity())", input.classList)
        guideMsg.style.display = input.checkValidity() ? 'none' : 'block';
        console.log("guideMsg.style.display", guideMsg.style.display)
    }
    
    input.addEventListener('input', validateInput);
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
        Div(id="error_msg"),
        Script(
            """
            function toggleTheme() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
            }

            document.addEventListener('DOMContentLoaded', function() {
                const savedTheme = localStorage.getItem('theme');
                if (savedTheme) {
                    document.documentElement.setAttribute('data-theme', savedTheme);
                }
            });
        """
        ),
        Style(
            """
            #clone_url_input.invalid {
                border-color: #ff4136;
                background-color: rgba(255, 65, 54, 0.1);
            }
            #clone_url_input.invalid:focus {
                box-shadow: 0 0 0 0.2rem rgba(255, 65, 54, 0.25);
            }

            [data-theme="dark"] #clone_url_input.invalid {
                border-color: #ff6b6b;
                background-color: rgba(255, 107, 107, 0.1);
            }
            [data-theme="dark"] #clone_url_input.invalid:focus {
                box-shadow: 0 0 0 0.2rem rgba(255, 107, 107, 0.25);
            }
        """
        ),
    )
