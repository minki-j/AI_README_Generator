from fastapi import APIRouter
from fastapi import Body

from app.langgraph.main_graph import main_graph
from ..common import THREAD
from app.feedback_scenario.middle_step_list import middle_step_list

router = APIRouter()


@router.get("")
def root():
    return {"message": "/middleSteps route working fine"}


@router.post("")
def middle_steps(user_feedback: str = Body(...), llm_output: str = Body(...)):
    print("--- /middleSteps POST ---")
    
    # res = main_graph.invoke(None, THREAD)
    # print(f"==>> res: {res}")
    
    step_number = 1
    llm_output = "Analyzing the repository..."

    return {
        "next_step": middle_step_list[step_number]["feedback_question"],
        "llm_output": llm_output,
    }
