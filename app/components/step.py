from fasthtml.common import *
import json

def Step(
    feedback_question,
    answer,
    retrieved_chunks,
    project_id,
    next_step,
    directory_tree,
    is_last_step=False,
):
    """A step is a intermeidate process to generate a REAME file. For example, there could be 3 steps where the first step is to generate the entry point of the repository, second step is to generate get_started section and third step is to generate the installation section."""

    def FileExplorer(directory_tree):
        """Render a simple file explorer with checkable items for files only."""


        def render_tree(directory_tree):
            if not directory_tree:
                return []
            items = []
            for name, content in directory_tree.items():
                if isinstance(content, dict):
                    items.append(
                        Li(style="list-style-type: none; margin-left: 0;")(
                            Span(name),
                            Ul(style="padding-left: 0.5rem; margin-bottom: 0;")(
                                *render_tree(content)
                            ),
                        )
                    )
                else:
                    items.append(
                        Li(style="list-style-type: none; margin-left: 0;margin-bottom: 0;")(
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

        return Div(style="margin-bottom: 1rem;")(
            H4("File Explorer"),
            Ul(style="padding-left: 0; margin-bottom: 0;")(
                *render_tree(json.loads(directory_tree))
            ),
            cls="file-explorer",
            style="background-color: #fbfcfc; border: 1px solid #a0a0a0; border-radius: 5px; padding: 10px; max-height: 300px; overflow-y: auto;",
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
            Input(type="hidden", id="directory_tree", name="directory_tree", value=json.dumps(directory_tree)),
            Textarea(
                id="user_feedback",
                name="user_feedback",
                placeholder="Enter your feedback here",
            ),
            Button("Apply Feedback", type="submit", cls="outline"),
        ),
        Script("""
            document.addEventListener('change', function(e) {
                if (e.target.matches('.file-explorer input[type="checkbox"]')) {
                    let tree = JSON.parse(document.getElementById('directory_tree').value);
                    updateTree(tree, e.target.value, e.target.checked);
                    document.getElementById('directory_tree').value = JSON.stringify(tree);
                }
            });

            function updateTree(tree, fileName, value) {
                if (fileName in tree) {
                    tree[fileName] = value;
                } else {
                    for (let key in tree) {
                        if (typeof tree[key] === 'object') {
                            if (fileName in tree[key]) {
                                tree[key][fileName] = value;
                                break;
                            }
                        }
                    }
                }
            }
        """),
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
    directory_tree,
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
            directory_tree,
            is_last_step,
        ),
        Div(
            Ol(cls="row center-xs middle-xs", style="padding-inline-start:0;")(
                *make_page_list(total_step_num, current_step)
            )
        ),
    )
