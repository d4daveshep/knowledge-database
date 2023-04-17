from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import ConnectionNodeNotFoundError
from .database import LocalSession, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db_session():
    db_session = LocalSession()
    try:
        yield db_session
    finally:
        db_session.close()


#
# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db_session: Session = Depends(get_db_session)):
#     db_user = crud.get_user_by_email(db_session, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db_session=db_session, user=user)
#
#
# @app.get("/users/", response_model=list[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
#     users = crud.get_users(db_session, skip=skip, limit=limit)
#     return users
#
#
# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db_session: Session = Depends(get_db_session)):
#     db_user = crud.get_user(db_session, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
#
#
# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#         user_id: int, item: schemas.ItemCreate, db_session: Session = Depends(get_db_session)
# ):
#     return crud.create_user_item(db_session=db_session, item=item, user_id=user_id)
#
#
# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
#     items = crud.get_items(db_session, skip=skip, limit=limit)
#     return items
#

@app.post("/nodes/", response_model=schemas.Node)
def create_node(node: schemas.NodeCreate, db_session: Session = Depends(get_db_session)):
    db_node = crud.get_node_by_name(db_session, name=node.name)
    if db_node:
        raise HTTPException(status_code=400, detail="Node already exists")
    return crud.create_node(db_session=db_session, node=node)


@app.get("/nodes/", response_model=list[schemas.Node])
def read_nodes(like: str = "*", skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
    if like == "*":
        nodes = crud.get_nodes(db_session, skip=skip, limit=limit)
    else:
        nodes = crud.get_nodes_like_name(db_session, like=like, skip=skip, limit=limit)

    return nodes


@app.get("/nodes/{node_id}", response_model=schemas.Node)
def read_node(node_id: int, db_session: Session = Depends(get_db_session)):
    db_node = crud.get_node(db_session, node_id=node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return db_node


@app.put("/nodes/{node_id}", response_model=schemas.Node)
def update_node(node_id: int, node: schemas.NodeCreate, db_session: Session = Depends(get_db_session)):
    db_node = crud.update_node(db_session, node_id, updated_name=node.name)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Can't update, Node not found")
    return db_node


@app.delete("/nodes/{node_id}")
def delete_node(node_id: int, db_session: Session = Depends(get_db_session)):
    crud.delete_node(db_session, node_id)
    return "Deleted"


@app.post("/connections/", response_model=schemas.Connection)
def create_connection(connection: schemas.ConnectionCreate, db_session: Session = Depends(get_db_session)):
    try:
        db_connection = crud.create_connection(db_session, connection)
    except ConnectionNodeNotFoundError:
        raise HTTPException(status_code=404, detail="Connection node not found")
    return db_connection
