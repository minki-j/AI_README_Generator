import json
from langchain_core.documents.base import Document


def to_path_map(node_names):
    dict = {}
    for name in node_names:
        dict[name] = name
    return dict


def convert_tree2dict(tree):
    """
    convert to dictionary in a format of {"path": False, "path": {"path": False}}
    where the value is False if it is a file, and a dictionary if it is a directory
    """
    tree_dict = {}

    def add_to_dict(path_parts, current_dict, item_type):
        if len(path_parts) == 1:
            current_dict[path_parts[0]] = {} if item_type == "tree" else False
        else:
            current_dict.setdefault(path_parts[0], {})
            add_to_dict(path_parts[1:], current_dict[path_parts[0]], item_type)

    for item in tree:
        path_parts = item["path"].split("/")
        add_to_dict(path_parts, tree_dict, item["type"])

    return tree_dict


def convert_docs_from_llamaindex_to_langchain(docs):
    lc_docs = []
    for doc in docs:
        llmaindex_doc_dict = doc.dict()
        langchain_doc_dict = {
            "page_content": llmaindex_doc_dict["text"],
            "metadata": {
                "source": llmaindex_doc_dict["metadata"]["file_path"],
            }
        }
        lc_docs.append(Document(**langchain_doc_dict))
    return lc_docs

    
