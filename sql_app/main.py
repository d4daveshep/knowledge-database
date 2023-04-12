from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
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


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db_session: Session = Depends(get_db_session)):
    db_user = crud.get_user_by_email(db_session, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db_session=db_session, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
    users = crud.get_users(db_session, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db_session: Session = Depends(get_db_session)):
    db_user = crud.get_user(db_session, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
        user_id: int, item: schemas.ItemCreate, db_session: Session = Depends(get_db_session)
):
    return crud.create_user_item(db_session=db_session, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db_session: Session = Depends(get_db_session)):
    items = crud.get_items(db_session, skip=skip, limit=limit)
    return items
