from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .crud import ConnectionNodeNotFoundError
from .database import LocalSession, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


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
def get_nodes(like: str = "*", skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
    if like == "*":
        nodes = crud.get_nodes(db_session, skip=skip, limit=limit)
    else:
        nodes = crud.get_nodes_like_name(db_session, like=like, skip=skip, limit=limit)

    return nodes


@app.get("/nodes/{node_id}", response_model=schemas.Node)
def get_node(node_id: int, db_session: Session = Depends(get_db_session)):
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
def get_connections(name_like: str = "*", node_id: int = 0, skip: int = 0, limit: int = 100,
                    db_session: Session = Depends(get_db_session)):
    if node_id > 0:
        connections = crud.get_connections_to_node(db_session, node_id)
    else:
        if name_like == "*":
            connections = crud.get_connections(db_session, skip=skip, limit=limit)
        else:
            connections = crud.get_connections_like_name(db_session, like=name_like, skip=skip, limit=limit)
            pass
    return connections


@app.get("/connections/{connection_id}", response_model=schemas.Connection)
def get_connection(connection_id: int, db_session: Session = Depends(get_db_session)):
    db_connection = crud.get_connection(db_session, connection_id=connection_id)
    if db_connection is None:
        raise HTTPException(status_code=404, detail="Connection not found")
    return db_connection


@app.delete("/connections/{connection_id}", status_code=200)
def delete_connection(connection_id: int, response: Response, db_session: Session = Depends(get_db_session)):
    if crud.delete_connection(db_session, connection_id):
        return
    else:
        raise HTTPException(status_code=404)


@app.put("/connections/{connection_id}", status_code=200)
def update_connection(connection_id: int, connection: schemas.ConnectionCreate, response: Response,
                      db_session: Session = Depends(get_db_session)) -> int:
    if crud.get_connection(db_session, connection_id) is None:
        response.status_code = status.HTTP_201_CREATED
    db_connection = crud.update_connection(db_session, connection_id, updated_connection=connection)
    return db_connection.id


@app.get("/stats/", status_code=200)
def get_database_stats(db_session: Session = Depends(get_db_session)):
    stats = {"node_count": crud.get_table_size(db_session, models.Node),
             "connection_count": crud.get_table_size(db_session, models.Connection)}

    return stats


@app.delete("/connections/", status_code=200)
def delete_all_connections(db_session: Session = Depends(get_db_session)):
    num_connections_deleted = crud.delete_connections(db_session)
    return {"message": f"deleted {num_connections_deleted} connections"}


@app.delete("/nodes/", status_code=200)
def delete_all_nodes(db_session: Session = Depends(get_db_session)):
    num_connections_deleted = crud.delete_connections(db_session)
    num_nodes_deleted = crud.delete_nodes(db_session)
    return {"message": f"deleted {num_nodes_deleted} nodes and {num_connections_deleted} connections"}

