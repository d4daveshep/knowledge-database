import pytest

from web_apps import models, crud
from web_apps.crud import ConnectionNodeNotFoundError
from web_apps.schemas import NodeCreate, ConnectionCreate


def test_create_connection_and_nodes(db_session):
    conn = crud.create_connection(
        db_session, ConnectionCreate(
            name="has title",
            subject=NodeCreate(name="David"),
            target=NodeCreate(name="General Manager")
        )
    )

    assert conn.name == "has title"
    assert conn.subject.name == "David"
    assert conn.target.name == "General Manager"


def test_create_connection_to_existing_nodes(db_session):
    new_conn = crud.create_connection(
        db_session, ConnectionCreate(
            name="wants to learn",
            subject=3,  # Cindy
            target=25  # SpringBoot
        )
    )

    assert new_conn.name == "wants to learn"
    assert new_conn.subject.name == "Cindy"
    assert new_conn.target.name == "SpringBoot"


def test_create_connection_to_nonexistent_node_ids(db_session):
    with pytest.raises(ConnectionNodeNotFoundError) as error:
        crud.create_connection(
            db_session, ConnectionCreate(
                name="bad connection",
                subject=98,
                target=99
            )
        )


def test_delete_connection(db_session):
    orig_count = crud.get_table_size(db_session, models.Connection)

    rows_deleted = crud.delete_connection(db_session, 1)
    assert rows_deleted == 1

    new_count = crud.get_table_size(db_session, models.Connection)
    assert new_count == orig_count - 1


def test_delete_nonexistent_connection(db_session):
    orig_count = crud.get_table_size(db_session, models.Connection)
    crud.delete_connection(db_session, 99)

    new_count = crud.get_table_size(db_session, models.Connection)
    assert new_count == orig_count


def test_delete_node_deletes_connections_to_node(db_session):
    original_node_count = crud.get_table_size(db_session, models.Node)
    original_connection_count = crud.get_table_size(db_session, models.Connection)

    # find and delete Andrew
    andrew = crud.get_nodes_like_name(db_session, "andrew")[0]
    crud.delete_node(db_session, andrew.id)

    # verify only 1 node deleted
    new_node_count = crud.get_table_size(db_session, models.Node)
    assert new_node_count == original_node_count - 1

    # verify 6 connections deleted
    new_connection_count = crud.get_table_size(db_session, models.Connection)
    assert new_connection_count == original_connection_count - 6


def test_get_connections_to_node_id(db_session):
    andrew = crud.get_nodes_like_name(db_session, "Andrew")[0]

    connections = crud.get_connections_to_node(db_session, andrew.id)
    assert len(connections) == 6


def test_get_connections_to_node_name_like(db_session):
    nodes_like = crud.get_nodes_like_name(db_session, "engineer")
    assert len(nodes_like) == 2

    connections_to_nodes_like = crud.get_connections_to_node_like_name(db_session, "engineer")

    assert len(connections_to_nodes_like) == 2
    connection_3 = crud.get_connection(db_session, 3)
    assert connection_3 in connections_to_nodes_like


def test_get_connection_by_id(db_session):
    andrew_appt = crud.get_connection(db_session, 1)
    assert andrew_appt.id == 1


def test_update_connection(db_session):
    connection = crud.update_connection(
        db_session, connection_id=1,
        updated_connection=ConnectionCreate(
            name="is a",
            subject=NodeCreate(name="Ryan"),
            target=NodeCreate(name="Nice Guy")
        )
    )
    assert connection.id == 1
    assert connection.name == "is a"
    assert connection.subject.name == "Ryan"
    assert connection.target.name == "Nice Guy"


def test_cant_create_duplicate_connection(db_session):
    crud.create_connection(
        db_session,
        ConnectionCreate(name="is a unique", subject=NodeCreate(name="David"), target=NodeCreate(name="Human Being"))
    )

    original_node_count = crud.get_table_size(db_session, models.Node)
    original_connection_count = crud.get_table_size(db_session, models.Connection)

    crud.create_connection(
        db_session,
        ConnectionCreate(name="is a unique", subject=NodeCreate(name="David"), target=NodeCreate(name="Human Being"))
    )

    new_node_count = crud.get_table_size(db_session, models.Node)
    new_connection_count = crud.get_table_size(db_session, models.Connection)

    assert new_node_count == original_node_count
    assert original_connection_count == new_connection_count


def test_get_connection_by_name_and_node_ids(db_session):
    node_1 = crud.get_node(db_session, 1)
    node_2 = crud.get_node(db_session, 2)
    new_connection_name = "is friends with"
    new_connection = crud.create_connection(
        db_session,
        ConnectionCreate(name=new_connection_name, subject=node_1.id, target=node_2.id)
    )

    got_connection = crud.get_connection_by_name_target_id_and_subject_id(db_session,
                                                                          name=new_connection_name,
                                                                          subject_id=node_1.id,
                                                                          target_id=node_2.id)

    assert new_connection.id == got_connection.id


def test_delete_all_connections(db_session):
    original_connection_count = crud.get_table_size(db_session, models.Connection)
    assert original_connection_count > 0

    crud.delete_connections(db_session)

    new_connection_count = crud.get_table_size(db_session, models.Connection)
    assert new_connection_count == 0


def test_get_connection_names(db_session):
    connection_names = crud.get_connection_names(db_session, like="e")
    assert len(connection_names) == 3
    assert connection_names["has title"] == 3
    assert connection_names["has experience in"] == 7
    assert connection_names["worked at"] == 7
