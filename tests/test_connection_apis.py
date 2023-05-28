from web_apps import schemas


def test_client_fixture(json_app_client):
    response = json_app_client.get("/stats/")
    assert response.status_code == 200
    stats = response.json()
    assert stats["node_count"] == 15
    assert stats["connection_count"] == 17


def test_create_connection_api_with_new_nodes(json_app_client):
    subject_name = "Wayne"
    conn_name = "is a"
    target_name = "Test Engineer"

    cc = schemas.ConnectionCreate(
        name=conn_name,
        subject=schemas.NodeCreate(name=subject_name),
        target=schemas.NodeCreate(name=target_name)
    )
    response = json_app_client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == conn_name
    assert conn.id == 28  # client fixture creates 27 connections
    assert conn.subject.name == subject_name
    assert conn.target.name == target_name

    response = json_app_client.get("/stats/")
    assert response.status_code == 200
    stats = response.json()
    assert stats["node_count"] == 17
    assert stats["connection_count"] == 18


def test_create_connection_api_with_existing_nodes(json_app_client):
    andrew = schemas.Node(**json_app_client.get("/nodes/1").json())
    chief_eng = schemas.Node(**json_app_client.get("/nodes/11").json())

    cc = schemas.ConnectionCreate(
        name="still has title",
        subject=andrew.id,
        target=chief_eng.id
    )
    response = json_app_client.post(
        "/connections/",
        json=cc.dict()
    )
    assert response.status_code == 200, response.text
    conn = schemas.Connection(**response.json())
    assert conn.name == "still has title"
    assert conn.id == 28  # client fixture creates 27 connections
    assert conn.subject.name == "Andrew"
    assert conn.target.name == "Chief Engineer"

    response = json_app_client.get("/stats/")
    assert response.status_code == 200
    stats = response.json()
    assert stats["node_count"] == 15
    assert stats["connection_count"] == 18


def test_create_connection_api_with_nonexistent_nodes(json_app_client):
    cc = schemas.ConnectionCreate(name="bad connection", subject=98, target=99)
    response = json_app_client.post("/connections/", json=cc.dict())
    assert response.status_code == 404


def test_get_connections_by_name(json_app_client):
    response = json_app_client.get("/connections/?name_like=title")
    assert response.status_code == 200, response.text
    connections_json = response.json()
    assert len(connections_json) == 3
    conn_1 = schemas.Connection(**connections_json[0])
    conn_2 = schemas.Connection(**connections_json[1])
    assert conn_1.name == conn_2.name == "has title"


def test_get_connections_by_node_id(json_app_client):
    response = json_app_client.get("/connections/?node_id=1")
    assert response.status_code == 200, response.text
    connections_json = response.json()
    assert len(connections_json) == 6
    conn_1 = schemas.Connection(**connections_json[0])
    assert conn_1.id == 1
    conn_2 = schemas.Connection(**connections_json[1])
    assert conn_2.id == 11


def test_delete_existing_connection(json_app_client):
    response = json_app_client.get("/connections/")
    orig_count = len(response.json())

    response = json_app_client.delete("/connections/2")
    assert response.status_code == 200

    response = json_app_client.get("/connections/")
    assert len(response.json()) == orig_count - 1


def test_delete_nonexistent_connection(json_app_client):
    response = json_app_client.get("/connections/")
    orig_count = len(response.json())

    response = json_app_client.delete("/connections/99")
    assert response.status_code == 404

    response = json_app_client.get("/connections/")
    assert len(response.json()) == orig_count


def test_get_connection_by_id(json_app_client):
    response = json_app_client.get("connections/1")
    assert response.status_code == 200, response.text
    role_connection_json = response.json()
    assert role_connection_json["id"] == 1
    assert role_connection_json["name"] == "has title"


def test_put_new_connection(json_app_client):
    response = json_app_client.get("/connections/50")
    assert response.status_code == 404
    response = json_app_client.put("/connections/50", json=schemas.ConnectionCreate(
        name="wants to be", subject=3, target=11).dict())  # Brian wants to be Chief Engineer
    assert response.status_code == 201  # created


def test_put_existing_connection(json_app_client):
    response = json_app_client.get("/connections/1")
    assert response.status_code == 200

    response = json_app_client.put("/connections/1", json=schemas.ConnectionCreate(
        name="wants to be", subject=3, target=2).dict())  # id 1 = Brian wants to be Chief Engineer
    assert response.status_code == 200

    response = json_app_client.get("/connections/1")
    connection = schemas.Connection.parse_raw(response.text)
    assert connection.id == 1
    assert connection.name == "wants to be"
    assert connection.subject.id == 3
    assert connection.target.id == 2


def test_stats_api(json_app_client):
    response = json_app_client.get("/stats/")
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["node_count"] == 15
    assert response_json["connection_count"] == 17
