from sqlmodel import SQLModel, Session, create_engine

from . import models  # noqa: F401

sqlite_file_name = "app/data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

postgresql_url = "postgresql://philipp@localhost:5432/auctioneer"

connect_args = {"check_same_thread": False} # why is this not working with postgresql
engine = create_engine(postgresql_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
