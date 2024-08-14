from fastapi import APIRouter

from app.langgraph.main_graph import main_graph
from ..common import THREAD

router = APIRouter()


@router.get("/")
def root():
    return {"message": "/finalStep route working fine"}

@router.post("/")
def final_step():
    res = main_graph.invoke({}, THREAD)
    return {"message": "finalStep route working fine"}