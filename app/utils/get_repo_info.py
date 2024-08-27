import os
import re
import subprocess

from app.utils.github_api_call import fetch_commits
from app.utils.request import github_api_request
from app.utils.generate_tree import generate_tree


def get_repo_info(clone_url, cache_dir):
    repo_info = {}
    repo_info["clone_url"] = clone_url
    repo_info["user"] = clone_url.split("/")[-2]
    repo_info["title"] = clone_url.split("/")[-1].replace(".git", "")
    repo_info["cache_dir"] = cache_dir

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
    clone_dir = os.path.join(cache_dir, "cloned_repositories", repo_info["title"])
    try:
        subprocess.run(
            "git clone " + clone_url + " " + clone_dir,
            capture_output=True,
            check=True,
            text=True,
            shell=True,
        ) # this will throw an error if the directory is already there
        print("Cloned the repository ", clone_url)
    except subprocess.CalledProcessError as e:
        if e.returncode == 128:
            print("Skipping cloning since the directory is already there")
        else:
            print(f"Error cloning repository: {e}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")

    # get the list of packages used
    requirement_dir = os.path.join(cache_dir, "packages_used", repo_info["title"])
    os.makedirs(requirement_dir, exist_ok=True)
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

    requirements = [re.sub(r"==.*", "", requirement) for requirement in requirements]

    repo_info["packages_used"] = ", ".join(requirements)

    return repo_info
