from sqlmodel import SQLModel, Session, create_engine

# from . import models  # noqa: F401

postgresql_url = "postgresql://philipp@localhost:5432/auctioneer"
engine = create_engine(postgresql_url, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
