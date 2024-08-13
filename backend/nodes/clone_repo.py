from varname import nameof as n
import os
import json
import subprocess
from state_schema import State
from langchain_core.pydantic_v1 import BaseModel, Field

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    FunctionMessage,
    SystemMessage,
    HumanMessage,
)


def clone_repo(state: State):
    print("==>> clone_repo node started")
    clone_url = state.get("clone_url", None)

    if not clone_url:
        raise ValueError("clone_url is not provided in the state")

    # print current directory
    print("Current directory: ", os.getcwd())


    # result = subprocess.run(
    #     "rm -rf ./cache/*",
    #     capture_output=True,
    #     check=True,
    #     text=True,
    #     shell=True,
    # )

    # create the target dir
    os.makedirs("./cache/cloned_repositories", exist_ok=True)

    target_dir = os.path.join(
        "./cache/cloned_repositories", state["title"].replace("/", "_")
    )
    try:
        print("start cloning ", clone_url)
        if not os.path.exists(target_dir):
            result = subprocess.run(
                "git clone " + clone_url + " " + target_dir,
                capture_output=True,
                check=True,
                text=True,
                shell=True,
            )
        else:
            print(f"Directory {target_dir} already exists. Skipping clone.")    
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        print(f"Return code: {e.returncode}")
        print(f"Output: {e.output}")
        print(f"Error output: {e.stderr}")
        raise e

    return
