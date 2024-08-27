import modal
from modal import App, Image, Volume, asgi_app, Secret

from app.fasthtml_app import app as web_app

app = App("ai-readme-generator")

image = (
    Image.debian_slim(python_version="3.12.2")
    .apt_install("graphviz", "libgraphviz-dev", "git")
    .pip_install(
        "python_fasthtml==0.4.5",
        "requests",
        "langchain",
        "langchain_core",
        "langchain-openai",
        "langchain_anthropic",
        "langchain_community",
        "langchainhub",
        "langchain_text_splitters",
        "langgraph==0.1.8",
        "langgraph-checkpoint==1.0.6",
        "langgraph-checkpoint-sqlite==1.0.0",
        "varname",
        "python-dotenv",
        "scikit_learn",
        "pendulum",
        "fastapi",
        "include",
        "Requests",
        "psycopg2_binary",
        "pydantic==1.10.2",
        "pipreqs",
        "faiss-cpu",
        "rank_bm25",
        "RAGatouille",
        "tree-sitter<0.22.0",
        "tree_sitter_languages",
    )
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
    ],
    volumes={"/vol": main_vol},
    timeout=600,  # 10 minutes
    container_idle_timeout=600,
)
@asgi_app()
def fasthtml_asgi():
    return web_app
