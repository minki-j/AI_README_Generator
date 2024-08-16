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

repo_info = get_repo_info(clone_url=CLONE_URL, cache_dir="./cache")

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
    {"configurable": {"thread_id": "2"}, "recursion_limit": 100}
)

os.makedirs("./cache/results", exist_ok=True)
with open(f"./cache/results/{repo_info["title"]}.txt", "w") as f:
    f.write(f"LLM's analysis of {repo_info['title']}\nRepo URL: {repo_info['clone_url']}\n\n\n")
    f.write(
        "\n\n-----------\n\n".join(
            [x["hypothesis"] for x in result["final_hypotheses"]]
        )
    )
