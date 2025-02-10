from datetime import timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from jinja2 import Environment, FileSystemLoader
from premailer import transform

from ..auth_handler import Token, authenticate_user, create_access_token
from ..config import ACCESS_TOKEN_EXPIRE_MINUTES
from ..dependencies import SessionDep
from ..models.user_model import UserCreate
from . import users
from .email import send_email

# TODO: implement registration
# TODO: implement logout invalidate token
# TODO: implement email verification
# TODO: implement password reset
# TODO: refresh token when in use, reset expire time ,access token and refresh token

env = Environment(
    loader=FileSystemLoader("app/templates")
)  # "templates" is your template directory


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
async def register_user(
    user: UserCreate, session: SessionDep, background_tasks: BackgroundTasks
):
    new_user = await users.create_user(user, session)

    if new_user:
        # Render the email template
        template = env.get_template("registration_email.html")
        login_link = "localhost:8000/Authentication/login_for_access_token_auth_login_post"
        html_content = template.render(user=new_user, login_link=login_link)

        # Transform the HTML content to inline style for email support
        html_content = transform(html_content)

        await send_email(
            to=user.email,
            subject="Registration Confirmation",
            body=html_content,
            background_tasks=background_tasks,
        )

        return {"registered": True}
