import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from web_apps import schemas
from web_apps.json_rest_app import app, get_db_session
from web_apps.models import Base


@pytest.fixture()
def client(db_populated):

    sqlalchemy_database_url = "sqlite:///" + db_populated

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

    # os.remove("./test.db")


def test_client(client):
    assert client


def test_node_crud_apis(client):
    # TODO break into separate tests
    pass


def test_create_node_api(client):
    name = "First New Starter"
    response = client.post("/nodes/", json=schemas.NodeCreate(name=name).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name
    assert node.id == 35


def test_read_node_api(client):
    response = client.get(f"/nodes/2")
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == "Brian"
    assert node.id == 2


def test_read_all_nodes_api(client):
    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 15
    node_1 = schemas.Node(**nodes_json[0])
    node_2 = schemas.Node(**nodes_json[1])
    node_3 = schemas.Node(**nodes_json[2])
    assert node_1.name == "Andrew"
    assert node_2.name == "Brian"
    assert node_3.name == "Cindy"


def test_read_node_by_name_api(client):
    response = client.get("/nodes/?like=Andrew")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_1 = schemas.Node(**nodes_json[0])
    assert node_1.name == "Andrew"


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
    assert response.text == '"deleted, id=2"'

    response = client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 2
    node_1 = schemas.Node(**nodes_json[0])
    node_3 = schemas.Node(**nodes_json[1])
    assert node_1.name == name_1
    assert node_3.name == name_3
