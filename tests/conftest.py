import sqlite3, os
import pytest
from collections import namedtuple

@pytest.fixture
def test_db():
    conn = sqlite3.connect('test.db')
    cur = conn.cursor()
    TestDB = namedtuple('TestDB', ['connection', 'cursor'])
    test_db = TestDB(conn, cur)
    yield test_db
    test_db.connection.close()
    os.remove('test.db')

