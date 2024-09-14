from fasthtml.common import *
import json

from .file_explorer import FileExplorer
from app.agents.state_schema import RetrievalMethod


def Step(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step: int,
    total_step_num: int,
    directory_tree_str: str,
    retrieval_method: str,
    is_last_step=False,
):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    common_style = "margin-bottom:1rem; background-color: #fbfcfc; border: 1px solid #a0a0a0; border-radius: 5px; padding: 10px;"
    scrollable_style = common_style + " max-height: 300px; overflow-y: auto;"
    textarea_style = (
        common_style
        + " min-height: 100px; max-height: 300px; overflow-y: auto; resize: vertical;"
    )

    def make_page_list(total_step_num, current_step):
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

    current_step = next_step - 1
    return Div(id="step", hx_ext="response-targets")(
        H4(f"Step {next_step-1}. {feedback_question}"),
        Form(
            id="step_form",
            hx_post=f"step?step_num={next_step - 1}&project_id={project_id}",
            hx_swap="outerHTML",
            hx_target="#step",
            hx_target_429="#quota_msg",
        )(
            H5("Answer"),
            Textarea(
                id="answer", name="answer", cls="dynamic-textarea", style=textarea_style
            )(answer),
            H5("Retrieved Code Snippets"),
            Div(
                cls="container",
                style=scrollable_style,
            )(
                *(
                    [P("No code snippets are retrieved")]
                    if not retrieved_chunks
                    else [
                        Code(
                            chunk,
                            style="margin-bottom:1rem; display: block; width: 100%; white-space: pre-wrap; word-break: break-all;",
                        )
                        for chunk in retrieved_chunks
                    ]
                )
            ),
            H5("Retrieval Method"),
            Select(
                id="retrieval_method",
                name="retrieval_method",
                cls="form-select",
            )(
                *[
                    Option(
                        method.value,
                        value=method.name,
                        selected=(
                            method == RetrievalMethod[retrieval_method]
                        ),
                    )
                    for method in RetrievalMethod
                ]
            ),
            H5("File Explorer"),
            FileExplorer(directory_tree_str, scrollable_style),
            Input(
                type="hidden",
                id="directory_tree_str",
                name="directory_tree_str",
                value=directory_tree_str,
            ),
            H5("Feedback"),
            Textarea(
                id="user_feedback",
                name="user_feedback",
                placeholder="Enter your feedback here",
                cls="dynamic-textarea",
                style=textarea_style,
            ),
            Button("Apply Feedback", id="apply_feedback_button", type="submit", cls="outline"),
        ),
        Div(id="quota_msg"),
        (
            Button(
                "Next Step",
                type="submit",
                cls="outline",
                id="next_step_button",
                hx_post=f"step?step_num={next_step}&project_id={project_id}",
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
                hx_vals="js:{}",
            )
            if not is_last_step
            else Button(
                "Finish",
                type="submit",
                cls="outline",
                hx_post=f"step/final?project_id={project_id}",
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
            )
        ),
        Div(
            Ol(cls="row center-xs middle-xs", style="padding-inline-start:0;")(
                *make_page_list(total_step_num, current_step)
            )
        ),
        Script(
            """
            (function() {
                const textareas = document.querySelectorAll('.dynamic-textarea');
                textareas.forEach(textarea => {
                    textarea.style.height = 'auto';
                    textarea.style.height = `${Math.min(textarea.scrollHeight, 600)}px`;
                    textarea.addEventListener('input', function() {
                        this.style.height = 'auto';
                        this.style.height = `${Math.min(this.scrollHeight, 600)}px`;
                    });
                });
            })();

            function updateTree(tree, fileName, value) {                
                function recursiveUpdate(obj) {
                    for (let key in obj) {
                        if (key === fileName) {
                            obj[key] = value;
                            return true;
                        } else if (typeof obj[key] === 'object') {
                            if (recursiveUpdate(obj[key])) {
                                return true;
                            }
                        }
                    }
                    return false;
                }
                recursiveUpdate(tree);
            }
            document.addEventListener('change', function(e) {
                if (e.target.matches('.file-explorer input[type="checkbox"]')) {
                    let tree = JSON.parse(document.getElementById('directory_tree_str').value);
                    updateTree(tree, e.target.value, e.target.checked);
                    document.getElementById('directory_tree_str').value = JSON.stringify(tree);
                }
            });
            """
        ),
    )
