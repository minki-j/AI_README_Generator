import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.agents.state_schema import State
from app.utils.get_user_picked_file_paths import get_user_picked_file_paths


def add_user_chosen_files(state: State):
    print("\n>>>> NODE: add_user_chosen_files")
    return {
        "valid_paths": get_user_picked_file_paths(state["directory_tree_dict"]),
    }


def read_file(path, root_path):
    full_path = os.path.join(root_path, path)
    if full_path.endswith(".ipynb"):
        print(f"Skipping jupyter notebook: {full_path}")
        return None
    if not os.path.exists(full_path):
        raise ValueError(f"Does not exist: {full_path}")
    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            return full_path.replace(root_path, ""), f.read()
    except UnicodeDecodeError:
        print(f"Unable to read file due to encoding issues: {full_path}. Skipping this file.")
        return None


def read_files(state: State):
    print("\n>>>> NODE: read_files")

    root_path = str(Path(state["cache_dir"]) / state["title"] / "cloned_repositories")
    valid_paths = state["valid_paths"]
    retrieved_chunks = {}
    with ThreadPoolExecutor() as executor:
        future_to_path = {
            executor.submit(read_file, path, root_path): (path, root_path) for path in valid_paths
        }
        for future in as_completed(future_to_path):
            result = future.result()
            if result:
                key, content = result
                retrieved_chunks[key] = content

    return {
        "retrieved_chunks": retrieved_chunks,
        "opened_files": valid_paths,
    }
