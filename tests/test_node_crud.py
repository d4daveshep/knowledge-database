import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

from web_apps import models, crud
from web_apps.models import Node
from web_apps.schemas import NodeCreate


@pytest.fixture()
def db_session(db_populated):
    engine = create_engine("sqlite:///"+db_populated, echo=True)

    base = automap_base()
    base.prepare(autoload_with=engine)

    # engine = create_engine("sqlite://", echo=True)
    # models.Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass

def test_db_session_with_populated_db(db_populated):
    engine = create_engine("sqlite:///"+db_populated, echo=True)

    Base = automap_base()
    Base.prepare(autoload_with=engine)


    with Session(engine) as session:
        david = Node(name="David")
        session.add(david)
        session.commit()


    pass

def test_create_node(db_session):
    name = "Chris"
    node = crud.create_node(db_session, NodeCreate(name=name))
    assert node.name == name
    assert node.id


def test_get_node_by_id(db_session):
    node = crud.get_node(db_session, 2)
    assert node.name == "Brian"

    node = crud.get_node(db_session, 99)
    assert not node


def test_get_node_by_name(db_session):
    node = crud.get_node_by_name(db_session, "Cindy")
    assert node.name == "Cindy"


def test_get_nodes(db_session):
    nodes = crud.get_nodes(db_session)
    assert len(nodes) == 15


def test_get_node_like_name(db_session):
    nodes = crud.get_nodes_like_name(db_session, like="engineer")
    assert len(nodes) == 2
    chief = nodes[0]
    assert chief.name == "Chief Engineer"


def test_update_node(db_session):
    node = crud.update_node(db_session, 1, updated_name="Andy")
    assert node.name == "Andy"


def test_update_nonexistent_node(db_session):
    node = crud.update_node(db_session, 99, updated_name="Bogie Man")
    assert node is None


def test_delete_existing_node(db_session):
    rows_deleted = crud.delete_node(db_session, 2)
    assert rows_deleted == 1
    node = crud.get_node(db_session, 2)
    assert node is None

    nodes = crud.get_nodes(db_session)
    assert len(nodes) == 14


def test_delete_nonexistent_node(db_session):
    rows_deleted = crud.delete_node(db_session, 99)
    assert rows_deleted == 0
    nodes = crud.get_nodes(db_session)
    assert len(nodes) == 15
