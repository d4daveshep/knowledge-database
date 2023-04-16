import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sql_app import schemas
from sql_app.main import app, get_db_session
from sql_app.models import Base

os.remove("./test.db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db_session] = override_get_db

client = TestClient(app)


def test_create_node():
    name = "New Starter"
    # node = schemas.NodeCreate(name=name)
    response = client.post(
        "/nodes/",
        json=schemas.NodeCreate(name=name).dict()
    )
    assert response.status_code == 200, response.text
    node = schemas.Node(**response.json())
    assert node.name == name
    assert node.id == 1
