from fastapi import APIRouter

from app.api.routes import test, initiate, middle_steps, final_step

api_router = APIRouter()
api_router.include_router(test.router, prefix="/test", tags=["test"])

api_router.include_router(initiate.router, prefix="/initiate", tags=["initiate"])

api_router.include_router(
    middle_steps.router, prefix="/middleSteps", tags=["middleSteps"]
)

api_router.include_router(final_step.router, prefix="/finalStep", tags=["finalStep"])
