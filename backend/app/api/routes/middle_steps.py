from fastapi import APIRouter
from fastapi import Body

from app.langgraph.main_graph import main_graph
from ..common import THREAD

router = APIRouter()


@router.get("")
def root():
    return {"message": "/middleSteps route working fine"}


@router.post("")
def middle_steps(user_feedback: str = Body(...), llm_output: str = Body(...)):
    print("--- /middleSteps POST ---")
    print(f"==>> user_feedback: {user_feedback}")
    print(f"==>> llm_output: {llm_output}")
    res = main_graph.invoke(None, THREAD)
    print(f"==>> res: {res}")
    return {
        "next_step": "Step 2: Analyzing the repository",
        "llm_output": "Analyzing the repository...",
    }
