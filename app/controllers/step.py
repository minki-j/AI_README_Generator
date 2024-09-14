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

from app.global_vars import STEP_LIST
from app.global_vars import DEBUG
from app.agents.state_schema import State


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

    form = await request.form()
    if len(form) == 0:  # when "next step" button is clicked
        user_feedback = None
        directory_tree_str = db.t.readmes.get(project_id).directory_tree_str
        directory_tree_dict = json.loads(directory_tree_str)

    else:  # when "apply feedback" button is clicked
        user_feedback = form.get("user_feedback")
        directory_tree_str = form.get("directory_tree_str")
        directory_tree_dict = json.loads(directory_tree_str)
        retrieval_method = form.get("retrieval_method")
        session.setdefault("retrieval_method", "FAISS")
        session["retrieval_method"] = retrieval_method

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
        )
        r = main_graph.invoke(None, config)
        session["quota"] = (session["quota"][0] - 1, session["quota"][1])
        results = r.get("results", {})
        retrieved_chunks = r.get("retrieved_chunks", None)
    except Exception as e:
        raise e

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
        return Step(
            STEP_LIST[step_num - 1]["feedback_question"],
            answer,
            retrieved_chunks,
            project_id,
            step_num + 1,
            len(STEP_LIST),
            directory_tree_str,
            session["retrieval_method"],
            is_last_step=True if step_num == len(STEP_LIST) - 1 else False,
        )
    else:
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )


async def generate_readme(session, project_id: str, request: Request):
    print("\n>>>> CTRL: generate_readme")
    if DEBUG:
        print("DEBUG MODE. SKIP GRAPH")
        r = update_readme_content(project_id, "DEBUG MODE. README GENERATED")
        if r:
            full_route = str(request.url_for("generate_readme"))
            route = full_route.replace(str(request.base_url), "")
            return RedirectResponse(
                url=f"/{route}?project_id={project_id}", status_code=303
            )
        else:
            return Div(
                "Error: Something went wrong. Please try again later.",
                cls="error-message",
            )

    config = {"configurable": {"thread_id": project_id}}
    r = main_graph.update_state(
        config,
        values={
            "current_step": len(STEP_LIST) + 1,
        },
    )
    r = main_graph.invoke(
        None,
        config,
    )
    session["quota"] = (session["quota"][0] - 1, session["quota"][1])
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
        return Div(
            "Error: Something went wrong. Please try again later.",
            cls="error-message",
        )
