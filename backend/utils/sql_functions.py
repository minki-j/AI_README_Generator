import json
import logging
from include.schemas.github_user_schema import GITHUB_USER_SCHEMA, GITHUB_REPO_SCHEMA


def convert_to_sql_data_type(val_type):
    if issubclass(val_type, bool):
        return "BOOLEAN"
    elif issubclass(val_type, int):
        return "INTEGER"
    elif issubclass(val_type, float):
        return "FLOAT"
    else:
        return "TEXT"


def get_existing_columns(cursor, table_name):
    query = f"""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = '{table_name}';
    """
    cursor.execute(query)
    columns = cursor.fetchall()
    # example return: [('login',), ('id',)]
    return [column[0] for column in columns]


def add_new_columns(cursor, table_name: str, example: dict):
    for column, type in example.items():
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {type}")
            logging.info(
                f"Added new column '{column}' with type '{type}' to table '{table_name}'."
            )
        except Exception as e:
            logging.error(f"Error adding column '{column}': {e}")


def create_or_update_table(cursor, data: list[dict], table_name: str):

    if not data or len(data) == 0:
        logging.warning("data is empty. No table created or updated.")
        return

    # create column definitions with data types
    column_definitions = ", ".join(
        [
            f"{column} {convert_to_sql_data_type(type(value))}"
            for column, value in data[0].items()
        ]
    )

    # if id exist in the data, set it as primary key
    # otherwise, set the first column as primary key
    primary_key = "id" if "id" in data[0].keys() else data[0].keys()[0]

    match table_name:
        case "github_accounts":
            foreign_key_statement = ""
        case "github_repositories":
            foreign_key_statement = (
                ", FOREIGN KEY (user_id) REFERENCES github_accounts(id)"
            )
        case "github_commits":
            foreign_key_statement = (
                ", FOREIGN KEY (repository_id) REFERENCES github_repositories(id)"
            )
        case _:
            foreign_key_statement = ""

    # Deprecated version
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions}, PRIMARY KEY ({primary_key}));"

    # TODO: This query needed to be tested!
    #     create_table_query = f"""
    # CREATE TABLE IF NOT EXISTS {table_name} (
    #     {column_definitions},
    #     PRIMARY KEY ({primary_key})
    #     {foreign_key_statement}
    # );
    # """

    try:
        print(create_table_query)
        cursor.execute(create_table_query)
        logging.info(f"Table '{table_name}' created or already exists.")
    except Exception as e:
        raise Exception(
            f"Failed to create table '{table_name}'. Query: {create_table_query}"
        ) from e

    # Check for new columns and add them
    existing_columns = get_existing_columns(cursor, table_name)
    new_columns = {
        column: convert_to_sql_data_type(type(value))
        for column, value in data[0].items()
        if column not in existing_columns
    }

    if new_columns:
        add_new_columns(cursor, table_name, new_columns)
    else:
        logging.info("No new columns to add.")


def insert_data(cursor, data: list[dict], table_name, primary_key="id"):
    if not data or len(data) == 0:
        logging.warning("data is empty. No data inserted.")
        return

    for i, element in enumerate(data):

        if not isinstance(element, dict):
            logging.error("not dictionary element at ", i, ", ", element)
            continue
        columns = element.keys()
        values = [element[column] for column in columns]

        # convert to json is value is a dictionary
        values = [
            json.dumps(value) if isinstance(value, dict) else value for value in values
        ]

        placeholders = ", ".join(["%s"] * len(values))
        update_str = ", ".join(
            [f"{col} = EXCLUDED.{col}" for col in columns if col != primary_key]
        )

        insert_query = f"""
        INSERT INTO {table_name} ({', '.join(columns)}) 
        VALUES ({placeholders})
        ON CONFLICT ({primary_key}) 
        DO UPDATE SET {update_str};"""

        try:
            cursor.execute(insert_query, values)
        except Exception as e:
            logging.error(f"on inserting data: {e}")
            logging.error(f"↳ values: {values}")
            logging.error(f"↳ query: {insert_query}")
            return


def select_data_with_condition(
    cursor, table_name: str, select_condition, where_condition: str, limit: int = None
):
    query = f"SELECT {select_condition} FROM {table_name} {'WHERE ' + where_condition if where_condition else ''} {'LIMIT ' + str(limit) if limit else ''};"

    try:
        cursor.execute(query)
    except Exception as e:
        print(f"Failed to execute query: {query}\n Error: {e}")
        return None
    return cursor.fetchall()


