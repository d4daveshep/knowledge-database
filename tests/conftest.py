import os.path
import sqlite3

import pytest


@pytest.fixture()
def db_connection(tmp_path):
    # set up
    db_filename = tmp_path / "temp.db"
    db_conn = sqlite3.connect(db_filename)
    yield db_conn

    # tear down
    db_conn.close()
    if os.path.isfile(db_filename):
        os.remove(db_filename)


@pytest.fixture()
def db_cursor(db_connection):
    cursor = db_connection.cursor()
    cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER NOT NULL, 
            name VARCHAR NOT NULL, 
            PRIMARY KEY (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE connections (
            id INTEGER NOT NULL, 
            name VARCHAR NOT NULL, 
            subject_id INTEGER NOT NULL, 
            target_id INTEGER NOT NULL, 
            PRIMARY KEY (id), 
            FOREIGN KEY(subject_id) REFERENCES nodes (id), 
            FOREIGN KEY(target_id) REFERENCES nodes (id)
        )
    """)
    yield cursor

    # tear down
    cursor.close()


@pytest.fixture()
def db_populate(db_cursor):
    names = [(1, "Andrew"), (2, "Brian"), (3, "Cindy")]
    roles = [(11, "Chief Engineer"), (12, "Practice Lead")]
    skills = [(21, "Java"), (22, "Angular"), (23, "React"), (24, "Android"), (25, "SpringBoot")]
    customers = [(31, "Warehouse Group"), (32, "Countdown"), (33, "Westpac"), (34, "Global Dairy")]

    """
    Here's how to generate a list of tuples of any length
    id_generator = iter(range(1, 50))
    nodes = [tuple([next(id_generator), node_name]) for node_name in names + roles + skills + customers]
    """

    db_cursor.executemany("INSERT INTO nodes VALUES ( ?, ? )", names + roles + skills + customers)
    db_cursor.connection.commit()

    return db_cursor
