import uuid
import json
from app.utils.initialize_db import db, StepResults


def initialize_db(
    session_id: str,
    project_id: str,
    answer: str,
    feedback_question: str,
    retrieved_chunks: list,
    directory_tree_dict: dict,
):
    print(f"DB: initialize_db")
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

        for chunk in retrieved_chunks:
            db.t.retrieved_chunks.insert(
                id=str(uuid.uuid4()),
                step_id=step_id,
                content=chunk,
            )

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


def insert_step_db(
    step, project_id, feedback_question, answer, retrieved_chunks, directory_tree_str
):
    print(f"DB: insert_step_db")
    try:
        # check if row exists with project_id and step
        step_data = next(
            db.t.steps.rows_where("step = ? AND readme_id= ?", [step, project_id]), None
        )
        if step_data:
            print("Step already exists. Updating the step...")
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
            for chunk in retrieved_chunks:
                db.t.retrieved_chunks.insert(
                    id=str(uuid.uuid4()),
                    step_id=step_data["id"],
                    content=chunk,
                )
            print("Step updated successfully")
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
            for chunk in retrieved_chunks:
                db.t.retrieved_chunks.insert(
                    id=str(uuid.uuid4()),
                    step_id=step_id,
                    content=chunk,
                )
        return True
    except Exception as e:
        print(f"Error: {e}")
        raise e


def update_readme_content(project_id: str, content: str):
    print(f"DB: update_readme_content")
    try:
        db.t.readmes.update(pk_values=project_id, updates={"content": content})
        return True
    except Exception as e:
        print(f"Error: {e}")
        raise e


def insert_step_results(project_id: str, results_json: str) -> bool:
    print(f"DB: insert_step_results")
    try:
        step_result = StepResults(
            id=str(uuid.uuid4()), readme_id=project_id, content=results_json
        )
        db.t.step_results.insert(step_result)
        return True
    except Exception as e:
        print(f"Error inserting step results: {e}")
        return False
