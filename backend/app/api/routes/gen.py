from fastapi import APIRouter
from fastapi import Body, Form, Query

from app.langgraph.main_graph import main_graph
from ..common import THREAD
from app.data.middle_step_list import middle_step_list

router = APIRouter()

@router.post("")
def root(id: str = Query(...), step: str = Query(...)):
    print("--- /gen POST ---")
    
@router.get("")
def root(id: str = Query(...), step: str = Query(...)):
    print("--- /gen GET ---")
    print(f"==>> id: {id}")
    print(f"==>> step: {step}")
    for state in main_graph.get_state_history(THREAD):
        last_state = state
        break
    print("==>> last_state: ", last_state)
    answered_middle_steps = last_state.get(
        "answered_middle_steps",
        {"configurable": {"thread_id": id}},
    )
    retrieved_chunks = last_state.get("retrieved_chunks", None)

    return {
        "feedback_question": answered_middle_steps[-1]["feedback_question"],
        "answer": answered_middle_steps[-1]["answer"],
        "retrieved_chunks": retrieved_chunks,
    }
