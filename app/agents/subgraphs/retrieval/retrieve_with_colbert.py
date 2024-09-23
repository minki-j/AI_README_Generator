import os
import pickle

from ragatouille import RAGPretrainedModel

from app.agents.state_schema import State

from .chunking import chunk_with_AST_parser
from .index_for_colbert import index_documents_with_colbert


def retrieve_with_colbert(state: State):
    print("\n>>>> NODE: retrieve_with_colbert")

    cache_dir = state["cache_dir"]

    queries = state["step_question"]["queries"]
    cloned_repo_root_path = f"{state['cache_dir']}/{state['title']}/cloned_repositories"

    doc_path = f"{cache_dir}/{state['title']}/chunked_doc_llamaindex/documents.pkl"
    index_path = f"{cache_dir}/{state['title']}/colbert/indexes/1"

    if os.path.exists(doc_path) and os.path.exists(index_path):
        print("Loading cached documents and embeddings")
        with open(doc_path, "rb") as f:
            documents = pickle.load(f)

    else:
        print("Embedidngs does not exist")
        os.makedirs(
            f"{cache_dir}/{state['title']}/chunked_doc_llamaindex", exist_ok=True
        )

        documents = chunk_with_AST_parser(cloned_repo_root_path, language="python")
        if not documents:
            print("No documents found")
            raise ValueError("No documents found")

        with open(doc_path, "wb") as f:
            pickle.dump(documents, f)

        index_documents_with_colbert(documents, f"{cache_dir}/{state['title']}", "1")

    RAG = RAGPretrainedModel.from_index(index_path, verbose=0)

    retrieved_code_snippets = []
    for query in queries:  # TODO parallelize this
        print(f"\n\n>>>> >>Searching for query: \n{query}<<<<<\n\n")
        results = RAG.search(
            query,
            k=5,
        )

        retrieved_code_snippets.extend(
            [
                result["content"]
                for result in results
                if result["score"] > state["colbert_threshold"]
            ]
        )

    print(f"Retrieved {len(retrieved_code_snippets)} code snippets")

    retrieved_code_snippets_dict = {
        "path_placeholder_for_colbert": document
        for document in retrieved_code_snippets
    }

    return {
        "retrieved_chunks": retrieved_code_snippets_dict,
        "opened_files": ["path_placeholder_for_colbert"],
    }

    # TODO: RAGatouille doesn't add metatdata to the documents so we need to add it manually
