from llama_index.core.node_parser import CodeSplitter
from llama_index.core import SimpleDirectoryReader


def chunk_with_AST_parser(directory_path: str, language: str = "python"):

    documents = SimpleDirectoryReader(
        input_dir=directory_path,
        required_exts=[".py"],
        recursive=True,
    ).load_data()

    code_splitter = CodeSplitter.from_defaults(
        language=language,
        chunk_lines=40,
        chunk_lines_overlap=2,
        max_chars=1500,
    )

    return code_splitter.get_nodes_from_documents(documents)
