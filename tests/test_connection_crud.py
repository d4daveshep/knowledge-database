import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from sql_app import models, crud
from sql_app.crud import ConnectionNodeNotFoundError
from sql_app.schemas import NodeCreate, ConnectionCreate, Node, Connection


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

    andrew_chief = ConnectionCreate(subject=andrew, name="has title", target=chief)
    andrew_java = ConnectionCreate(subject=andrew, name="knows", target=java)
    andrew_spring_boot = ConnectionCreate(subject=andrew, name="knows", target=spring_boot)
    andrew_twg = ConnectionCreate(subject=andrew, name="worked on", target=twg)
    andrew_gdt = ConnectionCreate(subject=andrew, name="worked on", target=gdt)

    david_lead = ConnectionCreate(subject=david, name="has title", target=fe_pl)
    david_java = ConnectionCreate(subject=david, name="knows", target=java)
    david_android = ConnectionCreate(subject=david, name="knows", target=android)
    david_westpac = ConnectionCreate(subject=david, name="worked on", target=westpac)

    robin_chief = ConnectionCreate(subject=robin, name="has title", target=chief)
    robin_angular = ConnectionCreate(subject=robin, name="knows", target=angular)
    robin_react = ConnectionCreate(subject=robin, name="knows", target=react)
    robin_cdx = ConnectionCreate(subject=robin, name="worked on", target=cdx)
    robin_gdt = ConnectionCreate(subject=robin, name="worked on", target=gdt)

    assert False  # TODO this stuff doesn't work yet

    db_session.add_all([andrew_chief, andrew_java, andrew_spring_boot, andrew_twg, andrew_gdt,
                        david_lead, david_java, david_android, david_westpac,
                        robin_chief, robin_angular, robin_react, robin_cdx, robin_gdt
                        ])
    db_session.commit()

    yield db_session


def test_fixture(db_session_with_nodes_and_connections):
    select_all_nodes = select(Node)
    nodes = db_session_with_nodes_and_connections.scalars(select_all_nodes).all()
    assert len(nodes) == 14

    select_all_connections = select(Connection)
    connections = db_session_with_nodes_and_connections.scalars(select_all_connections).all()
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


def test_get_connections(db_session):
    connections = crud.get_connections(db_session)
    assert len(connections) == 2
