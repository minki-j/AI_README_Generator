from app.db import db
import uuid

def initialize_db(session_id:str, project_id:str, answer:str, feedback_question:str, retrieved_chunks: list):
    try:
        db.t.readmes.insert(
            id=project_id,
            user_id=session_id, #TODO: Change to user_id once user authentication is implemented
            content="",
        )

        step_id = str(uuid.uuid4())
        db.t.steps.insert(
            id=step_id,
            readme_id=project_id,
            step=1,
            feedback_question=feedback_question,
            answer=answer,
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


def insert_step_db(step, project_id, feedback_question, answer, retrieved_chunks):
    try:
        step_id = str(uuid.uuid4())
        db.t.steps.insert(
            id=step_id,
            readme_id=project_id,
            step=step,
            feedback_question=feedback_question,
            answer=answer,
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