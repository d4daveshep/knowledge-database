import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sql_app import models, crud
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