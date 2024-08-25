import os
import json
import pickle
from varname import nameof as n
from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS

from ragatouille import RAGPretrainedModel

from app.agents.state_schema import State

from .chunking import chunk_with_AST_parser
from .colbert import index_documents_with_colbert

from app.global_vars import SKIP_COLBERT


def retrieve_code_by_hybrid_search_with_queries(state: State):
    print("Retrieving code snippets for ", state["title"])
    if SKIP_COLBERT:
        print("ColBERT is disabled")
        return {"retrieved_chunks": []}

    cache_dir = state["cache_dir"]
    queries = state["middle_step"]["queries"]
    root_path = str(Path(state["cache_dir"]) / "cloned_repositories" / state["title"])

    doc_path = f"{cache_dir}/{state['title']}/documents.pkl"
    index_path = f"{cache_dir}/colbert/indexes/{state['title']}"

    if os.path.exists(doc_path) and os.path.exists(index_path):
        print("Loading cached documents and embeddings")
        with open(doc_path, "rb") as f:
            documents = pickle.load(f)

    else:
        print("Embedidngs does not exist")
        os.makedirs(f"{cache_dir}/{state['title']}", exist_ok=True)

        documents = chunk_with_AST_parser(root_path, language="python")
        if not documents:
            print("No documents found")
            raise ValueError("No documents found")

        with open(doc_path, "wb") as f:
            pickle.dump(documents, f)

        index_documents_with_colbert(documents, cache_dir, state["title"])

    RAG = RAGPretrainedModel.from_index(index_path, verbose=0)

    retrieved_code_snippets = []
    for query in queries:  # TODO parallelize this
        print(f"--------Searching for query: {query}")
        results = RAG.search(
            query,
            k=5,
        )
        retrieved_code_snippets.extend([result["content"] for result in results])

    print(f"Retrieved {len(retrieved_code_snippets)} code snippets")

    # TODO: RAGatouille doesn't add metatdata to the documents so we need to add it manually
    # formatted_snippets = [
    #     f"{document.metadata["source"]}:\n{document.page_content}"
    #     for document in retrieved_code_snippets
    # ]

    return {
        "retrieved_chunks": retrieved_code_snippets,
        # "opened_files": [
        #     document.metadata["source"] for document in retrieved_code_snippets
        # ],
    }