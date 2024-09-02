"""This script is for analyzing a single repository without using Airflow. 
Change the clone_url to the repository you want to analyze."""

import os

from app.agents.main_graph import main_graph
from app.utils.get_repo_info import get_repo_info

from app.assets.step_list import STEP_LIST

CLONE_URL = "https://github.com/minki-j/AI_README_Generator.git"

current_dir = os.getcwd()
repo_info = get_repo_info(clone_url=CLONE_URL, cache_dir=f"{current_dir}/cache")
config = {"configurable": {"thread_id": "3"}, "recursion_limit": 100}

result = main_graph.invoke(
    {
        **repo_info,
        "step_question": STEP_LIST[0],
        "current_step": 1,
        "total_number_of_steps": len(STEP_LIST),
    },
    config,
)

for i in range(len(STEP_LIST) - 1):
    print(f"--------{i+1}---------")
    user_feedback = input("Enter a feedback:")

    main_graph.update_state(
        config,
        {
            "user_feedback": user_feedback,
            "current_step": int(i + 2),
            "step_question": STEP_LIST[i + 1],
        },
    )
    result = main_graph.invoke(None, config)

print("-----------------")
print(result)
