from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm.exc import DetachedInstanceError

import app.db_handler as db
import app.utils as utils

from ..db_handler import delete_object
from ..dependencies import AdminRequired, SessionDep, UserRequired
from ..models.auction_model import AuctionPublic
from ..models.filter_model import UserFilter
from ..models.user_model import (
    Role,
    SetUserPermission,
    User,
    UserCreate,
    UserMe,
    UserPublic,
    UserUpdate,
)

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
    hashed_password = utils.get_password_hash(user.password)
    del user.password
    db_user = User(**user.model_dump(), password_hash=hashed_password)
    db.add_object(db_user, session)
    return UserPublic.model_validate(db_user)


@router.get("/", dependencies=[UserRequired])
async def read_users(
    session: SessionDep,
    search_term: str | None = None,
    searched_column: UserFilter = UserFilter.USERNAME,
    order_by: UserFilter = UserFilter.USERNAME,
    reverse: bool = False,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
) -> list[UserPublic]:
    """
    ## Retrieve a list of users

    _Requires user authentication._

    ### Parameters

    * `session`: `SessionDep` The database session used for querying.

    * `search_term`: `str` The search term to filter the users by. The searched column is specified by `searched_column`.

    * `searched_column`: `UserFilter` The column to search in. Defaults to `UserFilter.USERNAME`.

    * `order_by`: `UserFilter` The column to order the users by. Defaults to `UserFilter.USERNAME`.

    * `reverse`: `bool` Whether to reverse the order. Defaults to `False`.

    * `offset`: `int` The offset of the first user to retrieve. Defaults to `0`.

    * `limit`: `int` The maximum number of users to retrieve. Defaults to `10`.

    ### Returns

    * `list[UserPublic]`: A list of public user representations:

    ### Raises

    * `HTTPException`: If the query fails.
    """

    users = db.read_objects(
        User,
        session,
        search_term,
        searched_column,
        order_by,
        reverse,
        offset,
        limit,
    )

    return [UserPublic.model_validate(user) for user in users]


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
    # user = session.get(User, user_id)
    user = db.read_object(User, session, user_id)
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
    return UserMe.model_validate(current_user)


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
    # should not happen because is already checked in UserRequired
    if not current_user.id:
        raise HTTPException(status_code=400, detail="User ID not found")

    updated_user = update_user(current_user.id, update_data, session)

    return UserMe.model_validate(updated_user)


@router.get("/me/auctions/")
async def read_user_auctions(
    current_user: Annotated[User, UserRequired],
    session: SessionDep,
) -> list[AuctionPublic]:
    public_auctions: list[AuctionPublic] = []

    # try if user has auctions in database
    try:
        current_user.auctions
    except DetachedInstanceError:
        return public_auctions

    for auction in current_user.auctions:
        if not auction:
            continue
        public_auction = AuctionPublic.model_validate(auction)
        public_auctions.append(public_auction)

    return public_auctions


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

    user_db = db.update_object(user_id, User, update_data, session)
    return user_db  # type: ignore


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

    user_data["updated_at"] = utils.get_current_timestamp()

    user_db.sqlmodel_update(user_data)

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db
