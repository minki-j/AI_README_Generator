from modal import App, Image, Volume
from app.utils.env_converter import env_converter

app = App("backend_ai-readme-generator")

image = (
    Image.debian_slim(python_version="3.12.2")
    .apt_install("graphviz", "libgraphviz-dev")
    .pip_install(
        "langchain",
        "langchain_core",
        "langchain-openai",
        "langchain_anthropic",
        "langchain_community",
        "langchainhub",
        "langchain_text_splitters",
        "langgraph",
        "varname",
        "python-dotenv",
        "scikit_learn",
        "pendulum",
        "fastapi",
        "include",
        "Requests",
        "psycopg2_binary",
        "pydantic==1.10.2",
    )
)

main_vol = Volume.from_name("main")
