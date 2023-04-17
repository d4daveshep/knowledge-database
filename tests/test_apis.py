import os
from os.path import exists

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sql_app import schemas
from sql_app.main import app, get_db_session
from sql_app.models import Base

if exists("./test.db"):
    os.remove("./test.db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)


def test_node_crud_APIs():
    # CREATE
    name_1 = "First New Starter"
    response = client.post("/nodes/", json=schemas.NodeCreate(name=name_1).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name_1
    assert node.id == 1

    # READ BY ID
    response = client.get(f"/nodes/{node.id}")
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name_1
    assert node.id == 1

    # READ ALL
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

    # READ BY NAME LIKE
    response = client.get("/nodes/?like=Second")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_2 = schemas.Node(**nodes_json[0])
    assert node_2.name == name_2

    # UPDATE
    name_3 = "Third New Starter"
    response = client.put("/nodes/2", json=schemas.NodeCreate(name=name_3).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name_3
    assert node.id == 2

    # DELETE
    response = client.delete("/nodes/1")
    assert response.status_code == 200, response.text

    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_2 = schemas.Node(**nodes_json[0])
    assert node_2.name == name_3


def test_connection_crud_APIs():
    # CREATE WITH NEW NODES
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

    # CREATE WITH EXISTING NODES
    cc = schemas.ConnectionCreate(
        name="has title",
        subject=conn.subject.id,
        target=conn.target.id
    )
    response = client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == "has title"
    assert conn.id == 2
    assert conn.subject.name == subject
    assert conn.target.name == target
