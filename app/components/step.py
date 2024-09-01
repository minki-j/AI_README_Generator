from fasthtml.common import *
import json


def Step(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step,
    directory_tree: str,
    is_last_step=False,
):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    def FileExplorer(directory_tree_str):
        """Render a simple file explorer with checkable items for files only."""
        try:
            directory_tree_obj = json.loads(directory_tree_str)
        except json.JSONDecodeError:
            print(
                f"Error: Unable to parse directory_tree_str as JSON. Value: {directory_tree_str}"
            )
            directory_tree_obj = {}  # Fallback to an empty dictionary

        if not isinstance(directory_tree_obj, dict):
            print(
                f"Error: directory_tree_obj is not a dictionary. Value: {directory_tree_obj}"
            )
            raise ValueError("directory_tree is not properly formatted in JSON")

        def render_tree(directory_tree_obj):
            if not directory_tree_obj:
                return []
            items = []

            for name, content in directory_tree_obj.items():
                if isinstance(content, dict):
                    items.append(
                        Li(style="list-style-type: none; margin-left: 0;")(
                            Span(name),
                            Ul(style="padding-left: 1rem; margin-bottom: 0;")(
                                *render_tree(content)
                            ),
                        )
                    )
                else:
                    items.append(
                        Li(
                            style="list-style-type: none; margin-left: 0;margin-bottom: 0;"
                        )(
                            Label(
                                Input(
                                    type="checkbox",
                                    name="file",
                                    value=name,
                                    checked=content,
                                ),
                                Span(name),
                            )
                        )
                    )
            return items

        return Div(
            cls="file-explorer",
            style="margin-bottom: 1rem; background-color: #fbfcfc; border: 1px solid #a0a0a0; border-radius: 5px; padding: 10px; max-height: 300px; overflow-y: auto;",
        )(
            H4("File Explorer"),
            Ul(style="padding-left: 0; margin-bottom: 0;")(
                *render_tree(directory_tree_obj)
            ),
        )

    return (
        H4(f"Step {str(int(next_step)-1)}. {feedback_question}"),
        Form(
            hx_post=f"step?step_num={str(int(next_step) - 1)}&project_id={project_id}",
            hx_swap="outerHTML",
            hx_target="#step",
            cls="",
        )(
            Textarea(id="answer", name="answer", rows="15"),
            Div(cls="container")(
                *[Code(chunk) for chunk in retrieved_chunks],
            ),
            FileExplorer(directory_tree),
            Input(
                type="hidden",
                id="directory_tree_str",
                name="directory_tree_str",
                value=directory_tree,
            ),
            Textarea(
                id="user_feedback",
                name="user_feedback",
                placeholder="Enter your feedback here",
            ),
            Button("Apply Feedback", type="submit", cls="outline"),
        ),
        Script(
            """
            document.addEventListener('change', function(e) {
                if (e.target.matches('.file-explorer input[type="checkbox"]')) {
                    let tree = JSON.parse(document.getElementById('directory_tree_str').value);
                    updateTree(tree, e.target.value, e.target.checked);
                    document.getElementById('directory_tree_str').value = JSON.stringify(tree);
                }
            });

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
        """
        ),
        (
            Button(
                "Next Step",
                type="submit",
                cls="outline",
                hx_post=f"step?step_num={next_step}&project_id={project_id}",
                hx_swap="outerHTML",
                hx_target="#step",
                hx_replace_url="true",
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
    )


def StepDiv(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step,
    total_step_num,
    directory_tree_str: str,
    is_last_step=False,
):
    def make_page_list(total_step_num, current_step):
        page_list = []
        for i in range(1, total_step_num + 1):
            common_style = "margin-bottom:0;"
            if i <= current_step:
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

    current_step = int(next_step) - 1
    return Div(id="step", cls="")(
        Step(
            feedback_question,
            answer,
            retrieved_chunks,
            project_id,
            next_step,
            directory_tree_str,
            is_last_step,
        ),
        Div(
            Ol(cls="row center-xs middle-xs", style="padding-inline-start:0;")(
                *make_page_list(total_step_num, current_step)
            )
        ),
    )
