import os
from state_schema import State
import json


def read_files_suggested_by_LLM(state: State):
    print("==>> read_files_suggested_by_LLM node started")

    root_path = state["repo_root_path"]
    valid_paths = state["valid_paths"]

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
        formatted_snippets = "No valid files found"
    else: 
        formatted_snippets = [
            f"{path}:\n\n{content}" for path, content in opened_files.items()
        ]
    return {
        "retrieved_code_snippets": "",
        # "retrieved_code_snippets": "\n\n------------\n\n".join(formatted_snippets),
        "opened_files": valid_paths,
    }
