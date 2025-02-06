from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..dependencies import SessionDep
from ..models.user_model import UserCreate
from ..utils.auth import Token, authenticate_user, create_access_token

# TODO: implement registration
# TODO: implement logout
# TODO: implement email verification
# TODO: implement password reset

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """
    ## Obtain an access token for a user

    This endpoint allows users to obtain an access token by providing valid credentials.

    ### Parameters

    * `form_data`: `OAuth2PasswordRequestForm` The form data containing username and password.

    ### Returns

    * `Token`: The access token and token type for the authenticated user.

    ### Raises

    * `HTTPException`: If the username or password is incorrect.
    """

    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
def register_user(user: UserCreate, session: SessionDep):
    return {"registered": True}
