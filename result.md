# AI README Generator

## Overview

The AI README Generator is a tool designed to help developers create comprehensive and well-structured README files for their projects. By analyzing the project's directory structure, code, and dependencies, the AI README Generator provides a detailed and formatted README in markdown format.

## Features

- **Automated README Generation**: Automatically generates a README file based on the project's structure and content.
- **User Feedback Integration**: Allows users to provide feedback at each step to refine the generated content.
- **Support for Python Projects**: Currently supports Python projects with plans to extend support to other languages.
- **Interactive Steps**: Guides users through multiple steps to ensure all necessary information is included in the README.
- **Quota Management**: Manages user quotas to prevent excessive usage.

## Installation

To install the AI README Generator, clone the repository and install the required dependencies:

```bash
git clone https://github.com/minki-j/AI_README_Generator.git
cd AI_README_Generator
pip install -r requirements.txt
```

## Usage

### Running the Application

To start the application, run the following command:

```bash
python main.py
```

### Generating a README

1. **Initialize the Project**: Start by providing the GitHub clone URL of your project.
2. **Follow the Steps**: The application will guide you through several steps where you can provide feedback and additional information.
3. **Generate the README**: Once all steps are completed, the application will generate the README file.

### Example

To generate a README for a specific project, you can use the `run_graph_locally.py` script:


```1:44:run_graph_locally.py
"""This script is for analyzing a single repository without using Airflow. 
Change the clone_url to the repository you want to analyze."""

import os

from app.agents.main_graph import main_graph
from app.utils.get_repo_info import get_repo_info

from app.step_list import STEP_LIST

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
        "previous_step": 0,
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
            "current_step": i + 2,
            "step_question": STEP_LIST[i + 1],
        },
        as_node="human_in_the_loop",
    )
    result = main_graph.invoke(None, config)

print("-----------------")
print(result)
```


## Project Structure

The project is organized into several modules:

- **app/agents**: Contains the logic for generating the README, including subgraphs and state management.
- **app/controllers**: Handles the HTTP requests and user interactions.
- **app/views**: Defines the HTML views and components.
- **app/utils**: Utility functions for database operations, quota management, and more.

### Key Files

- **main.py**: Entry point of the application.
- **app/agents/subgraphs/generate_readme/generate_readme.py**: Core logic for generating the README.
- **app/controllers/step.py**: Handles the steps and user feedback.
- **app/utils/db_functions.py**: Database operations.

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file in the root directory and add the following variables:

```plaintext
DEFAULT_MODEL=your_default_model
FALLBACK_MODEL=your_fallback_model
LLM_TEMPERATURE=temperature_value
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
QUOTA_LIMIT=10
QUOTA_RESET_MINUTES=30
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

## Acknowledgements

- [LangChain](https://github.com/langchain/langchain)
- [FastAPI](https://github.com/tiangolo/fastapi)
- [Graphviz](https://graphviz.org/)

## Contact

For any questions or feedback, please open an issue on the GitHub repository.

---

This README was generated using the AI README Generator.