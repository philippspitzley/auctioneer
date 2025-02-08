from typing import Annotated, Sequence, Type, TypeVar

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, select

import app.utils as utils
from app.utils import get_session

from .models.filter_model import Filter
from .models.user_model import User

# bound all types of subclasses from SQLModel to ModelT, used for generic functions
ModelT = TypeVar("ModelT", bound=SQLModel)

# TODO: add search in all columns at once
# TODO: add table model to replace ModelT


SessionDep = Annotated[Session, Depends(get_session)]


def read_object(
    obj_type: Type[ModelT],
    session: SessionDep,
    obj_id: int | None = None,
    column_name: Filter | None = None,
    search_term: str | None = None,
) -> ModelT:
    if column_name and search_term:
        column = getattr(obj_type, column_name)
        stmt = select(obj_type).where(obj_type[column] == search_term)

        obj = session.exec(stmt).first()

    obj = session.get(obj_type, obj_id)

    if not obj:
        raise HTTPException(
            status_code=404,
            detail=f"{obj_type.__name__} not found",
        )
    return obj


def read_objects(
    obj_type: Type[ModelT],
    session: Session,
    search_term: str | None = None,
    searched_column: Filter | None = None,
    order_by: Filter | None = None,
    reverse: bool = False,
    offset: int = 0,
    limit: int = 100,
) -> Sequence[ModelT]:
    stmt = select(obj_type)

    if search_term and searched_column:
        column = getattr(obj_type, searched_column)
        stmt = stmt.where(column.ilike(f"%{search_term}%"))

    stmt = stmt.offset(offset).limit(limit)

    if order_by is not None:
        order_by = getattr(obj_type, order_by)

        if reverse:
            order_by = order_by.desc()  # type: ignore

        stmt = stmt.order_by(order_by)

    return session.exec(stmt).all()


def add_object(obj: ModelT, session: Session) -> ModelT:
    try:
        session.add(obj)
        session.commit()
        session.refresh(obj)
    except IntegrityError as e:
        session.rollback()

        # extract DETAIL from error:

        # EXAMPLE: (psycopg2.errors.ForeignKeyViolation) insert or update on table "auction" violates foreign key constraint "auction_buyer_id_fkey"
        # DETAIL:  Key (buyer_id)=(0) is not present in table "user".

        # BECOMES: "Key (buyer_id)=(0) is not present in table 'user'."
        error: str = e.args[0].split("DETAIL: ")[-1].strip().replace('"', "'")

        raise HTTPException(
            status_code=400,
            detail=f"ERROR: {error}",
        )

    return obj


def update_object(
    obj_id: int,
    obj_type: Type[ModelT],
    obj_update_data: ModelT,
    session: Session,
) -> ModelT:
    obj_db = read_object(obj_type=obj_type, session=session, obj_id=obj_id)

    obj_data = obj_update_data.model_dump(exclude_unset=True)

    if obj_type == User and "password" in obj_data:
        password: str = obj_data["password"]
        obj_data["password_hash"] = utils.get_password_hash(password)
        del obj_data["password"]

    obj_data["updated_at"] = utils.get_current_timestamp()

    obj_db.sqlmodel_update(obj_data)

    add_object(obj_db, session)

    return obj_db


def delete_object(
    obj_id: int,
    obj_type: Type[ModelT],
    session: Session,
):
    obj = read_object(obj_type=obj_type, session=session, obj_id=obj_id)

    session.delete(obj)
    session.commit()
