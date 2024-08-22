import modal
from modal import App, Image, Volume, asgi_app, Secret

from app.fasthtml_app import app as web_app

app = App("frontend_ai-readme-generator")

image = Image.debian_slim(python_version="3.12.2").pip_install(
    "python_fasthtml",
    "requests",
)

main_vol = Volume.from_name("main")

@app.function(
    image=image,
    gpu=False,
    secrets=[
        Secret.from_name("my-openai-secret"),
        Secret.from_name("my-anthropic-secret"),
        Secret.from_name("my-github-secret"),
        Secret.from_name("my-langsmith-secret"),
        Secret.from_name("my-custom-secret"),
        Secret.from_name("backend_base_url"),
    ],
    volumes={"/vol": main_vol},
    timeout=600,  # 10 minutes
    container_idle_timeout=600,
)
@asgi_app()
def fastapi_asgi():
    return web_app
