"""This script is for analyzing a single repository without using Airflow. 
Change the clone_url to the repository you want to analyze."""

import os
import re
import subprocess

from utils.github_api_call import fetch_commits
from utils.request import github_api_request
from utils.generate_tree import generate_tree

from main_graph import langgraph_app

CLONE_URL = "https://github.com/minki-j/GitMeetup.git"

def get_repo_info(clone_url):
    repo_info = {}
    repo_info["clone_url"] = clone_url
    repo_info["user"] = clone_url.split("/")[-2]
    repo_info["title"] = clone_url.split("/")[-1].replace(".git", "")
    repo_info["repo_root_path"] = f"./cache/cloned_repositories/{repo_info['title']}/"

    # get the directory tree
    commits, _, _, _, _ = fetch_commits(
        f'https://api.github.com/repos/{repo_info["user"]}/{repo_info["title"]}/commits',
        params={"per_page": 3},
    )
    last_commit_sha = commits[0]["sha"]
    response = github_api_request(
        "GET",
        f'https://api.github.com/repos/{repo_info["user"]}/{repo_info["title"]}/git/trees/{last_commit_sha}',
        last_fetch_at=None,
        params={"recursive": "true"},
    )
    data = response.json()
    tree = data["tree"]
    repo_info["directory_tree"] = generate_tree([item["path"] for item in tree])

    # clone the repository
    clone_dir = os.path.join("./cache/cloned_repositories", repo_info["title"])
    try:
        print("start cloning ", clone_url)
        result = subprocess.run(
            "git clone " + clone_url + " " + clone_dir,
            capture_output=True,
            check=True,
            text=True,
            shell=True,
        )
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            print("Skipping cloning since the directory is already there")
        else:
            print(f"Error cloning repository: {e}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")

    # get the list of packages used
    requirement_dir = os.path.join("./cache/packages_used", repo_info["title"])
    subprocess.run(
        "mkdir -p " + requirement_dir + " && ls",
        capture_output=True,
        check=True,
        text=True,
        shell=True,
    )
    save_path = os.path.join(requirement_dir, "requirements.txt")
    subprocess.run(
        "pipreqs --scan-notebooks --mode no-pin --savepath "
        + save_path
        + " "
        + clone_dir,
        capture_output=True,
        check=True,
        text=True,
        shell=True,
    )
    with open(save_path, "r") as f:
        requirements = f.read().splitlines()

    requirements = [
        re.sub(r"==.*", "", requirement)
        for requirement in requirements
    ]
    print(f"python packages: {requirements}")

    repo_info["packages_used"] = ", ".join(requirements)

    return repo_info

repo_info = get_repo_info(CLONE_URL)

result = langgraph_app.invoke(
    {
        **repo_info,
        "steps": [],
        "analysis_results": [],
        "final_hypotheses": [],
        "validate_count": 0,
        "retrieval_count": 0,
        "hypothesis_count": 0,
    },
    {"recursion_limit": 100},
)

os.makedirs("./cache/results", exist_ok=True)
with open(f"./cache/results/{repo_info["title"]}.txt", "w") as f:
    f.write(f"LLM's analysis of {repo_info['title']}\nRepo URL: {repo_info['clone_url']}\n\n\n")
    f.write(
        "\n\n-----------\n\n".join(
            [x["hypothesis"] for x in result["final_hypotheses"]]
        )
    )
