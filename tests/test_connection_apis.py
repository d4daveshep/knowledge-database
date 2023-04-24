import os
from os.path import exists

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sql_app import schemas
from sql_app.main import app, get_db_session
from sql_app.models import Base

# global test data
andrew_name = "Andrew Anderson"
brian_name = "Brian Brown"
charlie_name = "Charlie Charkson"

chief_eng_name = "Chief Engineer"
mobile_eng_name = "Mobile Engineer"

java_name = "Java"
angular_name = "Angular"
react_name = "React"
android_name = "Android"
spring_boot_name = "SpringBoot"

role_connection_name = "has title"


@pytest.fixture()
def client():
    if exists("./test.db"):
        os.remove("./test.db")

    sqlalchemy_database_url = "sqlite:///./test.db"

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

    client.post("/nodes/", json=schemas.NodeCreate(name=andrew_name).dict())  # id: 1
    client.post("/nodes/", json=schemas.NodeCreate(name=chief_eng_name).dict())  # id: 2
    client.post("/nodes/", json=schemas.NodeCreate(name=brian_name).dict())  # id: 3
    client.post("/nodes/", json=schemas.NodeCreate(name=mobile_eng_name).dict())  # id: 4

    client.post("/connections/", json=schemas.ConnectionCreate(
        name=role_connection_name, subject=1, target=2).dict())  # id: 1
    client.post("/connections/", json=schemas.ConnectionCreate(
        name=role_connection_name, subject=3, target=4).dict())  # id: 2

    yield client

    os.remove("./test.db")


def test_create_connection_api_with_new_nodes(client):
    subject_name = "Wayne Wallace"
    conn_name = "is a"
    target_name = "Test Engineer"

    cc = schemas.ConnectionCreate(
        name=conn_name,
        subject=schemas.NodeCreate(name=subject_name),
        target=schemas.NodeCreate(name=target_name)
    )
    response = client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == conn_name
    assert conn.id == 3  # client fixture creates 2 connections
    assert conn.subject.name == subject_name
    assert conn.target.name == target_name


def test_create_connection_api_with_existing_nodes(client):
    andrew = schemas.Node(**client.get("/nodes/1").json())
    chief_eng = schemas.Node(**client.get("/nodes/2").json())

    cc = schemas.ConnectionCreate(
        name="has title",
        subject=andrew.id,
        target=chief_eng.id
    )
    response = client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == "has title"
    assert conn.id == 3  # client fixture creates 2 connections
    assert conn.subject.name == andrew_name
    assert conn.target.name == chief_eng_name


def test_create_connection_api_with_nonexistent_nodes(client):
    cc = schemas.ConnectionCreate(name="bad connection", subject=98, target=99)
    response = client.post("/connections/", json=cc.dict())
    assert response.status_code == 404


def test_read_connections_by_name(client):
    response = client.get("/connections/?like=title")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 2
    conn_1 = schemas.Node(**nodes_json[0])
    conn_2 = schemas.Node(**nodes_json[1])
    assert conn_1.name == conn_2.name == role_connection_name


# def test_update_connection(client):
#     assert False

def test_delete_connection(client):
    response = client.get("/connections/")
    assert len(response.json()) == 2

    response = client.delete("/connections/2")
    assert response.status_code == 200
    assert response.text == '"deleted, id=2"'

    response = client.get("/connections/")
    assert len(response.json()) == 1

def test_get_connection_by_id(client):
    response = client.get("connections/1")
    assert response.status_code == 200, response.text
    role_connection_json = response.json()
    assert role_connection_json["id"] == 1
    assert role_connection_json["name"] == role_connection_name

def test_put_new_connection(client):
    response = client.get("/connections/3")
    assert response.status_code == 404
    response = client.put("/connections/3", json=schemas.ConnectionCreate(
        name="wants to be", subject=3, target=2).dict())  # id 3 = brian wants to be chief engineer
    assert response.status_code == 201  # created

