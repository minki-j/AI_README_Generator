import os
import re
import time
from fasthtml.common import *

from app.utils.get_repo_info import get_repo_info
from app.utils.db_functions import initialize_db
from app.utils.check_quota import check_quota
from app.agents.main_graph import main_graph

from app.global_vars import STEP_LIST

from app.agents.state_schema import RetrievalMethod


async def step_initializer(
    session,
    request: Request,
    project_id: str,
):
    print("\n>>>> CTRL: step_initializer")
    check_quota_response = check_quota(session)
    if check_quota_response is not None:
        return check_quota_response

    form = await request.form()
    clone_url = form.get("clone_url")

    if os.path.exists(f"/vol"):
        cache_dir = f"/vol/cache"
        os.makedirs(cache_dir, exist_ok=True)
    else:
        cache_dir = "./cache"
        os.makedirs("./cache", exist_ok=True)

    repo_info = get_repo_info(clone_url, cache_dir)
    initial_state = {
        **repo_info,
        "total_number_of_steps": len(STEP_LIST),
        "previous_step": 0,
        "current_step": 1,
        "step_question": STEP_LIST[0],
        "colbert_threshold": 10,
        "retrieval_method": RetrievalMethod.FAISS,
        "invalid_paths": [],
    }

    try:
        r = main_graph.invoke(
            initial_state,
            {"configurable": {"thread_id": project_id}},
        )
        session["quota"] = (session["quota"][0] - 1, session["quota"][1])
        results = r.get("results", {})
        retrieved_chunks = r.get("retrieved_chunks", None)

    except Exception as e:
        raise e

    answer = results.get("1", [{}])[0].get("answer")
    if not answer:
        raise Exception("No answer found")

    r = initialize_db(
        session["session_id"],
        project_id,
        answer,
        STEP_LIST[0]["feedback_question"],
        retrieved_chunks,
        repo_info["directory_tree_dict"],
    )
    if r:
        full_route = str(request.url_for("step_view"))
        route = full_route.replace(str(request.base_url), "")
        print(f"Redirecting to: /{route}?step_num=1&project_id={project_id}")
        return RedirectResponse(
            url=f"/{route}?step_num=1&project_id={project_id}", status_code=303
        )
