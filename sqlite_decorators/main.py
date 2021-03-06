import sqlite3, functools
from contextlib import closing
from collections import namedtuple
from typing import NamedTuple
from .dbconfig import TYPE_MAP

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


def create_table(db_connection: sqlite3.Connection):
    """Decorator that takes a sqlite3 Cursor object and sqlite3 Connection and
    creates a table from a dictionary returning from an attached function.

    Dictionary takes the form:
    {
        "name": "table_name",
        "column1_name": "column1_type",
        "column2_name": "column2_type"
    }

    :param db_connection: Connection to desired database
    :type db_connection: sqlite3.Connection
    """

    def decorator_create_table(func):
        @functools.wraps(func)
        def wrapper_create_table(*args, **kwargs):
            with closing(db_connection.cursor()) as assigned_cursor:
                table_data = func(*args, **kwargs)
                assigned_cursor.execute(
                    f'CREATE TABLE IF NOT EXISTS {table_data["name"]} ({column_strings(table_data)})'
                )
                db_connection.commit()
            return table_data

        return wrapper_create_table

    return decorator_create_table


Row = namedtuple("Row", ["col_names", "values"])
Row.__doc__ = """
Formats data so it can be inserted into SQL to create and insert rows.

col_names: String of column names separated by commas

values: tuple of values that can be inserted parametrically into SQL
"""

def dict_into_row(insert_dict: dict) -> NamedTuple:
    """Takes a dict to create a namedtuple with col_names and values attributes.
    Internal function used for formatting in insert_row and insert_all_rows function.

    :param insert_dict: dict with column names as keys assigned to associated values
    :type insert_dict: dict
    :raises TypeError: TypeError if dict not used
    :return: namedtuple with attrs col_names as a str and values as a tuple
    :rtype: NamedTuple
    """
    if not isinstance(insert_dict, dict):
        raise TypeError("Expected dict type object")
    columns = tuple([str(key) for key in insert_dict.keys()])
    col_values = tuple(insert_dict.values())
    # # check if all the values are iterables
    # if len(filter(lambda x: hasattr(x, '__iter__'), col_values)) == len(col_values):
    #     row_parameters = [[]]
    return Row(", ".join(columns), col_values)


def iter_into_row(iterable_obj) -> NamedTuple:
    if hasattr(iterable_obj, '__iter__'):
        try:
            return dict_into_row(dict(iterable_obj))
        except TypeError as e:
            print(f'Could not turn obj into a row: {e}')
        except ValueError:
            print(f'Obj needs to contain elements of length 2')
    else:
        raise RuntimeError(f'Could not turn provided obj of type {type(iterable_obj)} into a row')

def insert_row(db_connection: sqlite3.Connection, table_name: str):
    """Decorator that takes function outputs and inserts it as a row to the designated table.

    Usage:
    >>> @insert_row(cur, conn, 'table1')
        def process_data(id, name, birthday):
            return {'id': id, 'name': name, 'birthday': birthday}

    Any non-str keys gets converted to their str form if they have one.
    :param db_connection: Connection object to the database
    :type db_connection: sqlite3.Connection
    :param table_name: name of table in database
    :type table_name: str
    """
    def decorator_insert_row(func):
        @functools.wraps(func)
        def wrapper_insert_row(*args, **kwargs):
            with closing(db_connection.cursor()) as assigned_cursor:
                func_map = {
                    dict: dict_into_row,
                    tuple: iter_into_row,
                    list: iter_into_row,
                    set: iter_into_row,
                    frozenset: iter_into_row
                    }
                provided_data = func(*args, **kwargs)
                # Calls a function depending on the internal func return type
                try:
                    row = func_map[type(provided_data)](provided_data)
                except KeyError:
                    raise TypeError(f'Unexpected type: {type(provided_data)}')
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


def insert_all_rows(db_connection: sqlite3.Connection, table_name: str):
    def decorator_insert_rows(func):
        @functools.wraps(func)
        def wrapper_insert_rows(*args, **kwargs):
            with closing(db_connection.cursor()) as assigned_cursor:
                provided_data = func(*args, **kwargs)
                assigned_cursor.executemany(
                    f"""INSERT INTO {table_name}
                    VALUES ({("?, " * len(provided_data[0])).rstrip(", ")});
                    """,
                    provided_data
                )
                db_connection.commit()
            return provided_data
        return wrapper_insert_rows
    return decorator_insert_rows