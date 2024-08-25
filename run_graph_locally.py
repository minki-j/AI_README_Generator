"""This script is for analyzing a single repository without using Airflow. 
Change the clone_url to the repository you want to analyze."""

import os

from app.agents.main_graph import main_graph
from app.utils.get_repo_info import get_repo_info

from app.data.step_list import step_list

CLONE_URL = "https://github.com/minki-j/AI_README_Generator.git"

current_dir = os.getcwd()
repo_info = get_repo_info(clone_url=CLONE_URL, cache_dir=f"{current_dir}/cache")
config = {"configurable": {"thread_id": "3"}, "recursion_limit": 100}

result = main_graph.invoke(
    {
        **repo_info,
        "middle_step": step_list[0],
        "current_step": 0,
        "total_number_of_steps": len(step_list),
    },
    config,
)

for i in range(len(step_list) - 1):
    print(f"--------{i+1}---------")
    user_feedback = input("Enter a feedback:")
    for state in main_graph.get_state_history(config):
        last_state = state
        break

    main_graph.update_state(
        config,
        {
            "user_feedback_list": [user_feedback],  # Must be a list
            "current_step": int(i + 1),
            "middle_step": step_list[i + 1],
        },
    )
    result = main_graph.invoke(None, config)

print("-----------------")
print(result)