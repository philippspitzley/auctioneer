from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlmodel import Session, select

from . import db, utils
from .config import ALGORITHM, SECRET_KEY
from .models.user_model import User


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


SessionDep = Annotated[Session, Depends(db.get_session)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# Contrary to the fastapi documentation, I have removed passlib and used bcrypt directly,
# as passlib issues an error message that is not supposed to be security-relevant,
# but this message is issued at every login.
# ErrorMessage: TypeError: argument 'hashed_password': 'str' object cannot be converted to 'PyBytes'
# Solution: https://github.com/pyca/bcrypt/issues/684#issuecomment-1902590553
# Replaced get_password_hash and verify_password with new bcrypt functions


def get_user(session: Session, username: str | None = None) -> User | None:
    if username:
        user = session.exec(select(User).where(User.email == username)).first()
        return user


def authenticate_user(username: str, password: str, session: Session):
    user = get_user(session, username)
    if not user:
        return False
    if not utils.verify_password(password, user.password_hash):
        return False
    return user


def is_admin(
    current_user: Annotated[User, Depends(authenticate_user)],
):
    if current_user.role != "admin":
        return False
    return True


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(session, token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
):
    if not is_admin(user):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
