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
    return f"deleted, id={node_id}"


@app.post("/connections/", response_model=schemas.Connection)
def create_connection(connection: schemas.ConnectionCreate, db_session: Session = Depends(get_db_session)):
    try:
        db_connection = crud.create_connection(db_session, connection)
    except ConnectionNodeNotFoundError:
        raise HTTPException(status_code=404, detail="Connection node not found")
    return db_connection


@app.get("/connections/", response_model=list[schemas.Connection])
def read_connections(like: str = "*", skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
    if like == "*":
        connections = crud.get_connections(db_session, skip=skip, limit=limit)
    else:
        connections = crud.get_connections_like_name(db_session, like=like, skip=skip, limit=limit)
        pass
    return connections

@app.delete("/connections/{connection_id}")
def delete_connection(connection_id:int, db_session:Session = Depends(get_db_session)):
    crud.delete_connection(db_session, connection_id)
    return f"deleted, id={connection_id}"
