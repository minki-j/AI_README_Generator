from fastapi import APIRouter

from app.langgraph.main_graph import main_graph
from ..common import THREAD

router = APIRouter()


@router.get("")
def root():
    return {"message": "/middleSteps route working fine"}

@router.post("")
def middle_steps():
    print("--- /middleSteps POST ---")
    res = main_graph.invoke(None, THREAD)
    print(f"==>> res: {res}")
    return {"message": "middleSteps route working fine"}