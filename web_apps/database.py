from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "sqlite:///./web_apps.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine: Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}, echo=True
)

LocalSession: sessionmaker[Session] = sessionmaker(autocommit=False, autoflush=False, bind=engine)
