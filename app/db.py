import threading
from fasthtml.common import *

db = database("data/main_database/main.db")

users, steps, retrieved_chunks, readmes = (
    db.t.users,
    db.t.steps,
    db.t.retrieved_chunks,
    db.t.readmes,
)

if users not in db.t:
    print("==>> Creating users tables")
    users.create(
        id=str,
        name=str,
        email=str,
        password=str,
        pk="id",
    )

if readmes not in db.t or steps not in db.t or retrieved_chunks not in db.t:
    print("==>> Creating readmes, steps, retrieved_chunks tables")
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

Users, Readmes, Steps, RetrievedChunks = (
    users.dataclass(),
    readmes.dataclass(),
    steps.dataclass(),
    retrieved_chunks.dataclass(),
)
db_lock = threading.Lock()  # Since we're multi-threading here

try:
    main_db_diagram = diagram(db.tables)    
    main_db_diagram.render("data/main_db_diagram", format="png", cleanup=True)
except:
    print(
        "Error on generating DB visualization. Probably graphviz executables were not found. Please install Graphviz and add it to your system's PATH."
    )
