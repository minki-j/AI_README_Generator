import os
import pickle
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)
from langchain_core.documents.base import Document
from sklearn.metrics.pairwise import cosine_similarity


def semantic_code_splitter(root_path, embedding_max_length=8191):
    # Average length of string per token = 4.35 - 5.00
    embedding_max_length_for_string = embedding_max_length * 4
    document_path = root_path
    loader = DirectoryLoader(
        document_path,
        glob=["*.py"],  # "*.md", "*.ts", "*.js", "*.tsx", "*.jsx"
        loader_cls=TextLoader,
        recursive=True,
    )
    documents = loader.load()

    if not documents:
        print("No documents found in the specified directory.")
        raise Exception("No documents found in the specified directory.")

    # Python Seperators: ['\nclass ', '\ndef ', '\n\tdef ', '\n\n', '\n', ' ', '']
    python_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=200,
        chunk_overlap=0,
        keep_separator=True,
        strip_whitespace=False,
    )
    print(f"Splitting {len(documents)} documents...")
    documents = python_splitter.split_documents(documents)

    openAIEmbedding = OpenAIEmbeddings(model="text-embedding-3-large")
    print(f"Embedding {len(documents)} split documents...")
    embeddings = openAIEmbedding.embed_documents(
        [document.page_content for document in documents]
    )

    # group documents with the same metadata source value and merge embeddings
    documents_grouped_by_source = {}
    for doc, embedding in zip(documents, embeddings):
        source = doc.metadata["source"]
        if source not in documents_grouped_by_source:
            documents_grouped_by_source[source] = []
        documents_grouped_by_source[source].append(
            {"content": doc.page_content, "embedding": embedding}
        )

    print("Calculating semantic similarities...")
    cosine_similarities = []
    for source, docs_in_same_source in documents_grouped_by_source.items():
        cosine_similarities_grouped_by_source = {"source": source, "similarities": []}
        for i in range(len(docs_in_same_source) - 1):
            cosine_similarity_result = cosine_similarity(
                [docs_in_same_source[i]["embedding"]],
                [docs_in_same_source[i + 1]["embedding"]],
            )
            cosine_similarities_grouped_by_source["similarities"].append(
                cosine_similarity_result[0][0]
            )
        cosine_similarities.append(cosine_similarities_grouped_by_source)

    print("Merging semantically similar documents...")
    documents_after_semantic_merging = []
    for (source, document), cosine_similarities_grouped_by_source in zip(
        documents_grouped_by_source.items(), cosine_similarities
    ):
        if source != cosine_similarities_grouped_by_source["source"]:
            print(
                f"Source mismatch: {source} vs {cosine_similarities_grouped_by_source['source']}"
            )
            raise Exception("Source mismatch")

        merged_chunk = ""
        for idx, similarity in enumerate(
            cosine_similarities_grouped_by_source["similarities"]
        ):
            # print(f"Similarity between {idx} and {idx+1}: {similarity}")
            # print("sentence 1: ", document[idx]["content"])
            # print("sentence 2: ", document[idx+1]["content"])
            # print("-------------------------------------------------")
            if similarity > 0.7:
                if len(merged_chunk) == 0:
                    merged_chunk = (
                        document[idx]["content"] + document[idx + 1]["content"]
                    )
                if len(merged_chunk) > embedding_max_length_for_string:
                    print("Merged chunk length exceeds the limit at ", source)
                    documents_after_semantic_merging.append(
                        Document(merged_chunk, metadata={"source": source})
                    )
                    merged_chunk = ""
                else:
                    merged_chunk += document[idx + 1]["content"]
            else:
                documents_after_semantic_merging.append(
                    Document(merged_chunk, metadata={"source": source})
                )

    return documents_after_semantic_merging
