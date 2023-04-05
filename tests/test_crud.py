import os

import pytest

from sql_app import crud, models
from sql_app.database import SessionLocal, engine
from sql_app.schemas import UserCreate, ItemCreate


@pytest.fixture()
def db_session():
    models.Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    yield session

    session.close()
    os.remove("./sql_app.db")


def test_create_and_get_user_with_item(db_session):
    user = crud.create_user(db_session, UserCreate(email="dave@dave.com", password="test_pwd"))
    assert user.email == "dave@dave.com"

    item = crud.create_user_item(db_session, ItemCreate(title="Dave", description="First name"), user.id)
    assert item.title == "Dave"
    item = crud.create_user_item(db_session, ItemCreate(title="Shepherd", description="Last name"), user.id)

    user = crud.get_user(db_session, 1)
    assert user.email == "dave@dave.com"
    assert len(user.items) == 2
    item = user.items[0]
    assert item.title == "Dave"
    assert item.description == "First name"
    item = user.items[1]
    assert item.title == "Shepherd"
    assert item.description == "Last name"
