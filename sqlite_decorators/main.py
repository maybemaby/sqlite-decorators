import sqlite3, functools
from collections import namedtuple


def column_strings(table_dict: dict) -> str:
    """Helper function to take the dictionary for create_table and
    make the string for SQL execution.
    """
    column_dict = table_dict.copy()
    column_dict.pop("name")
    output_list = []
    for name, col_type in column_dict.items():
        output_list.append(f"{name} {col_type}")
    return ", ".join(output_list)


def create_table(assigned_cursor: sqlite3.Cursor, db_connection: sqlite3.Connection):
    """Decorator that takes a sqlite3 Cursor object and sqlite3 Connection and
    creates a table from a dictionary returning from an attached function.

    Dictionary takes the form:
    {
        "name": "table_name",
        "column1_name": "column1_type",
        "column2_name": "column2_type"
    }

    :param assigned_cursor: [description]
    :type assigned_cursor: sqlite3.Cursor
    :param db_connection: [description]
    :type db_connection: sqlite3.Connection
    """

    def decorator_create_table(func):
        @functools.wraps(func)
        def wrapper_create_table(*args, **kwargs):
            table_data = func(*args, **kwargs)
            assigned_cursor.execute(
                f'CREATE TABLE {table_data["name"]} ({column_strings(table_data)})'
            )
            db_connection.commit()
            return table_data

        return wrapper_create_table

    return decorator_create_table


Row = namedtuple("Row", ["col_names", "values"])


def dict_into_row(insert_dict: dict):
    if not isinstance(insert_dict, dict):
        raise TypeError("Expected dict type object")
    columns = tuple([str(key) for key in insert_dict.keys()])
    col_values = tuple(insert_dict.values())
    return Row(", ".join(columns), col_values)


def insert_row(
    assigned_cursor: sqlite3.Cursor, db_connection: sqlite3.Connection, table_name: str
):
    def decorator_insert_row(func):
        @functools.wraps(func)
        def wrapper_insert_row(*args, **kwargs):
            func_map = {dict: dict_into_row}
            provided_data = func(*args, **kwargs)
            # Calls a function depending on the internal func return type
            row = func_map[type(provided_data)](provided_data)
            assigned_cursor.execute(
                f"""INSERT INTO {table_name}
                ({row.col_names})
                VALUES ({("?, " * len(row.values)).rstrip(", ")});
            """,
                row.values,
            )
            db_connection.commit()
            return provided_data

        return wrapper_insert_row

    return decorator_insert_row
