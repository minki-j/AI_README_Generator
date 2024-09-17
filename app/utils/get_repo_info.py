import os
import re
import subprocess
import shutil
from pathlib import Path

from app.utils.github_api_call import fetch_commits, github_api_request
from app.utils.generate_tree import generate_tree
from app.utils.converters import convert_tree2dict


def get_repo_info(clone_url, cache_dir):
    repo_info = {}
    repo_info["cache_dir"] = cache_dir
    repo_info["user"] = clone_url.split("/")[-2]
    repo_info["title"] = clone_url.split("/")[-1].replace(".git", "")

    # get the repo description
    response = github_api_request(
        "GET",
        f'https://api.github.com/repos/{repo_info["user"]}/{repo_info["title"]}',
        last_fetch_at=None,
        params={"per_page": 1},
    )
    data = response.json()
    repo_info["repo_description_by_user"] = data["description"]

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
    repo_info["directory_tree_dict"] = convert_tree2dict(tree)
    repo_info["directory_tree"] = generate_tree([item["path"] for item in tree])

    # clone the repository
    clone_dir = os.path.join(cache_dir, repo_info["title"], "cloned_repositories")
    if os.path.exists(clone_dir):
        print(f"Skip cloning for {repo_info['title']} since it has already been cloned")
    else:
        try:
            subprocess.run(
                ["git", "clone", clone_url, clone_dir],
                capture_output=True,
                check=True,
                text=True,
            )
            print(f"Cloned the repository {clone_url}")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
            print(f"Return code: {e.returncode}")
            print(f"Output: {e.output}")

    # get the list of packages used
    requirement_dir = os.path.join(cache_dir, repo_info["title"], "packages_used")
    os.makedirs(requirement_dir, exist_ok=True)
    save_path = os.path.join(requirement_dir, "requirements.txt")

    def run_pipreqs(clone_dir, save_path, temp_dir):
        cmd = f"pipreqs --scan-notebooks --mode no-pin --savepath {save_path} {clone_dir}"

        try:
            subprocess.run(cmd, capture_output=True, check=True, text=True, shell=True)
            print("pipreqs command executed successfully")
            return True, None
        except subprocess.CalledProcessError as e:
            match = re.search(r"ERROR: Failed on file: (.*?)$", e.stderr, re.MULTILINE)
            if match:
                return False, match.group(1)
            return False, None

    try:
        temp_dir = os.path.join(os.path.dirname(clone_dir), "temp_pipreqs")
        os.makedirs(temp_dir, exist_ok=True)
        moved_files = []
        success = False

        while not success:
            success, failed_file = run_pipreqs(clone_dir, save_path, temp_dir)
            if not success and failed_file:
                dst = os.path.join(temp_dir, failed_file)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(failed_file, dst)
                moved_files.append((failed_file, dst))
                print(f"pipreqs error on {failed_file}, moved to temporary directory and retrying")
            elif not success:
                raise Exception("Failed to run pipreqs and couldn't identify the problematic file")

        # Move files back to their original locations
        for src, dst in moved_files:
            shutil.move(dst, src)

        with open(save_path, "r") as f:
            requirements = f.read().splitlines()

        requirements = [re.sub(r"==.*", "", requirement) for requirement in requirements]
        repo_info["packages_used"] = ", ".join(requirements)

    except Exception as e:
        print(f"Error determining packages used: {e}")
        repo_info["packages_used"] = "Unable to determine packages used"

    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    return repo_info
