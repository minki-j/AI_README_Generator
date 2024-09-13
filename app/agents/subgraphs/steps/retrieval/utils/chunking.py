from llama_index.core.node_parser import CodeSplitter
from llama_index.core import SimpleDirectoryReader

from app.utils.converters import convert_docs_from_llamaindex_to_langchain

def chunk_with_AST_parser(directory_path: str, language: str = "python", framework="llamaindex"):

    documents = SimpleDirectoryReader(
        input_dir=directory_path,
        required_exts=[".py"],
        recursive=True,
        exclude=["cache", "testing", "data", "assets"],
    ).load_data()

    code_splitter = CodeSplitter.from_defaults(
        language=language,
        chunk_lines=40,
        chunk_lines_overlap=2,
        max_chars=1500,
    )

    chunked_docs = code_splitter.get_nodes_from_documents(documents)

    if framework == "langchain":
        print("Converting to langchain format")
        chunked_docs = convert_docs_from_llamaindex_to_langchain(chunked_docs)

    return chunked_docs
