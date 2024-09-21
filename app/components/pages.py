from fasthtml.common import *

from app.components.step import Step

def make_page_list(total_step_num, current_step, project_id):
    page_list = []
    for i in range(1, total_step_num + 1):
        common_style = "margin-bottom:0;"
        if i <= int(current_step):
            page_list.append(
                Li(cls="col-xs-2", style="list-style-type:none; margin-bottom:0;")(
                    A(
                        href=f"/step?step_num={i}&project_id={project_id}",
                        style="text-decoration: none;",
                    )(
                        P(i, style=f"{common_style} color: #007bff;"),
                    ),
                ),
            )
        else:
            page_list.append(
                Li(cls="col-xs-2", style="list-style-type:none; margin-bottom:0;")(
                    A(
                        href="#",
                        cls="disabled",
                        style="text-decoration: none; pointer-events: none;",
                    )(
                        P(i, style=f"{common_style} color: #c0c0c0;"),
                    ),
                ),
            )
    return page_list

def StepPage(step_num, total_step_num, step_data, directory_tree_str, retrieval_method, quota):
    print(f"StepPage: step_num: {step_num}, total_step_num: {total_step_num}")
    return (
        Title("AI README Generator"),
        Main(cls="container", hx_ext="response-targets")(
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
            Step(
                step_data["feedback_question"],
                step_data["answer"],
                step_data["retrieved_chunks"],
                step_data["project_id"],
                step_data["next_step"],
                directory_tree_str,
                retrieval_method,
                quota,
                is_last_step=True if int(step_num) >= total_step_num else False,
            ),
            Div(
                Ol(cls="row center-xs middle-xs", style="padding-inline-start:0;")(
                    *make_page_list(total_step_num, step_num, step_data["project_id"])
                )
            ),
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
        ),
        Div(id="quota_msg"),
        Div(id="error_msg"),
    )
