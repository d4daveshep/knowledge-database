import os
from os.path import exists

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sql_app import schemas
from sql_app.main import app, get_db_session
from sql_app.models import Base


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

    yield TestClient(app)

    os.remove("./test.db")


def test_node_crud_apis(client):
    # TODO break into separate tests
    pass


def test_create_node_api(client):
    name = "First New Starter"
    response = client.post("/nodes/", json=schemas.NodeCreate(name=name).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name
    assert node.id == 1


def test_read_node_api(client):
    name = "First New Starter"
    response = client.post("/nodes/", json=schemas.NodeCreate(name=name).dict())
    node = schemas.Node(**response.json())

    response = client.get(f"/nodes/{node.id}")
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name
    assert node.id == 1


def test_read_all_nodes_api(client):
    name_1 = "First New Starter"
    client.post("/nodes/", json=schemas.NodeCreate(name=name_1).dict())
    name_2 = "Second New Starter"
    client.post("/nodes/", json=schemas.NodeCreate(name=name_2).dict())

    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 2
    node_1 = schemas.Node(**nodes_json[0])
    node_2 = schemas.Node(**nodes_json[1])
    assert node_1.name == name_1
    assert node_2.name == name_2


def test_read_node_by_name_api(client):
    name_2 = "Second New Starter"
    client.post("/nodes/", json=schemas.NodeCreate(name=name_2).dict())

    response = client.get("/nodes/?like=Second")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_2 = schemas.Node(**nodes_json[0])
    assert node_2.name == name_2


def test_update_node_api(client):
    name_2 = "Second New Starter"
    client.post("/nodes/", json=schemas.NodeCreate(name=name_2).dict())
    name_3 = "Third New Starter"

    response = client.put("/nodes/1", json=schemas.NodeCreate(name=name_3).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name_3
    assert node.id == 1


def test_delete_node_api(client):
    name_2 = "Second New Starter"
    client.post("/nodes/", json=schemas.NodeCreate(name=name_2).dict())
    # DELETE
    response = client.delete("/nodes/1")
    assert response.status_code == 200, response.text

    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_2 = schemas.Node(**nodes_json[0])
    assert node_2.name == name_2


def test_create_connection_api_with_new_nodes(client):
    subject = "Andrew"
    conn_name = "is a "
    target = "Chief Engineer"

    cc = schemas.ConnectionCreate(
        name=conn_name,
        subject=schemas.NodeCreate(name=subject),
        target=schemas.NodeCreate(name=target)
    )
    response = client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == conn_name
    assert conn.id == 1
    assert conn.subject.name == subject
    assert conn.target.name == target


def test_create_connection_api_with_existing_nodes(client):
    response = client.post("/nodes/", json=schemas.NodeCreate(name="Andrew").dict())
    subject = schemas.Node(**response.json())
    response = client.post("/nodes/", json=schemas.NodeCreate(name="Chief Engineer").dict())
    target = schemas.Node(**response.json())

    cc = schemas.ConnectionCreate(
        name="has title",
        subject=subject.id,
        target=target.id
    )
    response = client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == "has title"
    assert conn.id == 1
    assert conn.subject.name == subject.name
    assert conn.target.name == target.name


def test_create_connection_api_with_nonexistent_nodes(client):
    cc = schemas.ConnectionCreate(name="bad connection", subject=98, target=99)
    # with pytest.raises(HTTPException) as exec:
    response = client.post("/connections/", json=cc.dict())
    assert response.status_code == 404
