from web_apps import schemas


def test_client(json_app_client):
    assert json_app_client


def test_create_node_api(json_app_client):
    name = "First New Starter"
    response = json_app_client.post("/nodes/", json=schemas.NodeCreate(name=name).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name
    assert node.id == 35


def test_read_node_api(json_app_client):
    response = json_app_client.get(f"/nodes/2")
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == "Brian"
    assert node.id == 2


def test_read_all_nodes_api(json_app_client):
    response = json_app_client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 15
    node_1 = schemas.Node(**nodes_json[0])
    node_2 = schemas.Node(**nodes_json[1])
    node_3 = schemas.Node(**nodes_json[2])
    assert node_1.name == "Andrew"
    assert node_2.name == "Brian"
    assert node_3.name == "Cindy"


def test_read_node_by_name_api(json_app_client):
    response = json_app_client.get("/nodes/?like=Andrew")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 1
    node_1 = schemas.Node(**nodes_json[0])
    assert node_1.name == "Andrew"


def test_update_node_api(json_app_client):
    full_name = "Charles James Clarkson"
    response = json_app_client.put("/nodes/1", json=schemas.NodeCreate(name=full_name).dict())
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == full_name
    assert node.id == 1


def test_delete_node_api(json_app_client):
    response = json_app_client.delete("/nodes/2")
    assert response.status_code == 200, response.text
    assert response.text == '"deleted, id=2"'

    response = json_app_client.get("/nodes/")
    assert response.status_code == 200, response.text
    nodes_json = response.json()
    assert len(nodes_json) == 14
    node_1 = schemas.Node(**nodes_json[0])
    node_3 = schemas.Node(**nodes_json[1])
    assert node_1.name == "Andrew"
    assert node_3.name == "Cindy"
