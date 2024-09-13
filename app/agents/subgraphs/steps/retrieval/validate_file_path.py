import os
from pathlib import Path

from app.agents.state_schema import State

from app.agents.common import chat_model
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate


def validate_file_paths_from_LLM(state: State):
    print("\n==>>NODE: validate_file_paths_from_LLM")
    if not state["cache_dir"] or not state["title"]:
        print(f"\n==>> cache_dir: {state['cache_dir']}")
        print(f"\n==>> title: {state['title']}")
        print(f"\n==>> state: {state}")
        raise ValueError("No cache_dir or title")
    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])

    if state.get("corrected_paths", None):
        # If this node is recursively called, use corrected paths from correct_file_paths node
        full_paths = state["corrected_paths"]
    else:
        file_paths = []  # TODO: update this with steps subgraph
        if len(file_paths) == 0:
            print("No file paths to validate")
            return {
                # "invalid_paths": [],
                "valid_paths": [],
            }
        full_paths = [os.path.join(root_path, path) for path in file_paths]

    invalid_paths = []
    valid_paths = []
    for full_path in full_paths:
        if not os.path.exists(full_path):
            invalid_paths.append(full_path)
        else:
            valid_paths.append(full_path)
    if invalid_paths:
        print(
            "Invalid paths detected:",
            [path.replace(root_path, "") for path in invalid_paths],
        )

    return {
        "invalid_paths": invalid_paths,
        "valid_paths": valid_paths,
    }


def correct_file_paths(state: State):
    print("\n==>>NODE: correct_file_paths")
    invalid_paths = state["invalid_paths"]
    root_path = "/Users/minkijung/Documents/2PetProjects/ernest"

    invalid_paths_without_root = [
        os.path.relpath(path, root_path) for path in invalid_paths
    ]

    directory_tree = state["directory_tree"]

    class PathCorrection(BaseModel):
        corrected_paths: list[str]

    prompt = ChatPromptTemplate.from_template(
        f"""There is some mistake in the following paths: {invalid_paths_without_root}

        Correct them refering to this Directory tree: {directory_tree}"""
    )

    chain = prompt | chat_model.with_structured_output(PathCorrection)

    result = chain.invoke(
        {
            "invalid_paths": ", ".join(invalid_paths),
            "directory_tree": state["directory_tree"],
        }
    )

    corrected_path_with_root = [
        os.path.join(root_path, path) for path in result.dict()["corrected_paths"]
    ]

    return {"corrected_paths": corrected_path_with_root}
