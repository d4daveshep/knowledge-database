from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from . import models, schemas


def create_node(db_session: Session, node: schemas.NodeCreate) -> models.Node:
    db_node = models.Node(name=node.name)
    db_session.add(db_node)
    db_session.commit()
    db_session.refresh(db_node)
    return db_node


def get_node(db_session: Session, node_id: int) -> models.Node | None:
    select_stmt = select(models.Node).filter(models.Node.id == node_id)
    return db_session.scalars(select_stmt).first()


def get_node_by_name(db_session: Session, name: str) -> models.Node | None:
    select_stmt = select(models.Node).filter(models.Node.name == name)
    return db_session.scalars(select_stmt).first()


def get_nodes(db_session: Session, skip: int = 0, limit: int = 100) -> list[models.Node]:
    select_stmt = select(models.Node)
    return list(db_session.scalars(select_stmt).all())


def get_nodes_like_name(db_session: Session, like: str, skip: int = 0, limit: int = 100):
    select_stmt = select(models.Node).filter(models.Node.name.ilike(f"%{like}%"))
    return list(db_session.scalars(select_stmt).all())


def update_node(db_session: Session, node_id: int, updated_name: str) -> models.Node | None:
    db_node = get_node(db_session, node_id)
    if db_node is None:
        return None
    update_stmt = update(models.Node).where(models.Node.id == node_id).values(name=updated_name)
    db_session.execute(update_stmt)
    db_session.commit()
    return get_node(db_session, node_id)


def delete_node(db_session: Session, node_id: int) -> None:
    # delete the node
    delete_stmt = delete(models.Node).where(models.Node.id == node_id)
    db_session.execute(delete_stmt)

    # delete any connections to the node
    delete_stmt = delete(models.Connection).where(
        models.Connection.subject_id == node_id)
    db_session.execute(delete_stmt)
    delete_stmt = delete(models.Connection).where(
        models.Connection.target_id == node_id)
    db_session.execute(delete_stmt)

    db_session.commit()


class ConnectionNodeNotFoundError(Exception):
    pass


def get_or_create_connection_node(db_session: Session, node: schemas.NodeCreate | int) -> models.Node:
    if isinstance(node, int):
        db_node = get_node(db_session, node)
        if db_node is None:
            raise ConnectionNodeNotFoundError(f"node_id: {node}")
    else:
        db_node = get_node_by_name(db_session, node.name)
        if not db_node:
            db_node = create_node(db_session, node)

    return db_node


def create_connection(db_session: Session, connection: schemas.ConnectionCreate) -> models.Connection:
    subject_node = get_or_create_connection_node(db_session, connection.subject)
    target_node = get_or_create_connection_node(db_session, connection.target)

    db_connection = models.Connection(name=connection.name, subject=subject_node, target=target_node)
    db_session.add(db_connection)
    db_session.commit()
    db_session.refresh(db_connection)
    return db_connection


def get_connections(db_session: Session, skip: int = 0, limit: int = 100) -> list[models.Connection]:
    select_stmt = select(models.Connection)
    return list(db_session.scalars(select_stmt).all())


def get_connections_like_name(db_session: Session, like: str, skip: int = 0, limit: int = 100) -> list[
    models.Connection]:
    select_stmt = select(models.Connection).filter(models.Connection.name.ilike(f"%{like}%"))
    return list(db_session.scalars(select_stmt).all())


def delete_connection(db_session: Session, connection_id: int) -> None:
    delete_stmt = delete(models.Connection).where(models.Connection.id == connection_id)
    db_session.execute(delete_stmt)
    db_session.commit()


def get_connections_to_node(db_session: Session, node_id: int) -> list[models.Connection]:
    select_stmt = select(models.Connection).filter(models.Connection.subject_id == node_id)
    connections = list(db_session.scalars(select_stmt).all())
    select_stmt = select(models.Connection).filter(models.Connection.target_id == node_id)
    connections.extend(list(db_session.scalars(select_stmt).all()))
    return connections

