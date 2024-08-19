"""This script is for analyzing a single repository without using Airflow. 
Change the clone_url to the repository you want to analyze."""

import os
import re
import subprocess

from app.utils.github_api_call import fetch_commits
from app.utils.request import github_api_request
from app.utils.generate_tree import generate_tree

from app.langgraph.main_graph import main_graph
from app.utils.get_repo_info import get_repo_info


CLONE_URL = "https://github.com/minki-j/GitMeetup.git"

# repo_info = get_repo_info(clone_url=CLONE_URL, cache_dir="./cache")
repo_info = {
    "clone_url": "https://github.com/minki-j/GitMeetup.git",
    "user": "minki-j",
    "title": "GitMeetup",
    "repo_root_path": "./cache/cloned_repositories/GitMeetup/",
    "directory_tree": "├── .astro\n│ ├── config.yaml\n│ ├── dag_integrity_exceptions.txt\n│ ├── test_dag_integrity_default.py\n├── .dockerignore\n├── .env.example\n├── .gitignore\n├── Dockerfile\n├── README.md\n├── dags\n│ ├── .airflowignore\n│ ├── __init__.py\n│ ├── analyze_repositories.py\n│ ├── common_tasks\n│ │ ├── __init__.py\n│ │ ├── get_column_names.py\n│ ├── fetch_full_repositories.py\n│ ├── fetch_repositories.py\n│ ├── fetch_user_full_info.py\n│ ├── search_users_by_location.py\n├── graph_diagrams\n│ ├── main_graph.png\n│ ├── subGraph_retrieval.png\n├── include\n│ ├── __init__.py\n│ ├── generate_readme\n│ │ ├── __init__.py\n│ │ ├── common.py\n│ │ ├── graph_imgs\n│ │ │ ├── main_graph.png\n│ │ ├── langgraph.json\n│ │ ├── main_graph.py\n│ │ ├── nodes\n│ │ │ ├── __init__.py\n│ │ │ ├── check.py\n│ │ │ ├── clone_repo.py\n│ │ │ ├── hypothesis.py\n│ │ │ ├── read_files.py\n│ │ │ ├── retrieve_code_snippets.py\n│ │ │ ├── validate_file_path.py\n│ │ ├── state_schema.py\n│ │ ├── subgraphs\n│ │ │ ├── __init__.py\n│ │ │ ├── retrieval\n│ │ │ │ ├── __init__.py\n│ │ │ │ ├── graph.py\n│ │ ├── utils\n│ │ │ ├── __init__.py\n│ │ │ ├── converters.py\n│ │ │ ├── semantic_splitter.py\n│ ├── github_api_call\n│ │ ├── __init__.py\n│ │ ├── functions.py\n│ │ ├── request.py\n│ ├── postgres_functions\n│ │ ├── __init__.py\n│ │ ├── execute_query.py\n│ ├── schemas\n│ │ ├── __init__.py\n│ │ ├── github_user_schema.py\n│ ├── scripts\n│ │ ├── __init__.py\n│ │ ├── connection.py\n│ ├── sql\n│ │ ├── get_column_names.sql\n│ │ ├── get_last_modified_datetime.sql\n│ ├── utils\n│ │ ├── __init__.py\n│ │ ├── convert_column_names.py\n│ │ ├── date_utils.py\n│ │ ├── filter_users_in_parallel.py\n│ │ ├── generate_tree.py\n│ │ ├── sql_functions.py\n├── logo.jpeg\n├── requirements.txt\n├── run_manually.py\n├── tests\n│ ├── __init__.py\n│ ├── dags\n│ │ ├── __init__.py\n│ │ ├── test_dag_example.py\n",
    "packages_used": "apache-airflow, langchain, langchain_anthropic, langchain_community, langchain_core, langchain_openai, langchain_text_splitters, langgraph, pendulum, psycopg2_binary, pytest, python-dotenv, Requests, scikit_learn, varname",
}

config = {"configurable": {"thread_id": "2"}, "recursion_limit": 100}

result = main_graph.invoke(
    {
        **repo_info,
        "cache_dir": "./cache",
        "steps": [],
        "analysis_results": [],
        "final_hypotheses": [],
        "validate_count": 0,
        "retrieval_count": 0,
        "hypothesis_count": 0,
    },
    config,
)

user_feedback = input("Enter a feedback:")
for state in main_graph.get_state_history(config):
    last_state = state
    break

main_graph.update_state(
    config, {"user_feedback": user_feedback}
)
result = main_graph.invoke(None, config)


user_feedback = input("Enter a feedback:")
for state in main_graph.get_state_history(config):
    last_state = state
    break

main_graph.update_state(
    config, {"user_feedback": user_feedback}
)
result = main_graph.invoke(None, config)
print("-----------------")
print(result)
