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
