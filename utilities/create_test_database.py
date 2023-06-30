import os
import sqlite3
from sqlite3 import Cursor


def create_tables(db_cursor: Cursor):
    db_cursor.execute("""
        CREATE TABLE nodes (
            id INTEGER NOT NULL, 
            name VARCHAR NOT NULL, 
            PRIMARY KEY (id)
        )
    """)
    db_cursor.execute("""
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


def insert_data(db_cursor: Cursor):
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


def create_test_database(temp_dir: str) -> str:
    db_filename = temp_dir + "/test.db"

    if os.path.isfile(db_filename):
        os.remove(db_filename)

    with sqlite3.connect(db_filename) as db_connection:
        db_cursor: Cursor = db_connection.cursor()
        create_tables(db_cursor)
        insert_data(db_cursor)
        db_cursor.close()

    return db_filename

