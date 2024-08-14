from include.generate_readme.state_schema import State
from typing import List
import json


def convert_postgres_to_state_schema(repo: dict) -> dict:
    convert_rule = {
        "id": "id",
        "name": "title",
        "description": "repo_description_by_user",
        "tree": "directory_tree",
        "packages_used": "packages_used",
        "clone_url": "clone_url",
    }

    converted_repo = {}

    for key, value in repo.items():
        if key in convert_rule:
            converted_repo[convert_rule[key]] = value

    if converted_repo["packages_used"]:
        converted_repo["packages_used"] = converted_repo["packages_used"].split(",")

    return converted_repo
