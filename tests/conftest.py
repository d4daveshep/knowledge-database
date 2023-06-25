import os.path
import sqlite3
import tempfile
from sqlite3 import Connection, Cursor

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient

from utilities.create_test_database import create_tables, insert_data
from web_apps.json_rest_app import get_db_session, app
from web_apps.models import Base


@pytest.fixture(scope="module")
def temp_dir() -> str:
    tmp_dir: str = tempfile.mkdtemp(dir="/tmp")
    # print(tmp_dir)
    yield tmp_dir

    # tear down
    os.rmdir(tmp_dir)


@pytest.fixture(scope="function")
def db_connection(temp_dir: str) -> Connection:
    # set up
    db_filename = temp_dir + "/test.db"
    print(f"\ndb_file={db_filename}")
    db_conn: Connection = sqlite3.connect(db_filename)
    yield db_conn

    # tear down
    db_conn.close()
    if os.path.isfile(db_filename):
        os.remove(db_filename)


@pytest.fixture(scope="function")
def db_cursor(db_connection: Connection) -> Cursor:
    cursor: Cursor = db_connection.cursor()
    create_tables(cursor)
    yield cursor

    # tear down
    cursor.close()


@pytest.fixture(scope="function")
def db_populated_filename(db_cursor: Cursor) -> str:
    insert_data(db_cursor)

    db_cursor.execute("PRAGMA database_list")
    rows = db_cursor.fetchone()
    db_filename = rows[2]

    yield db_filename

    # tear down
    pass


@pytest.fixture()
def db_session(db_populated_filename: str) -> Session:
    engine = create_engine("sqlite:///" + db_populated_filename, echo=False)

    base = automap_base()
    base.prepare(autoload_with=engine)

    # engine = create_engine("sqlite://", echo=True)
    # models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


@pytest.fixture()
def json_app_client(db_populated_filename: str) -> TestClient:
    sqlalchemy_database_url = "sqlite:///" + db_populated_filename

    engine = create_engine(
        sqlalchemy_database_url, connect_args={"check_same_thread": False}
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = testing_session_local()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db_session] = override_get_db

    client = TestClient(app)

    yield client
