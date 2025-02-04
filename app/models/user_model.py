from datetime import datetime
from enum import Enum

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

from ..utils.helper import get_current_timestamp

# TODO: generate UUI


class Role(str, Enum):
    admin = "admin"
    user = "user"


class UserBase(SQLModel):
    username: str = Field(index=True)
    email: EmailStr = Field(index=True, unique=True)


class UserPublic(UserBase):
    id: int | None = Field(default=None, primary_key=True)
    role: Role = Field(default=Role.user)


class User(UserPublic, table=True):
    password_hash: str
    created_at: datetime = Field(default_factory=get_current_timestamp)
    updated_at: datetime = Field(default=None)


class UserMe(UserBase):
    id: int
    role: Role
    created_at: datetime
    updated_at: datetime | None


class UserCreate(UserBase):
    password: str
    role: Role = Role.user


class UserUpdate(UserBase):
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class SetUserPermission(UserBase):
    role: Role
