import os.path
import sqlite3
import tempfile

import pytest


@pytest.fixture(scope="module")
def temp_dir():
    tmp_dir = tempfile.mkdtemp(dir="/tmp")
    # print(tmp_dir)
    yield tmp_dir

    # tear down
    os.rmdir(tmp_dir)



@pytest.fixture(scope="function")
def db_connection(temp_dir):
    # set up
    db_filename = temp_dir + "/test.db"
    print(f"\ndb_file={db_filename}")
    db_conn = sqlite3.connect(db_filename)
    yield db_conn

    # tear down
    db_conn.close()
    if os.path.isfile(db_filename):
        os.remove(db_filename)


@pytest.fixture(scope="function")
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


@pytest.fixture(scope="function")
def db_populated(db_cursor):
    names = [
        (1, "Andrew"),
        (2, "Brian"),
        (3, "Cindy")
    ]
    titles = [
        (11, "Chief Engineer"),
        (12, "Practice Lead"),
        (13, "Senior Engineer")
    ]
    skills = [
        (21, "Java"),
        (22, "Angular"),
        (23, "React"),
        (24, "Android"),
        (25, "SpringBoot")
    ]
    customers = [
        (31, "Warehouse Group"),
        (32, "Countdown"),
        (33, "Westpac"),
        (34, "Global Dairy")
    ]

    appointment_name = "has title"
    appointments = [
        (1, appointment_name, 1, 11),  # Andrew has title Chief Engineer
        (2, appointment_name, 2, 12),  # Brian has title Practice Lead
        (3, appointment_name, 3, 13),  # Cindy has title Senior Engineer
    ]

    experience_name = "has experience in"
    experiences = [
        (11, experience_name, 1, 21),  # Andrew has experience in Java
        (12, experience_name, 1, 25),  # Andrew has experience in SpringBoot
        (13, experience_name, 1, 23),  # Andrew has experience in Angular
        (14, experience_name, 2, 21),  # Brian has experience in Java
        (15, experience_name, 2, 24),  # Brian has experience in Android
        (16, experience_name, 3, 22),  # Cindy has experience in Angular
        (17, experience_name, 3, 23),  # Cindy has experience in React
    ]

    assignment_name = "worked at"
    assignments = [
        (21, assignment_name, 1, 31),  # Andrew worked at Warehouse Group
        (22, assignment_name, 1, 34),  # Andrew worked at Global Dairy
        (23, assignment_name, 2, 32),  # Brian worked at Countdown
        (24, assignment_name, 2, 33),  # Brian worked at Westpac
        (25, assignment_name, 3, 31),  # Cindy worked at Warehouse Group
        (26, assignment_name, 3, 33),  # Cindy worked at Westpac
        (27, assignment_name, 3, 34),  # Cindy worked at Global Dairy
    ]

    """
    Here's how to generate a list of tuples of any length
    id_generator = iter(range(1, 50))
    nodes = [tuple([next(id_generator), node_name]) for node_name in names + roles + skills + customers]
    """

    db_cursor.executemany("INSERT INTO nodes VALUES ( ?, ? )", names + titles + skills + customers)
    db_cursor.connection.commit()

    db_cursor.executemany("INSERT INTO connections VALUES ( ?, ?, ?, ?)", appointments + experiences + assignments)
    db_cursor.connection.commit()

    db_cursor.execute("PRAGMA database_list")
    rows = db_cursor.fetchone()
    db_filename = rows[2]

    # db_cursor.close()
    # db_cursor.connection.close()
    yield db_filename

    # tear down
    pass

