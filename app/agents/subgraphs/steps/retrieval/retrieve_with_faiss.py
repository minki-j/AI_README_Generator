import os
import gc
import pickle
import psutil

from langchain_openai import OpenAIEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS

from app.agents.state_schema import State

from .utils.chunking import chunk_with_AST_parser


def retrieve_with_faiss(state: State):
    print("\n>>>> NODE: retrieve_with_faiss")

    cache_dir = state["cache_dir"] 
    cloned_repository_root_path = f"{cache_dir}/{state['title']}/cloned_repositories"
    doc_path = f"{cache_dir}/{state['title']}/chunked_doc_langchain/documents.pkl"
    index_path = f"{cache_dir}/{state['title']}/faiss_vectorstore"

    if os.path.exists(doc_path) and os.path.exists(index_path):
        print("Loading cached documents and embeddings")
        with open(doc_path, "rb") as f:
            documents = pickle.load(f)
        embedding = OpenAIEmbeddings(model="text-embedding-3-large")
        faiss_vectorstore = FAISS.load_local(
            f"{cache_dir}/{state['title']}/faiss_vectorstore",
            embedding,
            allow_dangerous_deserialization=True,
        )
    else:
        print(f"Parse and create embeddings for {state['title']}")
        os.makedirs(
            f"{cache_dir}/{state['title']}/chunked_doc_langchain", exist_ok=True
        )

        documents = chunk_with_AST_parser(
            cloned_repository_root_path, language="python", framework="langchain"
        )
        if not documents:
            print("No documents found")
            raise ValueError("No documents found")

        with open(doc_path, "wb") as f:
            pickle.dump(documents, f)

        print(f"Creating FAISS vectorstore for {len(documents)} documents")
        embedding = OpenAIEmbeddings(model="text-embedding-3-large")
        faiss_vectorstore = FAISS.from_documents(documents, embedding)

        faiss_vectorstore.save_local(index_path)

    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 2

    faiss_retriever = faiss_vectorstore.as_retriever(search_kwargs={"k": 2})

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
    )
    retrieved_code_snippets = []
    for query in state["step_question"]["queries"]:  # TODO parallelize this
        result = ensemble_retriever.invoke(query)
        retrieved_code_snippets.extend(result)

    print(f"Retrieved {len(retrieved_code_snippets)} code snippets (hybrid search)")

    retrieved_code_snippets_dict = {
        document.metadata["source"].split("cloned_repositories/")[
            -1
        ]: document.page_content
        for document in retrieved_code_snippets
    }

    return {
        "retrieved_chunks": retrieved_code_snippets_dict,
        "opened_files": [
            document.metadata["source"] for document in retrieved_code_snippets
        ],
    }
