from sqlmodel import Session, create_engine

from app.config import DB_URI

engine = create_engine(DB_URI, echo=False)


def get_session():
    with Session(engine) as session:
        yield session
