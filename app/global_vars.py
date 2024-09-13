DEBUG = False
RETRIEVAL = "faiss"
SKIP_LLM_CALLINGS = True
STEP_LIST = [
    {
        "prompt": "What are the core packages used in this project?",
        "queries": [],
        "feedback_question": "Are these packages core to your project?",
        "retrieval_needed": False,
        "repo_info_to_look_up": [
            "packages_used",
            "directory_tree",
        ],
    },
    {
        "prompt": "Write the summary of this repository in 200 words or less.",
        "queries": ["Summary of the repository", "What is this repository about?"],
        "feedback_question": "Does this summary look good to you?",
        "retrieval_needed": True,
        "repo_info_to_look_up": [],
    },
    {
        "prompt": "List what technologies are used in this repository",
        "queries": [
            "Technologies used in the repository",
            "What technologies are used in this repository?",
        ],
        "feedback_question": "Does this technology list look good to you?",
        "retrieval_needed": False,
        "repo_info_to_look_up": [],
    },
    # {
    #     "prompt": "What is the entry point of the codebase?",
    #     "queries": ["Entry point of the codebase", "How to run the codebase"],
    #     "feedback_question": "Is this the entry point of your project?",
    #     "retrieval_needed": False,
    #     "repo_info_to_look_up": [],
    # },
    # {
    #     "prompt": "Write the installation instructions for this repository.",
    #     "queries": ["Installation instructions", "How to install this repository?"],
    #     "feedback_question": "Does this installation instruction look good to you?",
    #     "retrieval_needed": False,
    #     "repo_info_to_look_up": [],
    # },
    # {
    #     "prompt": "Write the usage instructions for this repository.",
    #     "feedback_question": "Does this usage instruction look good to you?",
    #     "retrieval_needed": False,
    #     "repo_info_to_look_up": [],
    # },
    # {
    #     "prompt": "Write the contribution guidelines for this repository.",
    #     "feedback_question": "Does this contribution guideline look good to you?",
    #     "retrieval_needed": False,
    #     "repo_info_to_look_up": [],
    # },
]
