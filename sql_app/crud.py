from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db_session: Session, user_id: int) -> models.User | None:
    return db_session.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db_session: Session, email: str) -> models.User | None:
    return db_session.query(models.User).filter(models.User.email == email).first()


def get_users(db_session: Session, skip: int = 0, limit: int = 100) -> list[models.User]:
    return db_session.query(models.User).offset(skip).limit(limit).all()


def create_user(db_session: Session, user: schemas.UserCreate) -> models.User:
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)
    return db_user


def get_items(db_session: Session, skip: int = 0, limit: int = 100) -> list[models.Item]:
    return db_session.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db_session: Session, item: schemas.ItemCreate, user_id: int) -> models.Item:
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db_session.add(db_item)
    db_session.commit()
    db_session.refresh(db_item)
    return db_item


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
    delete_stmt = delete(models.Node).where(models.Node.id == node_id)
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
