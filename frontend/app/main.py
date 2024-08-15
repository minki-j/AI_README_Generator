import modal 
from modal import asgi_app, Secret

from app.common import app as modal_app, image, vol
from app.home.main import app


@modal_app.function(
    image=image,
    gpu=False,
    secrets=[
        Secret.from_name("my-openai-secret"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("langsmith"),
        Secret.from_name("my-github-secret"),
        Secret.from_name("WriteMeReadMe_Global_Variables"),
    ],
    volumes={"/vol": vol},
    timeout=600,  # 10 minutes
    container_idle_timeout=600,
)
@asgi_app()
def fastapi_asgi():
    return app
