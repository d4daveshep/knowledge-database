"""
Test the creation of a test database (using common fixtures)
"""
import sqlite3
from os import path

from utilities.create_test_database import create_test_database


def test_create_test_database():
    temp_dir = "."

    db_filename = create_test_database(temp_dir)

    assert path.exists(db_filename)
    assert path.getsize(db_filename) == 12288

    with sqlite3.connect(db_filename) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM nodes")
        node_count, *rest = cursor.fetchone()
        assert node_count == 15

        cursor.execute("SELECT COUNT(*) FROM connections")
        connection_count, *rest = cursor.fetchone()
        assert connection_count == 17
