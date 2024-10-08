from fasthtml.common import *
import json


def FileExplorer(directory_tree_str, common_style):
    """Render a simple file explorer with checkable items for files only."""
    try:
        directory_tree_obj = json.loads(directory_tree_str)
    except json.JSONDecodeError:
        print(
            f"Error: Unable to parse directory_tree_str as JSON. Value: {directory_tree_str}"
        )
        directory_tree_obj = {} 

    if not isinstance(directory_tree_obj, dict):
        print(
            f"Error: directory_tree_obj is not a dictionary. Value: {directory_tree_obj}"
        )
        raise ValueError("directory_tree is not properly formatted in JSON")

    def render_tree(directory_tree_obj, current_path=''):
        if not directory_tree_obj:
            return []
        items = []

        for name, content in directory_tree_obj.items():
            full_path = f"{current_path}/{name}".lstrip('/')
            if isinstance(content, dict):
                items.append(
                    Li(
                        style="list-style-type: none; margin-left: 0;",
                        cls="file-explorer-directory",
                    )(
                        Span(
                            onclick=f"toggleDirectory(this, '{name}')",
                            style="cursor: pointer; margin-bottom: 0.125rem;",
                        )(
                            f"▼ {name}",
                        ),
                        Ul(
                            id=f"dir-{name}",
                            style="padding-left: 1rem; margin-bottom: 0;",
                        )(*render_tree(content, full_path)),
                    )
                )
            else:
                items.append(
                    Li(
                        style="list-style-type: none; margin-left: 0; margin-bottom: 0;"
                    )(
                        Label(
                            Input(
                                type="checkbox",
                                cls="file-explorer-checkbox",
                                name="file",
                                value=full_path,  # Use full_path instead of name
                                checked=content,
                                style="accent-color: black;",
                                # onchange="this.style.backgroundColor = this.checked ? 'lightblue' : '';",
                            ),
                            Span(name),
                        )
                    )
                )
        return items

    return Div(
        cls="file-explorer",
        style=common_style,
    )(
        Ul(style="padding-left: 0; margin-bottom: 0;")(
            *render_tree(directory_tree_obj)
        ),
    )
