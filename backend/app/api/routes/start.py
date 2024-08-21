import os

from fastapi import APIRouter, Form

from app.langgraph.main_graph import main_graph
from ..common import THREAD
from app.data.middle_step_list import middle_step_list
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
    initial_state = {
        **repo_info,
        "middle_step": middle_step_list[0],
    }
    print("initial_state: ", initial_state)
    res = main_graph.invoke(
        initial_state,
        THREAD,
    )

    answered_middle_steps = res.get("answered_middle_steps", None)
    retrieved_chunks = res.get("retrieved_chunks", None)

    if not answered_middle_steps:
        return {"feedback_question": "No final hypothesis found", "answer": ""}
    else:
        return {
            "feedback_question": answered_middle_steps[-1]["feedback_question"],
            "answer": answered_middle_steps[-1]["answer"],
            "retrieved_chunks": retrieved_chunks,
        }
