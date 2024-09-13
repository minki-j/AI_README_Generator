import os
from fasthtml.common import *

if os.path.exists(f"/vol"):
    os.makedirs("/vol/data/main_database", exist_ok=True)
    db_path = os.path.join("/vol", "data", "main_database", "main.db")
else:
    os.makedirs("./data/main_database", exist_ok=True)
    db_path = os.path.join(".", "data", "main_database", "main.db")

db = database(db_path)

users, steps, retrieved_chunks, readmes, step_results = (
    db.t.users,
    db.t.steps,
    db.t.retrieved_chunks,
    db.t.readmes,
    db.t.step_results,
)

if users not in db.t:
    print("\n==>> Creating users table")
    users.create(
        id=str,
        name=str,
        email=str,
        password=str,
        pk="id",
    )

if readmes not in db.t or steps not in db.t or retrieved_chunks not in db.t:
    print("\n==>> Creating readmes, steps, retrieved_chunks tables")
    readmes.create(
        id=str,
        user_id=str,
        content=str,
        directory_tree_str=str,
        pk="id",
        foreign_keys=(("user_id", "users")),
        if_not_exists=True,
    )
    steps.create(
        id=str,
        readme_id=str,
        step=int,
        feedback_question=str,
        directory_tree_str=str,
        answer=str,
        pk="id",
        foreign_keys=(("readme_id", "readmes")),
        if_not_exists=True,
    )
    retrieved_chunks.create(
        id=str,
        step_id=str,
        content=str,
        pk="id",
        foreign_keys=(("step_id", "steps")),
        if_not_exists=True,
    )

if step_results not in db.t:
    print("\n==>> Creating step_results table")
    step_results.create(
        id=str,
        readme_id=str,
        content=str,  # This will store the JSON format of results variable
        pk="id",
        foreign_keys=(("readme_id", "readmes")),
        if_not_exists=True,
    )

Users, Readmes, Steps, RetrievedChunks, StepResults = (
    users.dataclass(),
    readmes.dataclass(),
    steps.dataclass(),
    retrieved_chunks.dataclass(),
    step_results.dataclass(),
)

try:
    main_db_diagram = diagram(db.tables)    
    main_db_diagram.render("data/main_db_diagram", format="png", cleanup=True)
except:
    print(
        "Error on generating DB visualization. Probably graphviz executables were not found. Please install Graphviz and add it to your system's PATH."
    )
