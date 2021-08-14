from sqlite_decorators import __version__
from sqlite_decorators import create_table

def test_version():
    assert __version__ == '0.1.0'


def test_create_table(test_db):
    @create_table(test_db.cursor, test_db.connection)
    def output_string():
        return "Table1"
    example_str = output_string()
    assert example_str == "Table1"
    tables = test_db.cursor.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';""").fetchone()
    assert len(tables) == 1
    assert tables[0] == "Table1"