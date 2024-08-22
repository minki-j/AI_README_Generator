import os

from fastapi import APIRouter, Form, Query, Response

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
def recieve_project(
    response: Response, id: str = Query(...), clone_url: str = Form(...)
):
    print("--- /start POST ---")
    print("DEBUG MODE SKIP GRAPH")
    return {
            "feedback_question": "What is the purpose of the project?",
            "answer":"To generate README files using AI",
            "retrieved_chunks": ["TEST CHUNK"],
        }

    # create directory for user and the project
    if os.path.exists(f"/vol"):
        cache_dir = f"/vol/cache"
        os.makedirs(cache_dir, exist_ok=True)
    else:
        print("using local cache instead of Modal's storage")
        cache_dir = "./cache"
        os.makedirs("./cache", exist_ok=True)

    repo_info = get_repo_info(clone_url, cache_dir)
    initial_state = {
        **repo_info,
        "middle_step": middle_step_list[0],
        "total_number_of_steps": len(middle_step_list),
    }

    res = main_graph.invoke(
        initial_state,
        {"configurable": {"thread_id": id}},
    )

    answered_middle_steps = res.get("answered_middle_steps", None)
    retrieved_chunks = res.get("retrieved_chunks", None)

    if not answered_middle_steps:
        return {
            "feedback_question": "No final hypothesis found",
            "retrieved_chunks": [],
            "answer": "",
        }
    else:
        return {
            "feedback_question": answered_middle_steps[-1]["feedback_question"],
            "answer": answered_middle_steps[-1]["answer"],
            "retrieved_chunks": retrieved_chunks,
        }
