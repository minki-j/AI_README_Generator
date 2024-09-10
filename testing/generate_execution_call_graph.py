from pycallgraph2 import PyCallGraph
from pycallgraph2 import Config
from pycallgraph2 import GlobbingFilter
from pycallgraph2.output import GraphvizOutput

from app.agents.main_graph import main_graph
import os

from app.agents.main_graph import main_graph
from app.utils.get_repo_info import get_repo_info

from app.assets.step_list import STEP_LIST


def call_graph_filtered(function_, output_png="call_graph.png", custom_include=None):
    """A call graph generator filtered"""
    config = Config()
    config.trace_filter = GlobbingFilter(include=custom_include)
    graphviz = GraphvizOutput(output_file=output_png)

    CLONE_URL = "https://github.com/minki-j/AI_README_Generator.git"

    current_dir = os.getcwd()
    repo_info = get_repo_info(clone_url=CLONE_URL, cache_dir=f"{current_dir}/cache")
    g_config = {"configurable": {"thread_id": "3"}, "recursion_limit": 100}

    with PyCallGraph(output=graphviz, config=config):
        main_graph.invoke(
            {
                **repo_info,
                "step_question": STEP_LIST[0],
                "current_step": 1,
                "total_number_of_steps": len(STEP_LIST),
                "previous_step": 0,
            },
            g_config,
        )


if __name__ == "__main__":
    call_graph_filtered(main_graph, output_png="call_graph.png", custom_include=["app.agents.main_graph"])
