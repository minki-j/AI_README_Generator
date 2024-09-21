import json
import time
from fasthtml.common import *
from pprint import pprint

from app.components.step import Step
from app.utils.db_functions import (
    insert_step_db,
    update_readme_content,
    insert_step_results,
)
from app.utils.check_quota import check_quota
from app.agents.main_graph import main_graph
from app.utils.initialize_db import db
from app.utils.error_responses import error_modal

from app.step_list import STEP_LIST
from app.agents.state_schema import State
from app.agents.state_schema import RetrievalMethod


async def step_handler(
    session,
    request: Request,
    project_id: str,
    step_num: int,
):
    print("\n>>>> CTRL: step_handler")
    check_quota_response = check_quota(session)
    if check_quota_response is not None:
        return check_quota_response

    if request.headers.get("hx-trigger-name") == "next_step_button":
        user_feedback = None
        directory_tree_str = db.t.readmes.get(project_id).directory_tree_str
        directory_tree_dict = json.loads(directory_tree_str)
    elif request.headers.get("hx-trigger-name") == "step_form":
        form = await request.form()
        user_feedback = form.get("user_feedback")
        directory_tree_str = form.get("directory_tree_str")
        directory_tree_dict = json.loads(directory_tree_str)
        retrieval_method = form.get("retrieval_method", None)
        session.setdefault(
            "retrieval_method", retrieval_method if retrieval_method else "FAISS"
        )
    else:
        raise Exception(
            f"Invalid hx-trigger-name: {request.headers.get('hx-trigger-name')}"
        )

    try:
        config = {"configurable": {"thread_id": project_id}}
        main_graph.update_state(
            config,
            {
                "user_feedback": user_feedback,
                "directory_tree_dict": directory_tree_dict,
                "current_step": int(step_num),
                "step_question": STEP_LIST[step_num - 1],
                "retrieval_method": session["retrieval_method"],
            },
            as_node="human_in_the_loop",
        )
        r = main_graph.invoke(None, config)
        session["quota"] = (int(session["quota"][0]) - 1, session["quota"][1])
        results = r.get("results", {})
        retrieved_chunks = r.get("retrieved_chunks", {})
    except Exception as e:
        print(f"Error: {e}")
        return error_modal(e)

    answer = results.get(str(step_num), [{}])[-1].get("answer")
    if answer is None:
        raise Exception("Answer is None")

    r = insert_step_db(
        step_num,
        project_id,
        STEP_LIST[step_num - 1]["feedback_question"],
        answer,
        retrieved_chunks,
        directory_tree_str,
    )

    if r:
        full_route = str(request.url_for("step_view"))
        route = full_route.replace(str(request.base_url), "")
        return RedirectResponse(
            url=f"/{route}?step_num={step_num}&project_id={project_id}", status_code=303
        )
    else:
        return error_modal("Error: DB insert failed.")


async def generate_readme(session, project_id: str, request: Request):
    print("\n>>>> CTRL: generate_readme")
    if os.getenv("DEBUG", "false").lower() == "true":
        # print("DEBUG MODE. SKIP GRAPH")
        r = update_readme_content(project_id, "DEBUG MODE. README GENERATED")
        if r:
            full_route = str(request.url_for("generate_readme"))
            route = full_route.replace(str(request.base_url), "")
            return RedirectResponse(
                url=f"/{route}?project_id={project_id}", status_code=303
            )
        else:
            return error_modal("Error: update_readme_content failed")

    config = {"configurable": {"thread_id": project_id}}
    r = main_graph.update_state(
        config,
        values={
            "current_step": len(STEP_LIST) + 1,
        },
        as_node="human_in_the_loop",
    )
    r = main_graph.invoke(
        None,
        config,
    )
    session["quota"] = (int(session["quota"][0]) - 1, session["quota"][1])
    generated_readme = r.get("generated_readme", None)
    db_res = update_readme_content(project_id, generated_readme)

    # Insert results into the database
    results = r.get("results", None)

    if results:
        results_json = json.dumps(results, ensure_ascii=False)
        insert_step_results(project_id, results_json)

    if db_res:
        full_route = str(request.url_for("generate_readme"))
        route = full_route.replace(str(request.base_url), "")
        return RedirectResponse(
            url=f"/{route}?project_id={project_id}", status_code=303
        )
    else:
        return error_modal("Error: update_readme_content failed")


async def update_retrieval_method(session, request: Request):
    print("\n>>>> CTRL: update_retrieval_method")
    form = await request.form()
    session["retrieval_method"] = form.get("retrieval_method")
