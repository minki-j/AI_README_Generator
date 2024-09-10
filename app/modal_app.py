import modal
from modal import App, Image, Volume, asgi_app, Secret

from app.fasthtml_app import app as web_app

app = App("ai-readme-generator")

image = (
    Image.debian_slim(python_version="3.12.2")
    .apt_install("graphviz", "libgraphviz-dev", "git")
    .pip_install(
        "python_fasthtml==0.5.2",
        "langchain==0.2.14",
        "langchain_core==0.2.35",
        "langchain_openai==0.1.22",
        "langchain_anthropic==0.1.23",
        "langchain_community==0.2.12",
        "langchainhub",
        "langchain_text_splitters==0.2.2",
        "langgraph==0.2.14",
        "langgraph-checkpoint==1.0.6",
        "langgraph-checkpoint-sqlite==1.0.0",
        "llama_index==0.11.1",
        "ragatouille==0.0.8.post4",
        "requests==2.32.3",
        "varname==0.13.3",
        "python-dotenv==1.0.1",
        "scikit_learn==1.5.1",
        "pendulum==3.0.0",
        "fastapi==0.112.2",
        "pipreqs==0.5.0",
        "tree_sitter==0.21.3",
        "tree_sitter_languages==1.10.2",
        "uvicorn==0.30.1",
        "graphviz==0.20.3",
        "modal==0.62.236",
        "pydantic",
        "include",
        "psycopg2_binary",
        "faiss-cpu",
        "rank_bm25",
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
