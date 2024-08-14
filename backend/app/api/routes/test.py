from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {"message": "/test route working fine"}
