import os
from app.agents.state_schema import State
import json
from pathlib import Path


def validate_user_chosen_files(state: State):
    print("==>> validate_user_chosen_files node started")
    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])
    valid_paths = []
    directory_tree_dict = state["directory_tree_dict"]

    # recursively find the files that are the keys of this dict where the value is True
    def recursive_find(directory_tree_dict, current_path):
        for path, value in directory_tree_dict.items():
            if isinstance(value, dict):
                recursive_find(value, current_path + "/" + path)
            elif value == True:
                valid_paths.append(current_path + "/" + path)
            else:
                continue

    recursive_find(directory_tree_dict, root_path)

    return {
        "valid_paths": valid_paths,
    }


def read_files(state: State):
    print("==>> read_files node started")

    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])
    valid_paths = state["valid_paths"]
    print(f"==>> valid_paths: {valid_paths}")

    opened_files = {}
    for full_path in valid_paths:
        #! Currently skipping jupyter notebooks
        if full_path.endswith(".ipynb"):
            print(f"Skipping jupyter notebook: {full_path}")
            continue
        if not os.path.exists(full_path):
            raise ValueError(f"File does not exist at full_path: {full_path}")

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                opened_files[full_path.replace(root_path, "")] = f.read()
        except UnicodeDecodeError:
            print(f"Skipping file due to encoding issues: {full_path}")

        break  #! We are only reading the first file for now due to the limitation context lenght.

    # TODO: Add an intelligent way to shorten the code snippets

    if not opened_files:
        formatted_snippets = ["No valid files found"]
    else:
        formatted_snippets = [
            f"{path}:\n\n{content}" for path, content in opened_files.items()
        ]
    return {
        # "retrieved_chunks": "\n\n------------\n\n".join(formatted_snippets),
        "retrieved_chunks": formatted_snippets,
        "opened_files": valid_paths,
    }
