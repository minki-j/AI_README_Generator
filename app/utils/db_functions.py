import uuid
import json
from datetime import datetime

from app.utils.initialize_db import db


def initialize_project(
    session_id: str,
    project_id: str,
    answer: str,
    feedback_question: str,
    retrieved_chunks: list,
    directory_tree_dict: dict,
):
    print(f"\n>>>> DB: initialize_project")
    try:
        directory_tree_str = json.dumps(directory_tree_dict)

        db.t.readmes.insert(
            id=project_id,
            user_id=session_id,  # TODO: Change to user_id once user authentication is implemented
            content="",
            directory_tree_str=directory_tree_str,
        )

        step_id = str(uuid.uuid4())
        db.t.steps.insert(
            id=step_id,
            readme_id=project_id,
            step=1,
            feedback_question=feedback_question,
            answer=answer,
            directory_tree_str=directory_tree_str,
        )

        for path, chunk in retrieved_chunks.items():
            db.t.retrieved_chunks.insert(
                id=str(uuid.uuid4()),
                step_id=step_id,
                path=path,
                content=chunk,
            )

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def insert_step_db(
    step, project_id, feedback_question, answer, retrieved_chunks, directory_tree_str
):
    print(f"\n>>>> DB: insert_step_db")
    try:
        # check if row exists with project_id and step
        step_data = next(
            db.t.steps.rows_where("step = ? AND readme_id= ?", [step, project_id]), None
        )
        if step_data:
            db.t.steps.update(
                pk_values=step_data["id"],
                updates={
                    "feedback_question": feedback_question,
                    "answer": answer,
                    "directory_tree_str": directory_tree_str,
                },
            )
            # delete all retrieved_chunks with the step_id, then insert the new ones
            db.t.retrieved_chunks.delete_where("step_id = ?", [step_data["id"]])
            for path, chunk in retrieved_chunks.items():
                db.t.retrieved_chunks.insert(
                    id=str(uuid.uuid4()),
                    step_id=step_data["id"],
                    path=path,
                    content=chunk,
                )
        else:
            step_id = str(uuid.uuid4())
            db.t.steps.insert(
                id=step_id,
                readme_id=project_id,
                step=step,
                feedback_question=feedback_question,
                answer=answer,
                directory_tree_str=directory_tree_str,
            )
            for path, chunk in retrieved_chunks.items():
                db.t.retrieved_chunks.insert(
                    id=str(uuid.uuid4()),
                    step_id=step_id,
                    path=path,
                    content=chunk,
                )
        return True
    except Exception as e:
        print(f"Error: {e}")
        raise e


def update_readme_content(project_id: str, content: str):
    print(f"\n>>>> DB: update_readme_content")
    try:
        db.t.readmes.update(pk_values=project_id, updates={"content": content})
        return True
    except Exception as e:
        print(f"Error: {e}")
        raise e


def insert_step_results(project_id: str, results_json: str) -> bool:
    print(f"\n>>>> DB: insert_step_results")
    try:
        StepResults = db.t.step_results.dataclass()
        step_result = StepResults(
            id=str(uuid.uuid4()),
            readme_id=project_id,
            content=results_json,
            created_at_utc=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        db.t.step_results.insert(step_result)
        return True
    except Exception as e:
        print(f"Error inserting step results: {e}")
        return False
