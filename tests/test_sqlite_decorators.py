import datetime, itertools
import pytest
from sqlite_decorators import __version__
from sqlite_decorators import create_table, dict_into_row, insert_row, insert_all_rows


def test_version():
    assert __version__ == "0.1.0"


def test_create_table(test_db):
    @create_table(test_db.connection)
    def table_template():
        return {"name": "Table1", "column1": "TEXT", "column2": "INT"}

    example_dict = table_template()
    # Make sure the decorator still returns the normal function output.
    assert example_dict == {"name": "Table1", "column1": "TEXT", "column2": "INT"}
    tables = test_db.cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"""
    ).fetchall()
    assert len(tables) == 2
    assert tables[1][0] == "Table1"


def test_create_table_duplicate(test_db):
    # Makes sure the IF NOT EXISTS clause works properly and does not throw error.
    @create_table(test_db.connection)
    def table_template():
        return {"name": "Table1", "column1": "TEXT", "column2": "INT"}
    table_template()
    table_template()
    tables = test_db.cursor.execute(
        """SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"""
    ).fetchall()
    assert len(tables) == 2
    assert tables[1][0] == "Table1"


def test_dict_into_row():
    test_dict = {
        "id": 214123,
        555: "CHeck123",
        "name": "Tim",
        "favorite_food": "Apples",
    }
    row = dict_into_row(test_dict)
    assert row.col_names == "id, 555, name, favorite_food"
    assert row.values == tuple(test_dict.values())


def test_dict_into_row_fail():
    test_str = "Superman"
    test_int = 12345
    test_list = [test_str, test_int]
    with pytest.raises(TypeError) as excinfo:
        dict_into_row(test_str)
    assert "Expected dict type object" in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        dict_into_row(test_int)
    assert "Expected dict type object" in str(excinfo.value)
    with pytest.raises(TypeError) as excinfo:
        dict_into_row(test_list)
    assert "Expected dict type object" in str(excinfo.value)


def test_insert_row(test_db):
    @insert_row(test_db.connection, "insert_row")
    def row_template():
        return {"id": 1234, "name": "Tim", "birthday": datetime.date.today()}

    example_row = row_template()
    assert example_row == {"id": 1234, "name": "Tim", "birthday": datetime.date.today()}
    row = test_db.cursor.execute(
        """SELECT * FROM insert_row
    WHERE id=1234"""
    ).fetchone()
    assert row == (1234, "Tim", str(datetime.date.today()))


def test_insert_row_type_fail(test_db):
    @insert_row(test_db.connection, "insert_row")
    def row_template():
        return "String test"
    with pytest.raises(TypeError) as excinfo:
        row_template()
    assert "Unexpected type: <class 'str'>" in str(excinfo.value)


def test_insert_all_rows(test_db):
    @insert_all_rows(test_db.connection, "insert_row")
    def rows_template(list_or_tuple: str):
        if list_or_tuple == "list":
            return [
                (4521, "Bob", str(datetime.date(2000, 5, 12))),
                (2314, "Steve", str(datetime.date(2000, 5, 12))),
                (131241294, "Tom Hanks", str(datetime.date(2000, 5, 12)))
                ]
        elif list_or_tuple == "tuple":
            return (
                (2020, "Cameron", str(datetime.date(2000, 5, 12))),
                (1520, "Willis", str(datetime.date(2000, 5, 12))),
                (523124224, "Percy", str(datetime.date(2000, 5, 12)))
            )
    ex_list = rows_template("list")
    ex_tuple = rows_template("tuple")
    rows = test_db.cursor.execute("""
        SELECT * FROM insert_row
        WHERE birthday = date('2000-05-12');
    """).fetchall()
    assert rows == list(itertools.chain(tuple(ex_list) + ex_tuple))