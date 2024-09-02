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


class StepResult(TypedDict):
    answer: str
    opened_files: List[str]


class State(TypedDict):
    def merge_lists(original: list, new_result: list) -> list:
        if new_result == "RESET":
            return []
        for item in new_result:
            if item not in original:
                original.append(item)
        return original

    def merge_results(
        original: Dict[int, List[StepResult]],
        new_result: Dict[int, List[StepResult]],
    ) -> Dict[int, List[StepResult]]:
        if new_result == "RESET":
            return {}
        for step, step_results in new_result.items():
            if step not in original:
                original[step] = step_results
            else:
                for result in step_results:
                    # Check if an equivalent result already exists
                    if not any(
                        r["answer"] == result["answer"]
                        and r["opened_files"] == result["opened_files"]
                        for r in original[step]
                    ):
                        original[step].append(result)
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
    step_question: StepQ
    user_feedback: str
    directory_tree_dict: dict  # For indicating which files are retrieved

    # Long Term Memory
    results: Annotated[Dict[int, List[StepResult]], merge_results]

    # Outputs
    generated_readme: str
