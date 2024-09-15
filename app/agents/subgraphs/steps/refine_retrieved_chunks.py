import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.agents.state_schema import State
from app.agents.common import chat_model_small


def trim_retrieved_chunk(question: str, retrieved_chunks: str) -> str:
    prompt = ChatPromptTemplate.from_template(
        """Leave only the parts of the code snippets that are most relevant to the question and replace the rest with "...". If the entire code snippet is not relevant, return None.
        <question>
        {question}
        </question>
        <code_snippets>
        {retrieved_chunks}
        </code_snippets>
        """
    )

    chain = prompt | chat_model_small

    response = chain.invoke(
        {
            "question": question,
            "retrieved_chunks": retrieved_chunks,
        }
    )

    return response.content

def refine_retrieved_chunks(state: State) -> State:
    print("\n>>>> NODE: trim_retrieved_chunks")

    trimmed_chunks = {}
    long_chunks = {}
    for path, chunk in state["retrieved_chunks"].items():
        if len(chunk) > 1500:
            print(f"==>> path: {path}, len: {len(chunk)}")
            long_chunks[path] = chunk
        else:
            print(f"==>> path: {path}, len: {len(chunk)}")
            trimmed_chunks[path] = chunk
    queries = ", ".join(state["step_question"]["queries"])

    with ThreadPoolExecutor() as executor:
        future_to_chunk = {
            executor.submit(
                trim_retrieved_chunk,
                queries,
                chunk,
            ): path
            for path, chunk in long_chunks.items()
        }
        for future in as_completed(future_to_chunk):
            path = future_to_chunk[future]
            chunk = future.result()
            trimmed_chunks[path] = chunk

    return {
        "retrieved_chunks": {
            "replace": True,
            **trimmed_chunks,
        }
    }
