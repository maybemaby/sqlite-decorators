import sqlite3, os
import pytest
from collections import namedtuple

@pytest.fixture
def test_db():
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    try:
        cur.execute("CREATE TABLE insert_row (id INT, name TEXT, birthday DATE)")
    except sqlite3.OperationalError as e:
        # In case a testdb wasn't teared down properly for any reason
        if 'table insert_row already exists' in str(e):
            conn.close()
            os.remove('test.db')
            conn = sqlite3.connect('test.db')
            cur = conn.cursor()
            cur.execute("CREATE TABLE insert_row (id INT, name TEXT, birthday DATE)")  
    conn.commit()
    TestDB = namedtuple('TestDB', ['connection', 'cursor'])
    test_db = TestDB(conn, cur)
    yield test_db
    test_db.connection.close()
    os.remove('test.db')

