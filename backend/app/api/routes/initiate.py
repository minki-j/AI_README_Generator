import os

from fastapi import APIRouter, Form

from app.langgraph.main_graph import main_graph
from ..common import THREAD

router = APIRouter()


@router.get("")
def root():
    print("--- / GET ---")
    return {"message": "/recieveProject route working fine"}


@router.post("")
def recieve_project(clone_url: str = Form(...)):
    print("--- /initiate POST ---")
    print(f"clone_url: {clone_url}")
    print("vol dir list: ", os.listdir("/vol"))
    user_name = clone_url.split("/")[-2]
    print(f"user_name: {user_name}")
    title = clone_url.split("/")[-1]
    print(f"title: {title}")

    # create directory for user and the project
    project_dir = f"/vol/{user_name}/{title}"
    os.makedirs(project_dir, exist_ok=True)
    print(f"project_dir: {project_dir}")

    res = main_graph.invoke(
        {
            "clone_url": clone_url,
        },
        THREAD,
    )

    print("res: ", res)

    return {"message": "recieveProject route working fine"}
