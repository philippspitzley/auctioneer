from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from ..db_handler import delete_object

from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.user_model import (
    Role,
    SetUserPermission,
    User,
    UserCreate,
    UserMe,
    UserPublic,
    UserUpdate,
)
from ..utils.auth import get_password_hash
from ..utils.helper import get_current_timestamp

router = APIRouter(
    prefix="/users",
    tags=["User"],
)


@router.post("/", dependencies=[AdminRequired])
async def create_user(user: UserCreate, session: SessionDep) -> UserPublic:
    """
    ## Create a new user

    _Requires admin permissions._

    ### Parameters

    * user: `UserCreate` The user representation to create.

    * session: `SessionDep`: The database session used for querying.

    ### Returns

    * `UserPublic`: The public user representation:

    ### Raises

    * `HTTPException`: If the user already exists.
    """
    hashed_password = get_password_hash(user.password)
    del user.password
    db_user = User(**user.model_dump(), password_hash=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    public_user = UserPublic.model_validate(db_user)
    return public_user


@router.get("/", dependencies=[UserRequired])
async def read_users(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10,
) -> list[UserPublic]:
    """
    ## Retrieve a list of users

    _Requires user authentication._

    ### Parameters

    * `session`: `SessionDep` The database session used for querying.

    * `offset`: `int` The offset of the first user to retrieve.

    * `limit`: `int` The maximum number of users to retrieve.

    ### Returns

    * `list[UserPublic]`: A list of public user representations:

    ### Raises

    * `HTTPException`: If the query fails.
    """
    stmt = select(User).offset(offset).limit(limit).order_by(User.username)
    users = session.exec(stmt).all()
    public_users = [UserPublic.model_validate(user) for user in users]

    return public_users


@router.get("/{user_id}", dependencies=[UserRequired])
async def read_user(user_id: int, session: SessionDep) -> UserPublic:
    """
    ## Retrieve a user by ID

    _Requires user authentication._

    ### Parameters

    * `user_id`: `int` The ID of the user to retrieve.

    * `session`: `SessionDep` The database session used for querying.

    ### Returns

    * `UserPublic`: The public user representation:

    ### Raises

    * `HTTPException`: If the user is not found.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    public_user = UserPublic.model_validate(user)
    return public_user


@router.get("/me/")
async def read_user_me(
    current_user: Annotated[User, UserRequired],
) -> UserMe:
    """
    ## Retrieve the current user

    _Requires user authentication._

    ### Returns

    * `UserMe`: The current user representation:

    ### Raises

    * `HTTPException`: If the user is not found.
    """
    me = UserMe.model_validate(current_user)

    return me


@router.patch("/me/")
async def update_user_me(
    current_user: Annotated[User, UserRequired],
    update_data: UserUpdate,
    session: SessionDep,
) -> UserMe:
    """
    ## Update the current user

    _Requires user authentication._

    ### Parameters

    * `current_user`: `User` The current user representation.

    * `update_data`: `UserUpdate` The data to update the user with.

    * `session`: `SessionDep` The database session used for querying.

    ### Returns

    * `UserMe`: The updated user representation:

    ### Raises

    * `HTTPException`: If the user is not found.
    """
    if not current_user.id:
        raise HTTPException(status_code=400, detail="User ID not found")

    updated_user = update_user(current_user.id, update_data, session)

    return UserMe.model_validate(updated_user)


@router.patch("/{user_id}", dependencies=[AdminRequired])
def update_user(
    user_id: int, update_data: UserUpdate, session: SessionDep
) -> User:
    """
    ## Update a user

    _Requires admin permissions._

    ### Parameters

    * `user_id`: `int` The ID of the user to update.

    * `update_data`: `UserUpdate` The data to update the user with.

    * `session`: `SessionDep` The database session used for querying.

    ### Returns

    * `User`: The updated user representation:

    ### Raises

    * `HTTPException`: If the user is not found.
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = update_data.model_dump(exclude_unset=True)

    user_data["updated_at"] = get_current_timestamp()

    if update_data.password:
        hashed_password = get_password_hash(update_data.password)
        user_data["password_hash"] = hashed_password

    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db


@router.delete("/{user_id}", dependencies=[AdminRequired])
def delete_user(user_id: int, session: SessionDep):
    """
    ## Delete a user by ID

    _Requires admin permissions._

    ### Parameters

    * `user_id`: `int` The ID of the user to delete.

    * `session`: `SessionDep` The database session used for querying.

    ### Returns

    * `dict[str, bool]`: A dictionary with a single key-value pair, {"ok": True}.

    ### Raises

    * `HTTPException`: If the user is not found.
    """
    delete_object(user_id, User, session)

    return {"ok": True}


@router.patch("/permission/{user_id}", dependencies=[AdminRequired])
def update_user_permission(user_id: int, role: Role, session: SessionDep):
    """
    ## Update a user's permission

    _Requires admin permissions._

    ### Parameters

    * `user_id`: `int` The ID of the user to update.

    * `role`: `Role` The new role for the user.

    * `session`: `SessionDep` The database session used for querying.

    ### Returns

    * `User`: The updated user representation:

    ### Raises

    * `HTTPException`: If the user is not found.
    """
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = SetUserPermission.model_validate(user_db)
    user_data = update_data.model_dump(exclude_unset=True)
    user_data["role"] = role

    user_data["updated_at"] = get_current_timestamp()

    user_db.sqlmodel_update(user_data)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db
