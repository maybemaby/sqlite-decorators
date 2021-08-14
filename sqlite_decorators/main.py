import sqlite3, functools

def create_table(assigned_cursor: sqlite3.Cursor, db_connection: sqlite3.Connection):
    def decorator_create_table(func):
        @functools.wraps(func)
        def wrapper_create_table(*args, **kwargs):
            table_name = func(*args, **kwargs)
            assigned_cursor.execute(f'CREATE TABLE {table_name} (test text)')
            db_connection.commit()
            return table_name
        return wrapper_create_table
    return decorator_create_table