from sqlalchemy import select, update, delete, Result, func, table, or_
from sqlalchemy.orm import Session

from . import models, schemas


def create_node(db_session: Session, node: schemas.NodeCreate) -> models.Node:
    existing_node = get_node_by_name(db_session, node.name)
    if existing_node:
        return existing_node
    else:
        # print(f"{node.name}")
        new_node = models.Node(name=node.name)
        db_session.add(new_node)
        db_session.commit()
        db_session.refresh(new_node)
        return new_node


def get_node(db_session: Session, node_id: int) -> models.Node | None:
    select_stmt = select(models.Node).filter(models.Node.id == node_id)
    return db_session.scalars(select_stmt).first()


def get_node_by_name(db_session: Session, name: str) -> models.Node | None:
    # select_stmt = select(models.Node).filter(models.Node.name.contains(name))
    select_stmt = select(models.Node).filter_by(name_insensitive=name)
    return db_session.scalars(select_stmt).first()


def get_nodes(db_session: Session, skip: int = 0, limit: int = 100) -> list[models.Node]:
    select_stmt = select(models.Node)
    return list(db_session.scalars(select_stmt).all())


def get_nodes_like_name(db_session: Session, like: str, skip: int = 0, limit: int = 100) -> list[models.Node]:
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


def delete_node(db_session: Session, node_id: int) -> int:
    # delete the node
    delete_stmt = delete(models.Node).where(models.Node.id == node_id)
    result: Result = db_session.execute(delete_stmt)

    if result.rowcount:
        # delete any connections to the node
        delete_stmt = delete(models.Connection).where(
            models.Connection.subject_id == node_id)
        db_session.execute(delete_stmt)
        delete_stmt = delete(models.Connection).where(
            models.Connection.target_id == node_id)
        db_session.execute(delete_stmt)

    db_session.commit()
    return result.rowcount


class ConnectionNodeNotFoundError(Exception):
    pass


def get_or_create_connection_node(db_session: Session, node: schemas.NodeCreate | int) -> models.Node:
    if isinstance(node, int):
        db_node = get_node(db_session, node)
        if db_node is None:
            raise ConnectionNodeNotFoundError(f"node_id: {node}")
    else:
        # db_node = get_node_by_name(db_session, node.name)
        # if not db_node:
        db_node = create_node(db_session, node)

    return db_node


def get_connection_by_name_target_id_and_subject_id(db_session: Session, name: str, subject_id: int,
                                                    target_id: int) -> models.Connection | None:
    select_stmt = select(models.Connection).filter(models.Connection.name.contains(name),
                                                   # TODO changes this to use comparator
                                                   models.Connection.subject_id == subject_id,
                                                   models.Connection.target_id == target_id)

    return db_session.scalars(select_stmt).first()


def create_connection(db_session: Session, connection: schemas.ConnectionCreate) -> models.Connection:
    subject_node: models.Node = get_or_create_connection_node(db_session, connection.subject)
    target_node: models.Node = get_or_create_connection_node(db_session, connection.target)

    existing_connection = get_connection_by_name_target_id_and_subject_id(
        db_session, name=connection.name, subject_id=subject_node.id, target_id=target_node.id)
    if not existing_connection:
        db_connection = models.Connection(name=connection.name, subject=subject_node, target=target_node)
        db_session.add(db_connection)
        db_session.commit()
        db_session.refresh(db_connection)
        return db_connection
    else:
        return existing_connection


def get_connections(db_session: Session, skip: int = 0, limit: int = 100) -> list[models.Connection]:
    select_stmt = select(models.Connection)
    return list(db_session.scalars(select_stmt).all())


def get_connections_like_name(db_session: Session, like: str, skip: int = 0, limit: int = 100) -> list[
    models.Connection]:
    select_stmt = select(models.Connection).filter(models.Connection.name.ilike(f"%{like}%"))
    return list(db_session.scalars(select_stmt).all())


def delete_connection(db_session: Session, connection_id: int) -> int:
    delete_stmt = delete(models.Connection).where(models.Connection.id == connection_id)
    result: Result = db_session.execute(delete_stmt)
    db_session.commit()
    return result.rowcount


def get_connections_to_node(db_session: Session, node_id: int) -> list[models.Connection]:
    select_stmt = select(models.Connection).filter(
        or_(models.Connection.subject_id == node_id, models.Connection.target_id == node_id))
    connections = list(db_session.scalars(select_stmt).all())
    return connections


def get_connection(db_session: Session, connection_id: int) -> models.Connection | None:
    select_stmt = select(models.Connection).filter(models.Connection.id == connection_id)
    return db_session.scalars(select_stmt).first()


def update_connection(db_session: Session, connection_id: int,
                      updated_connection: schemas.ConnectionCreate) -> models.Connection:
    subject_node = get_or_create_connection_node(db_session, updated_connection.subject)
    target_node = get_or_create_connection_node(db_session, updated_connection.target)

    if get_connection(db_session, connection_id) is None:
        db_connection = models.Connection(id=connection_id, name=updated_connection.name, subject=subject_node,
                                          target=target_node)
        db_session.add(db_connection)
        db_session.commit()
        db_session.refresh(db_connection)
    else:
        update_stmt = update(models.Connection).where(models.Connection.id == connection_id).values(
            name=updated_connection.name, subject_id=subject_node.id, target_id=target_node.id)
        db_session.execute(update_stmt)
        db_session.commit()
        db_connection = get_connection(db_session, connection_id)
    return db_connection


def get_connections_to_node_like_name(db_session: Session, like: str) -> list[models.Connection]:
    nodes_like: list[models.Node] = get_nodes_like_name(db_session, like)
    connections: set[models.Connection] = set()

    for node in nodes_like:
        connections_to_node: list[models.Connection] = get_connections_to_node(db_session, node.id)
        for connection in connections_to_node:
            connections.add(connection)

    return list(connections)


def get_table_size(db_session, table_class: table) -> int:
    length = db_session.scalar(select(func.count()).select_from(table_class))
    return length


def delete_nodes(db_session: Session) -> int:
    delete_stmt = delete(models.Node)
    result: Result = db_session.execute(delete_stmt)
    db_session.commit()
    return result.rowcount


def delete_connections(db_session: Session) -> int:
    delete_stmt = delete(models.Connection)
    result: Result = db_session.execute(delete_stmt)
    db_session.commit()
    return result.rowcount


