from collections import defaultdict


def build_tree(paths):
    tree = lambda: defaultdict(tree)
    root = tree()
    for path in paths:
        parts = path.split("/")
        current_level = root
        for part in parts:
            current_level = current_level[part]
    return root


def tree_to_string(tree, indent=""):
    tree_str = ""
    for key, subtree in sorted(tree.items()):
        tree_str += f"{indent}├── {key}\n"
        if subtree:
            tree_str += tree_to_string(subtree, indent + "│ ")
    return tree_str

def generate_tree(paths):
    tree = build_tree(paths)
    return tree_to_string(tree)