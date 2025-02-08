from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, Relationship, SQLModel

from ..utils import get_current_timestamp

# Import Product model only for type checking to avoid circular imports
if TYPE_CHECKING:
    from .auction_model import Auction


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
    updated_at: datetime | None = Field(default=None)

    auctions: Mapped[list["Auction"]] = Relationship(
        sa_relationship=relationship(
            back_populates="owner",
            foreign_keys="[Auction.owner_id]",
        )
    )


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
