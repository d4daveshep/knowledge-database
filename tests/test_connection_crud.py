import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sql_app import models, crud
from sql_app.crud import ConnectionNodeNotFoundError
from sql_app.schemas import NodeCreate, ConnectionCreate


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", echo=True)

    models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


@pytest.fixture()
def db_session_with_nodes_and_connections(db_session):
    # people
    andrew = NodeCreate(name="Andrew Lindesay")
    david = NodeCreate(name="David Rawson")
    robin = NodeCreate(name="Robin Southgate")

    # roles
    chief = NodeCreate(name="Chief Engineer")
    fe_pl = NodeCreate(name="Front End Practice Lead")

    # skills
    java = NodeCreate(name="Java")
    angular = NodeCreate(name="Angular")
    react = NodeCreate(name="React")
    android = NodeCreate(name="Android")
    spring_boot = NodeCreate(name="SpringBoot")

    # customers
    twg = NodeCreate(name="The Warehouse Group")
    cdx = NodeCreate(name="CountdownX")
    westpac = NodeCreate(name="Westpac NZ")
    gdt = NodeCreate(name="Global Dairy Trade")

    crud.create_connection(db_session, ConnectionCreate(name="has title", subject=andrew, target=chief))
    crud.create_connection(db_session, ConnectionCreate(name="has experience in", subject=andrew, target=java))
    crud.create_connection(db_session, ConnectionCreate(name="has experience in", subject=andrew, target=spring_boot))
    crud.create_connection(db_session, ConnectionCreate(subject=andrew, name="worked at", target=twg))
    crud.create_connection(db_session, ConnectionCreate(subject=andrew, name="worked at", target=gdt))

    crud.create_connection(db_session, ConnectionCreate(subject=david, name="has title", target=fe_pl))
    crud.create_connection(db_session, ConnectionCreate(subject=david, name="has experience in", target=java))
    crud.create_connection(db_session, ConnectionCreate(subject=david, name="has experience in", target=android))
    crud.create_connection(db_session, ConnectionCreate(subject=david, name="worked at", target=westpac))

    crud.create_connection(db_session, ConnectionCreate(subject=robin, name="has title", target=chief))
    crud.create_connection(db_session, ConnectionCreate(subject=robin, name="has experience in", target=angular))
    crud.create_connection(db_session, ConnectionCreate(subject=robin, name="has experience in", target=react))
    crud.create_connection(db_session, ConnectionCreate(subject=robin, name="worked at", target=cdx))
    crud.create_connection(db_session, ConnectionCreate(subject=robin, name="worked at", target=gdt))

    # assert False  # TODO this stuff doesn't work yet

    # db_session.add_all([andrew_chief, andrew_java, andrew_spring_boot, andrew_twg, andrew_gdt,
    #                     david_lead, david_java, david_android, david_westpac,
    #                     robin_chief, robin_angular, robin_react, robin_cdx, robin_gdt
    #                     ])
    # db_session.commit()

    yield db_session


def test_fixture(db_session_with_nodes_and_connections):
    nodes = crud.get_nodes(db_session_with_nodes_and_connections)
    assert len(nodes) == 14

    connections = crud.get_connections(db_session_with_nodes_and_connections)
    assert len(connections) == 14


def test_create_connection_and_nodes(db_session):
    conn = crud.create_connection(
        db_session, ConnectionCreate(
            name="has title",
            subject=NodeCreate(name="Andrew"),
            target=NodeCreate(name="Chief Engineer")
        )
    )

    assert conn.name == "has title"
    assert conn.subject.name == "Andrew"
    assert conn.target.name == "Chief Engineer"


def test_create_connection_to_existing_nodes(db_session):
    conn_1 = crud.create_connection(
        db_session, ConnectionCreate(
            name="has title",
            subject=NodeCreate(name="Andrew"),
            target=NodeCreate(name="Chief Engineer")
        )
    )

    conn_2 = crud.create_connection(
        db_session, ConnectionCreate(
            name="is a",
            subject=conn_1.subject_id,
            target=conn_1.target_id
        )
    )

    assert conn_2.name == "is a"
    assert conn_2.subject.name == "Andrew"
    assert conn_2.target.name == "Chief Engineer"


def test_create_connection_to_nonexistent_nodes(db_session):
    with pytest.raises(ConnectionNodeNotFoundError) as error:
        conn_2 = crud.create_connection(
            db_session, ConnectionCreate(
                name="bad connection",
                subject=98,
                target=99
            )
        )


def test_delete_connection(db_session_with_nodes_and_connections):
    crud.delete_connection(db_session_with_nodes_and_connections, 1)
    connections = crud.get_connections(db_session_with_nodes_and_connections)
    assert len(connections) == 13


def test_delete_nonexistent_connection(db_session_with_nodes_and_connections):
    crud.delete_connection(db_session_with_nodes_and_connections, 99)
    connections = crud.get_connections(db_session_with_nodes_and_connections)
    assert len(connections) == 14


def test_delete_node_deletes_connections_to_node(db_session_with_nodes_and_connections):
    # find and delete Andrew
    andrew = crud.get_nodes_like_name(db_session_with_nodes_and_connections, "Andrew")[0]
    crud.delete_node(db_session_with_nodes_and_connections, andrew.id)

    # verify only 1 node deleted
    nodes = crud.get_nodes(db_session_with_nodes_and_connections)
    assert len(nodes) == 13

    # verify 5 connections deleted
    connections = crud.get_connections(db_session_with_nodes_and_connections)
    assert len(connections) == 9


def test_get_connections_to_node_id(db_session_with_nodes_and_connections):
    andrew = crud.get_nodes_like_name(db_session_with_nodes_and_connections, "Andrew")[0]

    connections = crud.get_connections_to_node(db_session_with_nodes_and_connections, andrew.id)
    assert len(connections) == 5


def test_get_connections_to_node_name_like(db_session_with_nodes_and_connections):
    assert False


def test_get_connection_by_id(db_session_with_nodes_and_connections):
    andrew = crud.get_connection(db_session_with_nodes_and_connections, 1)
    assert andrew.id == 1


def test_update_connection(db_session_with_nodes_and_connections):
    connection = crud.update_connection(db_session_with_nodes_and_connections, connection_id=1,
                                        updated_connection=ConnectionCreate(name="is a",
                                                                            subject=NodeCreate(name="Ryan Sharpe"),
                                                                            target=NodeCreate(name="Nice Guy")
                                                                            )
                                        )
    assert connection.id == 1
