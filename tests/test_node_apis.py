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
name_1 = "Andrew Anderson"
name_2 = "Brian Brown"
name_3 = "Charlie Charkson"


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

    client.post("/nodes/", json=schemas.NodeCreate(name=name_1).dict())
    client.post("/nodes/", json=schemas.NodeCreate(name=name_2).dict())
    client.post("/nodes/", json=schemas.NodeCreate(name=name_3).dict())

    yield client

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
    assert node.id == 4


def test_read_node_api(client):
    response = client.get(f"/nodes/2")
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name_2
    assert node.id == 2


def test_read_all_nodes_api(client):
    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 3
    node_1 = schemas.Node(**nodes_json[0])
    node_2 = schemas.Node(**nodes_json[1])
    node_3 = schemas.Node(**nodes_json[2])
    assert node_1.name == name_1
    assert node_2.name == name_2
    assert node_3.name == name_3


def test_read_node_by_name_api(client):
    response = client.get("/nodes/?like=Andrew")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_1 = schemas.Node(**nodes_json[0])
    assert node_1.name == name_1


def test_update_node_api(client):
    full_name = "Charles James Clarkson"
    response = client.put("/nodes/1", json=schemas.NodeCreate(name=full_name).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == full_name
    assert node.id == 1


def test_delete_node_api(client):
    response = client.delete("/nodes/2")
    assert response.status_code == 200, response.text

    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 2
    node_1 = schemas.Node(**nodes_json[0])
    node_3 = schemas.Node(**nodes_json[1])
    assert node_1.name == name_1
    assert node_3.name == name_3
