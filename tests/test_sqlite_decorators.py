from sqlite_decorators import __version__
from sqlite_decorators import create_table

def test_version():
    assert __version__ == '0.1.0'


def test_create_table(test_db):
    @create_table(test_db.cursor, test_db.connection)
    def table_template():
        return {
            "name": "Table1",
            "column1": "TEXT",
            "column2": "INT"
            }
    example_dict = table_template()
    # Make sure the decorator still returns the normal function output.
    assert example_dict == {
            "name": "Table1",
            "column1": "TEXT",
            "column2": "INT"
            }
    tables = test_db.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';""").fetchone()
    assert len(tables) == 1
    assert tables[0] == "Table1"