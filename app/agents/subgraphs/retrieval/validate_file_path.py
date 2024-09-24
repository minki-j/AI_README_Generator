import os
from pathlib import Path

from app.agents.state_schema import State

from app.agents.llm_models import chat_model
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.prompts import ChatPromptTemplate


class PathCorrection(BaseModel):
    corrected_paths: list[str]


def validate_file_paths_from_LLM(state: State):
    print("\n>>>> NODE: validate_file_paths_from_LLM")
    if os.getenv("SKIP_LLM_CALLINGS", "false").lower() == "true":
        print("DEBUG MODE: SKIP validate_file_paths_from_LLM node")
        invalid_paths = []
        return {
            "valid_paths": [],
        }

    FILE_PATH_VALIDATION_TRIES = 3
    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])

    prompt = ChatPromptTemplate.from_template(
        """There is some mistake in the following paths: {invalid_paths}

        Correct them refering to this Directory tree: {directory_tree}"""
    )

    chain = prompt | chat_model.with_structured_output(PathCorrection)

    LLM_chosen_file_paths = state["LLM_chosen_file_paths"]
    invalid_paths = LLM_chosen_file_paths
    validated_file_paths = []
    for i in range(FILE_PATH_VALIDATION_TRIES):
        print(f"correcting invalid paths: {i}th try")
        for path in invalid_paths.copy():
            if os.path.exists(os.path.join(root_path, path)):
                validated_file_paths.append(path)
                invalid_paths.remove(path)

        if len(invalid_paths) == 0:
            break

        print(f"Invalid paths: {invalid_paths}")

        invalid_paths = chain.invoke(
            {
                "invalid_paths": ", ".join(invalid_paths),
                "directory_tree": state["directory_tree"],
            }
        ).corrected_paths

        print(f"Corrected paths: {invalid_paths}")

    return {
        "valid_paths": validated_file_paths,
    }
