from sqlite3 import Cursor

from sqlalchemy import Connection
from sqlalchemy.orm import Session

from utilities.create_test_database import insert_data


def load_test_data(db_session: Session) -> None:
    db_connection: Connection = db_session.connection()

    cursor: Cursor = db_connection.connection.cursor()

    insert_data(cursor)



