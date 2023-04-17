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
