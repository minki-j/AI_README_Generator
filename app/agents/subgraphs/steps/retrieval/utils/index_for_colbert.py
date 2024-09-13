from ragatouille import RAGPretrainedModel
import time


def index_documents_with_colbert(documents, cache_dir, index_name):
    print("==>>NODE: index_documents_with_colbert")
    start_time = time.time()

    RAG = RAGPretrainedModel.from_pretrained(
        "colbert-ir/colbertv2.0", index_root=cache_dir
    )

    RAG.index(
        index_name=index_name,
        collection=[document.text for document in documents],
        split_documents=False,
    )

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"\n\n>>>>>>>Indexing with ColBERT is done in {elapsed_time:.2f} seconds<<<<<<<\n\n")