from typing import Type, TypeVar

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from.models.user_model import User

# bound all types of subclasses from SQLModel to T
T = TypeVar("T", bound=SQLModel)

postgresql_url = "postgresql://philipp@localhost:5432/auctioneer"
engine = create_engine(postgresql_url, echo=False)


def get_user(username: str | None = None) -> User | None:
    with Session(engine) as session:
        user = session.exec(select(User).where(User.email == username)).first()
        return user


def get_session():
    with Session(engine) as session:
        yield session


############################################


def delete_object(obj_id: int, obj_type: Type[T], session: Session):
    obj = session.get(obj_type, obj_id)

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=f"{obj_type.__name__} not found",
        )
    print(obj)
    session.delete(obj)
    session.commit()


def create_object(obj: T, session: Session) -> T:
    session.add(obj)
    session.commit()
    session.refresh(obj)

    return obj