def update_table_single_row(cursor, table_name: str, condition: str, update: dict):
    existing_cols = get_existing_columns(cursor, table_name)
    for key in update.keys():
        if key not in existing_cols:
            new_column = {key: convert_to_sql_data_type(GITHUB_USER_SCHEMA[key])}
            add_new_columns(
                cursor,
                table_name,
                new_column,
            )

    update_str = ", ".join([f"{key} = {value}" for key, value in update.items()])
    query = f"""
        UPDATE {table_name} 
        SET {update_str} 
        WHERE {condition};
        """

    try:
        cursor.execute(query)
    except Exception as e:
        print(f"Failed to execute query: {query}")
        return None

    return cursor.fetchall()


def does_table_exists(cursor, table_name):
    query = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = %s
    );
    """
    cursor.execute(query, (table_name,))
    return cursor.fetchone()[0]


def update_table_multiple_rows(
    cursor,
    table_name: str,
    existing_columns: list[str],
    data: list[dict],
    identifier: str,
):
    print(f"==>> update_table_multiple_rows: total {len(data)}")

    if table_name not in ["github_accounts", "github_repositories"]:
        logging.error(f"Table name '{table_name}' not supported.")
        return

    # Extract the columns to be updated
    if not data or len(data) == 0:
        logging.warning("data is empty. No table created or updated.")
        return

    columns = [key for key in data[0].keys() if key != identifier]

    new_columns = [column for column in columns if column not in existing_columns]

    example_new_columns = {}

    for column in new_columns:
        example_new_columns[column] = convert_to_sql_data_type(
            GITHUB_USER_SCHEMA[column]
            if table_name == "github_accounts"
            else (
                GITHUB_REPO_SCHEMA[column]
                if table_name == "github_repositories"
                else str
            )
        )

    if not does_table_exists(cursor, table_name):
        create_or_update_table(cursor, data, table_name)
    else:
        add_new_columns(cursor, table_name, example_new_columns)

    # Start building the SQL query
    sql_set_clauses = []
    parameters = []  # List to hold parameters for the query
    for column in columns:
        case_statements = []
        for row in data:
            if column in row:
                parameters.append(row[identifier])
                if row[column] is not None:
                    parameters.append(row[column])
                    case_statements.append(f"WHEN {identifier} = %s THEN %s")
                else:
                    case_statements.append(f"WHEN {identifier} = %s THEN NULL")
        case_statements.append(f"ELSE {column}")
        case_clause = f"{column} = CASE \n" + "\n".join(case_statements) + "\nEND"
        sql_set_clauses.append(case_clause)
    sql_set_clauses_str = ", \n".join(sql_set_clauses)

    # Handling identifiers for the IN clause
    ids_placeholders = ", ".join(["%s"] * len(data))
    parameters.extend([row[identifier] for row in data])

    query = f"""
UPDATE {table_name}
SET {sql_set_clauses_str}
WHERE {identifier} IN ({ids_placeholders})
    """
    cursor.execute(query, parameters)
    try:
        cursor.execute(query, parameters)
    except Exception as e:
        print(f"Failed to execute query")
        print("Error Message:", e)
        print("parameters: ", parameters)
        return None

    return


def create_document_table_with_repo_id_as_fk(cursor, table_name: str):

    query = f"""
CREATE TABLE IF NOT EXISTS {table_name} (
    id SERIAL PRIMARY KEY,
    repo_id INT,
    data JSONB,
    FOREIGN KEY (repo_id) REFERENCES github_repositories(id) ON DELETE CASCADE
);
"""
    try:
        cursor.execute(query)
        logging.info(f"Table '{table_name}' created or already exists.")
    except Exception as e:
        raise Exception(
            f"Failed to create table '{table_name}'. Query: {query} from {e}"
        )


def insert_document(cursor, table_name: str, repo_id: int, documents: list[dict]):
    for document in documents:
        query = f"""
            INSERT INTO {table_name} (repo_id, data)
            VALUES (%s, %s);
            """
        try:
            cursor.execute(
                query,
                (
                    repo_id,
                    json.dumps(document),
                ),
            )
        except Exception as e:
            logging.error(f"on inserting document: {e}")
            logging.error(f"↳ values: {document}")
            logging.error(f"↳ query: {query}")
            return
