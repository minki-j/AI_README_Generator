import os

from fastapi import APIRouter, Form

from app.langgraph.main_graph import main_graph
from ..common import THREAD
from app.feedback_scenario.middle_step_list import middle_step_list
from app.utils.get_repo_info import get_repo_info

router = APIRouter()


@router.get("")
def root():
    print("--- /start POST ---")
    return {"message": "/recieveProject route working fine"}


@router.post("")
def recieve_project(project: dict):
    print("--- /start POST ---")

    clone_url = project.get("clone_url")

    # create directory for user and the project
    cache_dir = f"/vol/cache"
    os.makedirs(cache_dir, exist_ok=True)

    repo_info = get_repo_info(clone_url, cache_dir)
    print(f"==>> repo_info: {repo_info}")

    res = main_graph.invoke(
        {
            **repo_info,
            "cache_dir": cache_dir,
            "steps": [],
            "analysis_results": [],
            "final_hypotheses": [],
            "validate_count": 0,
            "retrieval_count": 0,
            "hypothesis_count": 0,
        },
        THREAD,
    )

    llm_output = res.get("final_hypotheses", [])[0]["hypothesis"]

    return {
        "next_step": middle_step_list[0]["feedback_question"],
        "llm_output": llm_output,
    }
