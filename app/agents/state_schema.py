from enum import Enum
from typing import Annotated, TypedDict, Dict, List


class StepQ(TypedDict):
    """
    Example:
        "prompt": "What is the entry point of the codebase?",
        "queries": ["Entry point of the codebase", "How to run the codebase"],
        "feedback_question": "Is this the entry point of your project?",
    """

    prompt: str
    queries: list[str]
    feedback_question: str
    retrieval_needed: bool
    repo_info_to_look_up: list[str]


class StepResult(TypedDict):
    answer: str
    opened_files: List[str]
    user_feedback: str
    user_selected_files: List[str]


class RetrievalMethod(Enum):
    FAISS = "Faiss"
    COLBERT = "ColBERT"


class State(TypedDict):
    def merge_lists(original: list, new_result: list) -> list:
        if new_result == "RESET":
            return []
        for item in new_result:
            if item not in original:
                original.append(item)
        return original

    def merge_results(
        original: Dict[str, List[StepResult]],
        new_result: Dict[str, List[StepResult]],
    ) -> Dict[str, List[StepResult]]:
        if new_result == "RESET":
            return {}
        for step, step_results in new_result.items():
            step = str(step)
            if step not in original:
                original[step] = step_results
            else:
                for result in step_results:
                    # Check if an equivalent result already exists
                    if not any(
                        all(
                            r.get(attr) == result.get(attr)
                            for attr in StepResult.__annotations__
                        )
                        for r in original[step]
                    ):
                        original[step].append(result)
        return original

    def update_step_question(original: StepQ, next_step_question: dict) -> StepQ:
        for key, value in next_step_question.items():
            if key in StepQ.__annotations__:
                original[key] = value
            else:
                raise ValueError(f"Key {key} not found in StepQ")
        return original

    # Inputs
    # Can't be changed after initialization
    cache_dir: str
    title: str
    user: str
    repo_description_by_user: str
    directory_tree: str
    packages_used: List[str]
    total_number_of_steps: int
    colbert_threshold: float

    # Ephemeral Variables
    # Will be reset after each step
    invalid_paths: List[str]
    valid_paths: Annotated[List[str], merge_lists]
    corrected_paths: List[str]

    # Short Term Memory
    # Will be updated after each step
    previous_step: int
    current_step: int
    retrieved_chunks: Annotated[List[str], merge_lists]
    step_question: Annotated[StepQ, update_step_question]
    user_feedback: str
    directory_tree_dict: dict  # For indicating which files are retrieved
    retrieval_method: RetrievalMethod

    # Long Term Memory
    results: Annotated[Dict[str, List[StepResult]], merge_results]

    # Outputs
    generated_readme: str
