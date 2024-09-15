import os
from pathlib import Path

from app.agents.state_schema import State


def add_user_chosen_files(state: State):
    print("\n>>>> NODE: add_user_chosen_files")
    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])
    user_chosen_files = []
    directory_tree_dict = state["directory_tree_dict"]

    # recursively find the files that are the keys of this dict where the value is True, and add them to the valid_paths list
    def recursive_find(directory_tree_dict, current_path):
        for path, value in directory_tree_dict.items():
            if isinstance(value, dict):
                recursive_find(value, current_path + "/" + path)
            elif value == True:
                user_chosen_files.append(current_path + "/" + path)
            else:
                continue

    recursive_find(directory_tree_dict, root_path)

    return {
        "valid_paths": user_chosen_files,
    }


def read_files(state: State):
    print("\n>>>> NODE: read_files")

    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])
    valid_paths = state["valid_paths"]
    print("reading the following files: ", valid_paths)

    opened_files = {}
    for full_path in valid_paths:
        #! Currently skipping jupyter notebooks
        if full_path.endswith(".ipynb"):
            print(f"Skipping jupyter notebook: {full_path}")
            continue
        if not os.path.exists(full_path):
            raise ValueError(f"Does not exist: {full_path}")

        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                opened_files[full_path.replace(root_path, "")] = f.read()
        except UnicodeDecodeError:
            print(f"Skipping file due to encoding issues: {full_path}")

        break  #! We are only reading the first file for now due to the limitation context lenght.

    # TODO: Add an intelligent way to shorten the code snippets

    if not opened_files:
        opened_files = {}
    
    return {
        "retrieved_chunks": opened_files,
        "opened_files": valid_paths,
    }
