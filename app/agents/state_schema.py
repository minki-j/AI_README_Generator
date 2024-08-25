from typing import Annotated, TypedDict, List, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class MiddleStep(TypedDict):
    prompt: str
    queries: List[str]
    feedback_question: str
    answer: str

class State(TypedDict):
    def merge_lists(attribute_instance: List, new_result: List) -> List:
        if new_result == "RESET":
            # print("\n-----------------\nReset for merge_lists")
            return []
        for item in new_result:
            if item not in attribute_instance:
                attribute_instance.append(item)
        return attribute_instance

    def concat_strings(attribute_instance: str, new_result: str) -> str:
        if new_result == "RESET":
            # print("\n-----------------\nReset for concat_strings")
            return ""
        return attribute_instance + "\n\n" + new_result

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
    current_step: int
    retrieval_count: int
    retrieved_chunks: Annotated[list[MiddleStep], merge_lists]
    middle_step: MiddleStep
    user_feedback_list: Annotated[list[str], merge_lists]
    scatch_pad: str

    # Long Term Memory
    messages: Annotated[Sequence[BaseMessage], add_messages]
    opened_files: Annotated[List[str], merge_lists]
    answered_middle_steps: Annotated[List[str], merge_lists]
    generated_readme: str
