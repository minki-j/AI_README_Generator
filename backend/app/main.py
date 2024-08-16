from fastapi import FastAPI

from app.api.main import api_router
from app.common import app, image, main_vol

from modal import asgi_app, Secret

web_app = FastAPI()
web_app.include_router(api_router)

@app.function(
    image=image,
    gpu=False,
    secrets=[
        Secret.from_name("my-openai-secret"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("my-github-secret"),
        Secret.from_name("my-langsmith-secret"),
        Secret.from_name("my-custom-secret"),
    ],
    volumes={"/vol": main_vol},
    timeout=600,  # 10 minutes
    container_idle_timeout=600,
)
@asgi_app()
def fastapi_asgi():
    print("Starting FastAPI app")
    return web_app
