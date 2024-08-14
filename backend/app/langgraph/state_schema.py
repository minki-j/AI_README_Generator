from typing import Annotated, TypedDict, List, Sequence
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class State(TypedDict):
    @staticmethod
    def merge_lists(attribute_instance: List, new_result: List) -> List:
        if new_result == "RESET":
            # print("\n-----------------\nReset for merge_lists")
            return []
        for item in new_result:
            if item not in attribute_instance:
                attribute_instance.append(item)
        return attribute_instance

    @staticmethod
    def concat_strings(attribute_instance: str, new_result: str) -> str:
        if new_result == "RESET":
            # print("\n-----------------\nReset for concat_strings")
            return ""
        return attribute_instance + "\n\n" + new_result

    title: str
    repo_root_path: str
    repo_description_by_user: str
    directory_tree: str
    packages_used: List[str]
    clone_url: str

    messages: Annotated[Sequence[BaseMessage], add_messages]

    invalid_paths: List[str] = []
    valid_paths: Annotated[List[str], merge_lists] = []
    corrected_paths: List[str] = []
    validate_count: int = 0

    candidate_hypothesis: dict
    analysis_results: Annotated[List[dict], merge_lists] = []
    final_hypotheses: Annotated[List[dict], merge_lists] = []

    retrieved_code_snippets: Annotated[str, concat_strings] = ""
    opened_files: Annotated[List[str], merge_lists] = []
    retrieval_count: int = 0

    hypothesis_count: int = 0
