import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from web_apps import models, crud
from web_apps.models import Node
from web_apps.schemas import NodeCreate


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", echo=True)

    models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


@pytest.fixture()
def session_with_3_nodes(db_session):
    andrew = Node(name="Andrew Lindesay")
    david = Node(name="David Rawson")
    robin = Node(name="Robin Southgate")
    db_session.add_all([andrew, david, robin])
    db_session.commit()

    yield db_session


def test_create_node(db_session):
    name = "Chris Callahan"
    node = crud.create_node(db_session, NodeCreate(name=name))
    assert node.name == name
    assert node.id


def test_get_node_by_id(session_with_3_nodes):
    node = crud.get_node(session_with_3_nodes, 2)
    assert node.name == "David Rawson"

    node = crud.get_node(session_with_3_nodes, 99)
    assert not node


def test_get_node_by_name(session_with_3_nodes):
    node = crud.get_node_by_name(session_with_3_nodes, "David Rawson")
    assert node.name == "David Rawson"


def test_get_nodes(session_with_3_nodes):
    nodes = crud.get_nodes(session_with_3_nodes)
    assert len(nodes) == 3


def test_get_node_like_name(session_with_3_nodes):
    nodes = crud.get_nodes_like_name(session_with_3_nodes, like="robin")
    assert len(nodes) == 1
    robin = nodes[0]
    assert robin.name == "Robin Southgate"


def test_update_node(session_with_3_nodes):
    node = crud.update_node(session_with_3_nodes, 1, updated_name="Andy Linde")
    assert node.name == "Andy Linde"


def test_update_nonexistent_node(session_with_3_nodes):
    node = crud.update_node(session_with_3_nodes, 99, updated_name="Andy Linde")
    assert node is None


def test_delete_existing_node(session_with_3_nodes):
    rows_deleted = crud.delete_node(session_with_3_nodes, 2)
    assert rows_deleted == 1
    node = crud.get_node(session_with_3_nodes, 2)
    assert node is None

    nodes = crud.get_nodes(session_with_3_nodes)
    assert len(nodes) == 2


def test_delete_nonexistent_node(session_with_3_nodes):
    rows_deleted = crud.delete_node(session_with_3_nodes, 99)
    assert rows_deleted == 0
    nodes = crud.get_nodes(session_with_3_nodes)
    assert len(nodes) == 3
